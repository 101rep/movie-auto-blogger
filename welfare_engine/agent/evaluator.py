"""Evaluator Agent for Welfare Engine V1.0.
Analyzes each policy candidate with a 100-point scoring model:
- Support Scale (25 pts)
- Search Potential (25 pts)
- Audience Size (20 pts)
- Deadline Urgency (15 pts) [D-30, D-14, D-7, D-3]
- Seasonality & Regional Distribution (15 pts) [1월 연말정산, 3월 교육, 5월 근로장려금, 9월 명절]
Determines Priority:
- 90~100: IMMEDIATE (즉시 발행)
- 70~89: SCHEDULED (예약 발행)
- 50~69: WAITING (대기)
- <= 50: HOLD (보류)
"""
import json
import logging
import re
from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional
from welfare_engine.database.models import WelfareContent, ContentStatus, PriorityLevel

logger = logging.getLogger("welfare_engine.evaluator")

HIGH_SEARCH_KEYWORDS = [
    "청년도약계좌", "부모급여", "기초연금", "소상공인", "정책자금",
    "근로장려금", "자녀장려금", "청년월세", "에너지바우처", "첫만남이용권",
    "디딤돌대출", "버팀목전세", "희망리턴패키지", "긴급생계지원"
]

SEASONAL_KEYWORDS = {
    1: ["연말정산", "환급금", "세액공제", "소득공제"],
    2: ["연말정산", "신학기", "입학지원"],
    3: ["신학기", "교육지원", "입학금", "보육료", "학자금"],
    4: ["과학의날", "취업지원", "청년"],
    5: ["근로장려금", "자녀장려금", "종합소득세", "어린이날", "가족지원"],
    6: ["여름철", "풍수해", "재난지원"],
    7: ["여름휴가", "냉방비", "에너지바우처"],
    8: ["청년의날", "2학기", "학자금대출"],
    9: ["명절지원", "추석", "귀성", "소상공인특별자금", "한가위"],
    10: ["독감예방접종", "어르신백신", "소상공인"],
    11: ["동절기", "난방비", "김장지원", "연탄쿠폰"],
    12: ["동절기", "에너지바우처", "희망온돌", "연말마감"]
}


class WelfareEvaluator:
    """Evaluates candidates using multi-factor objective scoring."""

    def __init__(self, target_date: Optional[date] = None):
        self.today = target_date or date.today()

    def calculate_scale_score(self, amount_text: str, title: str) -> int:
        """Evaluate Scale of Support (Max 25 pts)."""
        combined = f"{amount_text} {title}".lower()
        if any(w in combined for w in ["5,000만원", "7,000만원", "1억원", "목돈", "전액지원"]):
            return 25
        if any(w in combined for w in ["100만원", "1200만원", "330만원", "300만원", "240만원", "월 100"]):
            return 22
        if any(w in combined for w in ["월 20만원", "월 34만원", "월 50만원", "수백만원", "200만원"]):
            return 19
        if any(w in combined for w in ["바우처", "할인", "감면", "10만원"]):
            return 15
        return 12

    def calculate_search_score(self, title: str, category: str) -> int:
        """Evaluate Search Potential (Max 25 pts)."""
        score = 15
        for kw in HIGH_SEARCH_KEYWORDS:
            if kw in title:
                score = 25
                break
        if score < 25 and any(w in title or w in category for w in ["지원금", "바우처", "월세", "대출", "연금"]):
            score = 20
        return score

    def calculate_audience_score(self, target: str) -> int:
        """Evaluate Audience Size (Max 20 pts)."""
        if any(w in target for w in ["전 국민", "모든 국민", "전 연령", "모든 가정"]):
            return 20
        if any(w in target for w in ["청년", "어르신", "소상공인", "자영업자", "20~40대"]):
            return 17
        if any(w in target for w in ["저소득", "취약계층", "장애인", "한부모"]):
            return 14
        return 10

    def calculate_urgency_score(self, deadline: str) -> Tuple[int, str]:
        """Evaluate Deadline Urgency (Max 15 pts) [D-3, D-7, D-14, D-30]."""
        if not deadline or "상시" in deadline or "연중" in deadline:
            return 7, "상시접수"

        # Try parsing YYYY-MM-DD
        date_match = re.search(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", deadline)
        if date_match:
            try:
                y, m, d = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                dl_date = date(y, m, d)
                days_left = (dl_date - self.today).days
                if days_left < 0:
                    return 0, "마감종료"
                if days_left <= 3:
                    return 15, f"D-{days_left} (초임박)"
                if days_left <= 7:
                    return 12, f"D-{days_left} (임박)"
                if days_left <= 14:
                    return 9, f"D-{days_left} (마감예정)"
                if days_left <= 30:
                    return 6, f"D-{days_left}"
                return 4, f"D-{days_left}"
            except Exception:
                pass

        if "조기마감" in deadline or "소진 시" in deadline:
            return 11, "예산 소진 시 조기마감"

        return 6, "상시/미정"

    def calculate_seasonality_and_region(self, title: str, region: str) -> Tuple[int, str]:
        """Evaluate Seasonality & Regional Distribution (Max 15 pts)."""
        score = 5
        notes = []

        # 1. Seasonality Algorithm
        curr_month = self.today.month
        season_kws = SEASONAL_KEYWORDS.get(curr_month, [])
        matched_season = [kw for kw in season_kws if kw in title]
        if matched_season:
            score += 7
            notes.append(f"{curr_month}월 시즈널({','.join(matched_season)})")

        # 2. Regional Distribution
        if region in ["전국", "서울", "경기", "부산", "대구"]:
            score += 3
            notes.append(f"주요권역({region})")

        return min(15, score), " & ".join(notes) if notes else "기본"

    def evaluate_content(self, content: WelfareContent) -> Tuple[int, str, Dict[str, Any]]:
        """Run full evaluation on a WelfareContent item."""
        scale_score = self.calculate_scale_score(content.amount or "", content.title)
        search_score = self.calculate_search_score(content.title, content.category or "")
        audience_score = self.calculate_audience_score(content.target or "")
        urgency_score, urgency_note = self.calculate_urgency_score(content.deadline or "")
        season_score, season_note = self.calculate_seasonality_and_region(content.title, content.region or "전국")

        total = scale_score + search_score + audience_score + urgency_score + season_score
        total = min(100, max(0, total))

        if total >= 90:
            level = PriorityLevel.IMMEDIATE.value
            status = ContentStatus.READY.value
        elif total >= 70:
            level = PriorityLevel.SCHEDULED.value
            status = ContentStatus.READY.value
        elif total >= 50:
            level = PriorityLevel.WAITING.value
            status = ContentStatus.WAITING.value
        else:
            level = PriorityLevel.HOLD.value
            status = ContentStatus.HOLD.value

        breakdown = {
            "scale_score": scale_score,
            "search_score": search_score,
            "audience_score": audience_score,
            "urgency_score": urgency_score,
            "urgency_note": urgency_note,
            "season_score": season_score,
            "season_note": season_note,
            "total_score": total,
            "level": level
        }

        return total, level, breakdown

    def evaluate_and_update(self, content: WelfareContent) -> None:
        """Evaluate content and update DB attributes directly."""
        total, level, breakdown = self.evaluate_content(content)
        content.priority_score = total
        content.priority_level = level
        content.score_breakdown = json.dumps(breakdown, ensure_ascii=False)
        content.status = ContentStatus.READY.value if total >= 70 else (
            ContentStatus.WAITING.value if total >= 50 else ContentStatus.HOLD.value
        )
        logger.info(f"Evaluated [{content.id}] '{content.title}': {total} pts ({level})")
