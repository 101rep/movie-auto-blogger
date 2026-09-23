import re
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Content
from domain_types.schemas import ReviewAuditResult
from config import settings
from utils.logger import start_job_log, finish_job_log

CLICHE_KEYWORDS = [
    "결론부터 말하면", "핵심은", "정리하면", "여러분",
    "첫째", "둘째", "셋째", "해본 적 있지?", "인 사람?",
    "궁금하지 않으신가요", "주목해주세요"
]

FORBIDDEN_POLICY_WORDS = [
    "100% 완치", "의학적 효능", "특효약", "절대 부작용 없음",
    "단독 최저가 보증 사기", "무조건 100% 수익"
]

class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)

    def audit_content(self, content_id: int) -> ReviewAuditResult:
        content = self.repo.get_content(content_id)
        if not content:
            raise ValueError(f"Content not found: {content_id}")

        job = start_job_log(self.db, "CONTENT_AUDIT_REVIEW", {"content_id": content_id})

        try:
            body = content.body
            comments = content.comments

            # 1. Quality & Readability Evaluation
            lines = [l.strip() for l in body.split("\n") if l.strip()]
            line_count = len(lines)
            avg_line_len = sum(len(l) for l in lines) / line_count if line_count > 0 else 0

            quality_score = 90
            feedbacks = []

            # Deduct if lines are too long (Threads requires short lines)
            if avg_line_len > 45:
                quality_score -= 10
                feedbacks.append("한 줄의 길이가 다소 깁니다. 모바일 가독성을 위해 더 짧게 끊어주세요.")
            else:
                feedbacks.append("모바일 가독성에 최적화된 문장 길이를 유지하고 있습니다.")

            # Detect cliches
            detected_cliches = [kw for kw in CLICHE_KEYWORDS if kw in body]
            if detected_cliches:
                quality_score -= (len(detected_cliches) * 5)
                feedbacks.append(f"AI 상투어({', '.join(detected_cliches)})가 감지되어 더 자연스러운 일상 어조로 수정이 권장됩니다.")

            # Check Hook Strength
            first_line = lines[0] if lines else ""
            if any(p in first_line for p in ["이유", "비결", "후기", "실수", "비교", "진짜", "버린"]):
                hook_strength = "최상"
                quality_score += 5
            else:
                hook_strength = "보통"

            # 2. Policy Verification
            policy_passed = True
            platform = getattr(content, "affiliate_platform", "COUPANG")
            comments_text = " ".join([c.body for c in comments])

            if platform == "NAVER_SHOPPING":
                has_disclosure = "쇼핑커넥트" in body or "수수료를 제공받습니다" in body
                if not has_disclosure:
                    policy_passed = False
                    feedbacks.append("⚠️ [공정위/네이버 주의] 본문 최상단에 쇼핑커넥트 필수 수수료 고지 문구가 누락되었습니다.")
                if "내돈내산" in body:
                    policy_passed = False
                    feedbacks.append("⚠️ [쇼핑커넥트 영구정지 위험] 제휴 글에 '내돈내산' 표기 적발 시 영구 정지됩니다. '실사용 검증'으로 수정하세요.")
            else:
                has_disclosure = ("수수료" in comments_text or "파트너스 활동" in comments_text or
                                  "수수료" in body or "파트너스" in body)
                if not has_disclosure:
                    policy_passed = False
                    feedbacks.append("⚠️ [정책 주의] 댓글 또는 본문에 공정위 파트너스 수수료 고지 문구가 누락되었습니다.")

            # Check forbidden exaggerations
            for bad_word in FORBIDDEN_POLICY_WORDS:
                if bad_word in body:
                    policy_passed = False
                    feedbacks.append(f"⚠️ [정책 위반] 허위/과장 소지가 있는 표현('{bad_word}')이 포함되어 있습니다.")

            # 3. Duplicate Content Check
            duplicate_score = self.calculate_duplicate_score(content.id, body)
            if duplicate_score >= 0.7:
                feedbacks.append(f"기존 게시물과 유사도({int(duplicate_score * 100)}%)가 높습니다. 차별화된 훅으로 리라이팅하세요.")
                quality_score -= 15

            quality_score = max(50, min(100, quality_score))
            feedback_text = " / ".join(feedbacks)

            # Persist audit results to database
            self.repo.update_content_review(
                content_id=content_id,
                quality_score=quality_score,
                duplicate_score=duplicate_score,
                policy_passed=policy_passed,
                review_feedback=feedback_text
            )

            finish_job_log(self.db, job, "SUCCESS", {
                "quality_score": quality_score,
                "policy_passed": policy_passed,
                "duplicate_score": duplicate_score
            })

            return ReviewAuditResult(
                quality_score=quality_score,
                duplicate_score=duplicate_score,
                policy_passed=policy_passed,
                cliches_detected=detected_cliches,
                feedback=feedback_text,
                readability_level="우수" if quality_score >= 85 else "보통",
                hook_strength=hook_strength
            )

        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def calculate_duplicate_score(self, current_content_id: int, body: str) -> float:
        # Simple Jaccard similarity over word tokens against other contents
        other_contents = self.db.query(Content).filter(Content.id != current_content_id).limit(30).all()
        if not other_contents:
            return 0.0

        current_tokens = set(re.findall(r"\w+", body))
        if not current_tokens:
            return 0.0

        max_sim = 0.0
        for c in other_contents:
            other_tokens = set(re.findall(r"\w+", c.body))
            if not other_tokens:
                continue
            intersection = current_tokens.intersection(other_tokens)
            union = current_tokens.union(other_tokens)
            sim = len(intersection) / len(union) if union else 0.0
            if sim > max_sim:
                max_sim = sim

        return round(max_sim, 3)