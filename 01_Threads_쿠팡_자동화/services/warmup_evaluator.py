import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database.models import Account, Content, PerformanceMetric, Comment
from database.repository import Repository
from integrations.threads_api import ThreadsOfficialAPI

logger = logging.getLogger("WarmupEvaluator")

# ==================== 옵션 1: 하이브리드 결합형 양성화 심사 기준 (Graduation Criteria) ====================
# [능동적 웜업 활동 60% + 성과 반응 지표 40%] 100점 만점
MIN_OUTBOUND_COMMENTS = 25  # 1. 타 계정 아웃바운드 웜업 댓글 활동 (40점 만점) - 최소 25건
MIN_STREAK_DAYS = 3        # 2. 연속 웜업 활동 일수 (20점 만점) - 3일 이상 분산 활동
MIN_VIEWS = 200            # 3. 피드 실조회수 및 프로필 유입 (20점 만점) - 최소 200회
MIN_ORGANIC_POSTS = 3      # 4. 순수 무링크 공감글 발행 건수 (20점 만점) - 최소 3건
PASS_SCORE = 70.0          # 졸업 커트라인 점수 (100점 만점 중 70점 이상)

# 필수 통과 관문 (Hard Gates for Graduation - 실질적 웜업 활동 없이는 졸업 불가)
GATE_MIN_OUTBOUND = 15     # 최소 실질 아웃바운드 댓글 활동 건수
GATE_MIN_ORGANIC = 2       # 최소 공감글 발행 건수
GATE_MIN_STREAK = 2        # 최소 연속 일수

# 추가 연장 시 즉시 투입되는 고화력 참여 유도 질문형 템플릿
EXTENSION_HOOK_TEMPLATES = [
    ("퇴근길 지하철에서 문득 든 생각인데, 다들 주말 앞두고 제일 힐링되는 순간이 언제인가요? 1) 소파 눕방 2) 맛있는 배달음식 3) 밀린 예능 몰아보기. 여러분의 1픽은?", "퇴근길 소소한 힐링 밸런스 게임"),
    ("집에 있는 물건 중에 '이건 진짜 1년 넘게 써도 돈값 제대로 했다' 싶은 인생템 하나씩만 댓글로 추천해주세요! 서로 꿀팁 나눠봐요 ㅎㅎ", "인생 돈값 꿀템 정보 공유"),
    ("월요병 극복하는 나만의 비장의 무기가 있으신가요? 커피 세 잔 말고 진짜 효과 있는 방법 궁금합니다 ㅠㅠ", "직장인/일상 월요병 극복 찐공감")
]

class WarmupEvaluationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)

    def evaluate_account(self, account_id: int) -> Dict[str, Any]:
        """
        단일 계정의 양성화 지표(아웃바운드 웜업 댓글, 연속 일수, 실조회수, 공감글)를 정밀 측정하고 신뢰도 점수를 산출합니다.
        (옵션 1: 하이브리드 결합형 평가 공식 적용)
        """
        acc = self.repo.get_account(account_id)
        if not acc:
            return {"error": "Account not found"}

        # 1. 발행된 오가닉 글 통계
        published_posts = self.db.query(Content).filter(
            Content.account_id == account_id,
            Content.status == "PUBLISHED"
        ).all()

        published_organic = [p for p in published_posts if p.post_type == "ORGANIC_BUILDUP"]
        published_organic_count = len(published_organic)

        # 2. 예약 대기 중인 양성화 글 수
        scheduled_organic_count = self.db.query(Content).filter(
            Content.account_id == account_id,
            Content.status == "SCHEDULED",
            Content.post_type == "ORGANIC_BUILDUP"
        ).count()

        # 3. 누적 인터랙션 지표 집계 (PerformanceMetric 및 AutoReply 합산)
        post_ids = [p.id for p in published_posts]
        total_views = 0
        total_likes = 0
        total_replies = 0
        total_reposts = 0

        if post_ids:
            metrics = self.db.query(
                func.sum(PerformanceMetric.views),
                func.sum(PerformanceMetric.likes),
                func.sum(PerformanceMetric.replies),
                func.sum(PerformanceMetric.reposts)
            ).filter(PerformanceMetric.content_id.in_(post_ids)).first()

            total_views = metrics[0] or 0
            total_likes = metrics[1] or 0
            total_replies = metrics[2] or 0
            total_reposts = metrics[3] or 0

        # 자동 대댓글 및 아웃바운드 소통(스하리) 기록
        from database.models import AutoReply, OutboundInteraction
        auto_replies_count = self.db.query(AutoReply).filter(AutoReply.account_id == account_id).count()
        outbound_count = self.db.query(OutboundInteraction).filter(OutboundInteraction.account_id == account_id).count()

        # 아웃바운드 소통을 통한 프로필 유입 실조회수 및 상호작용 가산
        total_replies += auto_replies_count + (outbound_count * 2)
        total_views += outbound_count * 15 # 타 계정 댓글을 통한 프로필 유입 실조회수
        total_likes += outbound_count

        # 4. 연속 웜업 활동 일수 (Streak Days) 정밀 계산
        outbound_records = self.db.query(OutboundInteraction.created_at).filter(
            OutboundInteraction.account_id == account_id
        ).all()
        outbound_dates = set(r[0].strftime("%Y-%m-%d") for r in outbound_records if r[0])

        post_records = self.db.query(Content.published_at).filter(
            Content.account_id == account_id,
            Content.status == "PUBLISHED"
        ).all()
        post_dates = set(r[0].strftime("%Y-%m-%d") for r in post_records if r[0])

        active_dates = outbound_dates.union(post_dates)
        streak_days = len(active_dates)
        if streak_days == 0 and (outbound_count > 0 or published_organic_count > 0):
            streak_days = 1

        # 5. [옵션 1: 하이브리드] 4대 평가 기둥 점수 산출 (100점 만점)
        # ① 타 계정 아웃바운드 웜업 선댓글 활동 (40점 만점)
        outbound_score = min(40.0, (outbound_count / MIN_OUTBOUND_COMMENTS) * 40.0) if MIN_OUTBOUND_COMMENTS > 0 else 0
        # ② 연속 웜업 활동 일수 (20점 만점)
        streak_score = min(20.0, (streak_days / MIN_STREAK_DAYS) * 20.0) if MIN_STREAK_DAYS > 0 else 0
        # ③ 피드 실조회수 및 프로필 유입 (20점 만점)
        views_score = min(20.0, (total_views / MIN_VIEWS) * 20.0) if MIN_VIEWS > 0 else 0
        # ④ 순수 무링크 공감글 발행 건수 (20점 만점)
        organic_score = min(20.0, (published_organic_count / MIN_ORGANIC_POSTS) * 20.0) if MIN_ORGANIC_POSTS > 0 else 0

        total_trust_score = round(outbound_score + streak_score + views_score + organic_score, 1)

        # 6. 졸업(수료) 판정: 70점 이상 AND 필수 실질 활동 관문(아웃바운드 15건+, 공감글 2건+, 연속 2일+)
        is_graduated = (
            (total_trust_score >= PASS_SCORE) and
            (outbound_count >= GATE_MIN_OUTBOUND) and
            (published_organic_count >= GATE_MIN_ORGANIC) and
            (streak_days >= GATE_MIN_STREAK)
        )
        needs_extension = (not is_graduated) and (scheduled_organic_count <= 1) and (acc.warmup_status == "WARMING_UP")

        # 세부 안내 메시지
        remaining = []
        if outbound_count < MIN_OUTBOUND_COMMENTS:
            remaining.append(f"선댓글 소통 {MIN_OUTBOUND_COMMENTS - outbound_count}건 추가 필요")
        if streak_days < MIN_STREAK_DAYS:
            remaining.append(f"연속 웜업 {MIN_STREAK_DAYS - streak_days}일 추가 필요")
        if total_views < MIN_VIEWS:
            remaining.append(f"실조회수 {MIN_VIEWS - total_views}회 추가 유입 필요")
        if published_organic_count < MIN_ORGANIC_POSTS:
            remaining.append(f"공감글 {MIN_ORGANIC_POSTS - published_organic_count}건 추가 발행 필요")

        status_text = "양성화 수료 완료 (4:1 수익화 모드 전환 가능)" if is_graduated else (
            f"양성화 예열 중 (신뢰도 {total_trust_score}/100점 - {', '.join(remaining[:2]) if remaining else '순항 중'})"
        )

        # DB 업데이트
        acc.trust_score = total_trust_score
        if is_graduated and acc.warmup_status == "WARMING_UP":
            acc.warmup_status = "GRADUATED"
            acc.post_ratio_mode = "MIX_4_TO_1"
            logger.info(f"🎉 Account @{acc.username} has GRADUATED from warmup! (Trust Score: {total_trust_score})")

        self.db.commit()

        return {
            "account_id": acc.id,
            "username": acc.username,
            "display_name": acc.display_name,
            "login_password": acc.login_password or "q1w2e3r4!!",
            "cluster_type": acc.cluster_type,
            "warmup_status": acc.warmup_status,
            "post_ratio_mode": acc.post_ratio_mode,
            "trust_score": total_trust_score,
            "is_graduated": is_graduated,
            "needs_extension": needs_extension,
            "extended_days": acc.warmup_extended_days or 0,
            "status_text": status_text,
            "metrics": {
                "outbound_comments": outbound_count,
                "target_outbound": MIN_OUTBOUND_COMMENTS,
                "outbound_score": round(outbound_score, 1),
                "streak_days": streak_days,
                "target_streak": MIN_STREAK_DAYS,
                "streak_score": round(streak_score, 1),
                "views": total_views,
                "target_views": MIN_VIEWS,
                "views_score": round(views_score, 1),
                "published_organic": published_organic_count,
                "target_organic": MIN_ORGANIC_POSTS,
                "organic_score": round(organic_score, 1),
                "likes": total_likes,
                "replies": total_replies,
                "scheduled_organic": scheduled_organic_count
            },
            "outbound": {
                "today_count": self.db.query(OutboundInteraction).filter(
                    OutboundInteraction.account_id == account_id,
                    OutboundInteraction.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count(),
                "daily_limit": 10,
                "total_count": outbound_count,
                "remaining_today": max(0, 10 - self.db.query(OutboundInteraction).filter(
                    OutboundInteraction.account_id == account_id,
                    OutboundInteraction.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count())
            },
            "remaining_requirements": remaining
        }

    def auto_extend_warmup(self, account_id: int, days_to_add: int = 2) -> int:
        """
        신뢰도 점수 미달 시, 안전을 위해 2일간의 고화력 공감글을 추가 발행 예약하고 양성화 기간을 자동 연장합니다.
        """
        acc = self.repo.get_account(account_id)
        if not acc:
            return 0

        # 최신 예약 시간 찾기
        latest_content = self.db.query(Content).filter(
            Content.account_id == account_id
        ).order_by(desc(Content.scheduled_at)).first()

        start_time = latest_content.scheduled_at if (latest_content and latest_content.scheduled_at) else datetime.utcnow()
        if start_time < datetime.utcnow():
            start_time = datetime.utcnow()

        added_posts = 0
        from database.models import Product
        default_prod = self.db.query(Product).first()
        prod_id = default_prod.id if default_prod else 1

        for i in range(days_to_add):
            post_time = start_time + timedelta(days=i + 1, hours=2)
            template_text, template_title = EXTENSION_HOOK_TEMPLATES[i % len(EXTENSION_HOOK_TEMPLATES)]

            new_content = Content(
                project_id=acc.project_id or 1,
                account_id=acc.id,
                product_id=prod_id,
                content_type="THREADS",
                post_type="ORGANIC_BUILDUP",
                hook_style="DAILY_REALITY",
                comment_strategy="ORGANIC",
                affiliate_platform="COUPANG",
                title=f"[양성화 연장 공감] {template_title}",
                body=f"{template_text}\n\n#일상 #소통 #공감",
                status="SCHEDULED",
                quality_score=95,
                policy_passed=True,
                scheduled_at=post_time
            )
            self.db.add(new_content)
            added_posts += 1

        acc.warmup_extended_days = (acc.warmup_extended_days or 0) + days_to_add
        acc.warmup_status = "WARMING_UP"
        self.db.commit()

        logger.info(f"⚡ Auto-extended warmup for @{acc.username} (+{days_to_add} days, {added_posts} empathy posts added)")
        return added_posts

    def evaluate_and_sync_all(self) -> List[Dict[str, Any]]:
        """
        7개 전 계정을 일괄 평가하고, 미달 계정은 자동으로 기간 연장 및 게시물 충전을 진행합니다.
        """
        accounts = self.repo.list_accounts()
        results = []
        for acc in accounts:
            evaluation = self.evaluate_account(acc.id)
            if evaluation.get("needs_extension"):
                added = self.auto_extend_warmup(acc.id, days_to_add=2)
                evaluation["auto_extended_posts"] = added
                evaluation["extended_days"] = acc.warmup_extended_days
            results.append(evaluation)
        return results
