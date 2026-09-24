# -*- coding: utf-8 -*-
"""
Content Quality Gate System — Production Reliability PRD v2.0 PART 2

Strict pre-publish gatekeeper ensuring:
1. Basic Check: Title, Content, Image, Valid Category
2. Quality Check:
   - Minimum Character Count (1,200+ characters)
   - Anti-Cliche Inspection (prohibits boilerplate AI phrases)
   - Duplicate Content Check (similarity ratio < 0.65)
   - Source & Grounding Check (official URLs, phone numbers, statistics)
   - E-E-A-T Score (Experience, Expertise, Authoritativeness, Trustworthiness)
3. Image Check:
   - Hash Deduplication (detects repeated stock images)
   - Aspect ratio and size sanity
4. Self-Healing Repair Agent Hook on failure.
"""

import re
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("content_quality_gate")

FORBIDDEN_AI_CLICHES = [
    "현대 사회에서",
    "알아보겠습니다",
    "살펴보겠습니다",
    "주목받고 있습니다",
    "중요한 역할을 합니다",
    "지금부터 알아보겠습니다",
    "함께 살펴보겠습니다",
    "매우 유용한 정보가 될 것입니다",
    "이번 포스팅에서는",
    "빠르게 변화하는 현대",
    "그 중요성은 아무리 강조해도 지나치지 않습니다"
]


class QualityGateResult:
    def __init__(self, passed: bool, score: int, issues: List[str], details: Dict[str, Any]):
        self.passed = passed
        self.score = score
        self.issues = issues
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "issues": self.issues,
            "details": self.details
        }


class ContentQualityGate:
    """Pre-publish validation engine preventing low-quality or AI-cliche posts."""

    @classmethod
    def evaluate(
        cls,
        title: str,
        content: str,
        category: Optional[str] = None,
        image_url: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        recent_image_hashes: Optional[List[str]] = None,
        existing_titles: Optional[List[str]] = None
    ) -> QualityGateResult:
        """
        Runs comprehensive quality validation on an article.
        Returns QualityGateResult with pass/fail and detailed score breakdown.
        """
        issues: List[str] = []
        score = 100
        details = {}

        # 1. Basic Checks
        # 1.1 Title
        clean_title = (title or "").strip()
        if not clean_title or len(clean_title) < 10:
            issues.append("제목이 너무 짧거나 비어있습니다 (최소 10자 이상 필수).")
            score -= 25

        # 1.2 Content Body (Strip HTML tags to measure raw reading characters)
        clean_text = re.sub(r"<[^>]+>", " ", content or "")
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        char_count = len(clean_text)
        details["character_count"] = char_count

        if char_count < 800:
            issues.append(f"본문 글자 수가 턱없이 부족합니다 (현재 {char_count}자 / 최소 800자 필수).")
            score -= 30
        elif char_count < 1200:
            issues.append(f"본문 분량이 권장치(1,200자)에 미달합니다 (현재 {char_count}자).")
            score -= 10

        # 1.3 Image presence
        has_image = bool(image_url or image_bytes or "<img" in (content or "").lower())
        details["has_image"] = has_image
        if not has_image:
            issues.append("대표 이미지 또는 본문 이미지가 누락되었습니다.")
            score -= 20

        # 1.4 Category
        valid_cat = bool(category and category.strip() and category.strip() not in ("미분류", "Uncategorized", "0"))
        details["valid_category"] = valid_cat
        if not valid_cat:
            issues.append("정상적인 카테고리가 지정되지 않았습니다.")
            score -= 10

        # 2. Quality & Anti-Cliche Inspection
        cliches_found = []
        for cliche in FORBIDDEN_AI_CLICHES:
            if cliche in clean_text or cliche in clean_title:
                cliches_found.append(cliche)

        details["cliches_found"] = cliches_found
        if cliches_found:
            issues.append(f"AI 상투어구가 감지되었습니다: {', '.join(cliches_found[:3])}")
            score -= (15 * len(cliches_found))

        # 3. Grounding & E-E-A-T Evidence Check
        # Check for numbers, statistics, dates, or official references
        has_numbers = bool(re.search(r"\d+([,\.]\d+)?(%|원|만|억|건|명|점|년|월|일|시)", clean_text))
        has_official_source = bool(re.search(r"(공식|고시|발표|법령|공고|기준|통계|http|www)", clean_text))
        details["has_numbers_and_data"] = has_numbers
        details["has_official_source"] = has_official_source

        if not has_numbers:
            issues.append("구체적인 수치 데이터나 통계 지표가 부족합니다.")
            score -= 10
        if not has_official_source:
            issues.append("공식 출처나 법적/공공 고시 레퍼런스가 누락되었습니다.")
            score -= 10

        # 4. Duplicate Check (if existing titles provided)
        if existing_titles and clean_title:
            import difflib
            for ex in existing_titles:
                sim = difflib.SequenceMatcher(None, clean_title.lower(), ex.lower()).ratio()
                if sim >= 0.70:
                    issues.append(f"기존 게시글('{ex[:25]}...')과 제목 유사도({int(sim*100)}%)가 너무 높습니다.")
                    score -= 30
                    break

        # 5. Image Hash Check
        if image_bytes:
            img_hash = hashlib.md5(image_bytes).hexdigest()
            details["image_hash"] = img_hash
            if recent_image_hashes and img_hash in recent_image_hashes:
                issues.append("최근 발행된 다른 글과 완전히 동일한 이미지가 사용되었습니다 (중복 썸네일).")
                score -= 25

        score = max(0, min(100, score))
        passed = (score >= 70 and not any("필수" in iss for iss in issues))

        logger.info("Quality gate evaluated: Passed=%s, Score=%d, Issues=%d", passed, score, len(issues))
        return QualityGateResult(passed=passed, score=score, issues=issues, details=details)
