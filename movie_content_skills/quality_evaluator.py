# -*- coding: utf-8 -*-
"""
EnterPick24 100-Point Quality Score Engine (V4).
Scores content across 8 rigorous dimensions according to PART 30 specifications.
"""

import re
from typing import Dict, Any, List, Optional
from movie_content_skills.duplicate_engine import DuplicateCheckResult


class QualityScoreResult:
    """Encapsulates 100-point quality score breakdown and verdict."""

    def __init__(
        self,
        total_score: int,
        status: str,  # "AUTO_PUBLISH_ELIGIBLE", "REVIEW_REQUIRED", "BLOCK"
        breakdown: Dict[str, int],
        feedback: List[str],
        duplicate_risk: str
    ):
        self.total_score = total_score
        self.status = status
        self.breakdown = breakdown
        self.feedback = feedback
        self.duplicate_risk = duplicate_risk

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": self.total_score,
            "status": self.status,
            "breakdown": self.breakdown,
            "feedback": self.feedback,
            "duplicate_risk": self.duplicate_risk
        }


class V4QualityEvaluator:
    """Evaluates content quality against 8 official V4 dimensions."""

    def evaluate(
        self,
        title: str,
        content_html: str,
        dup_result: DuplicateCheckResult,
        ott_verified: bool = True,
        has_posters: bool = True
    ) -> QualityScoreResult:
        """
        Calculates 100-point score:
        1. 사실 정확성 (20점)
        2. 중복 안전성 (20점)
        3. 검색 의도 (15점)
        4. 콘텐츠 독창성 (15점)
        5. 한국어 현지화 (10점)
        6. OTT 검증 (10점)
        7. 모바일 UX (5점)
        8. 이미지 품질 (5점)
        """
        breakdown = {}
        feedback = []

        # 1. 사실 정확성 (20점): 연도, 분, 점수, 회차 등 단위 정합성
        unit_markers = ["년", "분", "점", "원", "회", "시즌"]
        units_found = sum(1 for u in unit_markers if u in content_html)
        factual_score = min(20, 10 + (units_found * 2))
        breakdown["factual_accuracy"] = factual_score

        # 2. 중복 안전성 (20점): 중복 리스크 기반
        if dup_result.risk_level == "LOW":
            dup_score = 20
        elif dup_result.risk_level == "MEDIUM":
            dup_score = 12
            feedback.append(f"중복 주의: {dup_result.block_reason or '중간 수준의 유사도'}")
        else:
            dup_score = 0
            feedback.append(f"중복 차단: {dup_result.block_reason}")
        breakdown["duplicate_safety"] = dup_score

        # 3. 검색 의도 (15점): 주요 제목 키워드 및 섹션 구성
        intent_markers = ["추천", "리뷰", "줄거리", "평점", "비교", "시청", "어디서", "보는 곳", "가이드"]
        intent_count = sum(1 for m in intent_markers if m in title or m in content_html)
        intent_score = 15 if intent_count >= 3 else 10
        breakdown["search_intent"] = intent_score

        # 4. 콘텐츠 독창성 (15점): Anti-Cliche 및 본문 길이
        cliches = ["현대 사회에서", "알아보겠습니다", "살펴보겠습니다", "중요한 역할을 합니다", "매우 흥미롭습니다"]
        cliche_hits = sum(1 for c in cliches if c in content_html)
        text_len = len(re.sub(r"<[^>]+>", "", content_html))
        
        orig_score = 15
        if cliche_hits > 0:
            orig_score -= (cliche_hits * 3)
            feedback.append(f"AI 상투어구 {cliche_hits}건 검출")
        if text_len < 1200:
            orig_score -= 5
            feedback.append(f"본문 길이 다소 짧음 ({text_len}자)")
        orig_score = max(0, min(15, orig_score))
        breakdown["content_originality"] = orig_score

        # 5. 한국어 현지화 (10점): 영문 과다 노출 방지 및 공식 한국어 명칭
        raw_english_patterns = ["Runtime:", "Genre:", "Cast:", "Director:", "Rating:"]
        raw_eng_found = sum(1 for p in raw_english_patterns if p in content_html)
        korean_score = 10 if raw_eng_found == 0 else max(0, 10 - (raw_eng_found * 2))
        if raw_eng_found > 0:
            feedback.append(f"UI 내 불필요한 영문 메타데이터 라벨 {raw_eng_found}건 발견")
        breakdown["korean_localization"] = korean_score

        # 6. OTT 검증 (10점): 검증일자 명시 및 시청 여부
        if ott_verified and ("OTT 정보 확인" in content_html or "검증일자" in content_html or "2026년" in content_html):
            ott_score = 10
        elif ott_verified:
            ott_score = 7
        else:
            ott_score = 0
            feedback.append("OTT 스트리밍 제공 여부 미검증")
        breakdown["ott_verification"] = ott_score

        # 7. 모바일 UX (5점): 반응형 테이블 컨테이너 및 카드 구조
        mobile_score = 5 if ("overflow-x" in content_html and "ep-card" in content_html) else 3
        breakdown["mobile_ux"] = mobile_score

        # 8. 이미지 품질 (5점): 포스터 컨테이너 및 한국어 ALT 속성
        has_alt = "alt=" in content_html and "포스터" in content_html
        img_score = 5 if (has_posters and has_alt) else 2
        breakdown["image_quality"] = img_score

        # Total Calculation
        total = sum(breakdown.values())

        # Determine Status
        if dup_result.risk_level == "HIGH":
            status = "BLOCK"
            feedback.append("중복 리스크 HIGH 등급으로 자동 발행 영구 금지")
        elif total >= 85:
            status = "AUTO_PUBLISH_ELIGIBLE"
        elif total >= 70:
            status = "REVIEW_REQUIRED"
        else:
            status = "BLOCK"

        return QualityScoreResult(
            total_score=total,
            status=status,
            breakdown=breakdown,
            feedback=feedback,
            duplicate_risk=dup_result.risk_level
        )
