"""Universal Content Quality Skill applying common standards across all verticals.

Provides:
- People-first content guidance
- Search Intent verification
- Contextual Anti-cliche suppression
- Information source demarcation (VERIFIED_FACT, USER_EXPERIENCE, AI_ANALYSIS, UNVERIFIED)
- Version metadata tracking
"""
import re
from typing import Any, Dict, List, Optional
from app.core.quality.profile import QualityProfile, QualityProfileRegistry
from app.core.quality.provenance import SourceType, ProvenanceRecord
from app.utils.logging import get_logger

logger = get_logger("content_quality_skill")

CONTENT_QUALITY_VERSION = "1.0"


class ContentQualitySkill:
    """Reusable quality skill for auto-pilot and experience-driven content generation."""

    def __init__(self, profile_name: str = "default", profile: Optional[QualityProfile] = None):
        self.version = CONTENT_QUALITY_VERSION
        self.profile = profile or QualityProfileRegistry.get(profile_name)

    def build_quality_system_instructions(self) -> str:
        """Generate common quality and anti-cliche instructions for AI system prompt."""
        cliche_bullets = "\n".join(f"  - \"{c}\"" for c in self.profile.banned_cliches)
        return f"""
[Universal Content Quality & E-E-A-T Standards (Version {self.version})]:
1. People-First Principle:
   - 검색엔진 조작용 키워드 나열을 엄격히 금지합니다.
   - 실제 독자가 해결하고자 하는 궁금증, 고민, 질문에 직관적이고 솔직하게 먼저 답하십시오.
2. Anti-Cliche & Immediate Hook:
   - 다음과 같은 진부하고 기계적인 AI 상투어구로 글을 시작하지 마십시오:
{cliche_bullets}
   - 본문 서두는 실제 상황, 핵심 관찰, 구체적 질문, 또는 실질적 쟁점으로 자연스럽게 시작하십시오.
3. Information Source Demarcation (정보 출처 엄격 구분):
   - 공식 데이터로 확인된 팩트(VERIFIED_FACT)와 분석/의견(AI_ANALYSIS)을 명확히 구분하여 서술하십시오.
   - 제공되지 않은 정보(UNVERIFIED)를 기정사실인 것처럼 날조하거나 단정 짓지 마십시오.
4. Information Gain (실질적 독창성):
   - 단순 요약 재작성을 넘어, 독자가 다른 곳에서 쉽게 얻지 못하는 실용적인 꿀팁, 주의사항, 체감 정보를 제공하십시오.
"""

    def inspect_text(self, text: str) -> Dict[str, Any]:
        """Inspect generated text for cliches, placeholders, and quality metrics."""
        detected_cliches: List[str] = []
        if self.profile.cliche_control:
            # Check for exact or normalized pattern matches
            normalized_text = re.sub(r'\s+', ' ', text.lower())
            for cliche in self.profile.banned_cliches:
                clean_c = cliche.replace("~", "").strip().lower()
                if clean_c and clean_c in normalized_text:
                    detected_cliches.append(cliche)

        char_count = len(text.strip())
        is_length_ok = char_count >= self.profile.min_body_length

        return {
            "version": self.version,
            "profile": self.profile.name,
            "char_count": char_count,
            "is_length_ok": is_length_ok,
            "detected_cliches": detected_cliches,
            "has_cliche_warning": len(detected_cliches) > 0,
            "passed": is_length_ok and len(detected_cliches) == 0
        }

    def sanitize_cliches(self, text: str) -> str:
        """Contextually clean machine cliches from text without damaging meaning."""
        replacements = [
            (r'^(요즘\s+[^.]+?(가|이|는|은)\s+인기입니다\.?\s*)', ''),
            (r'([^.]+?에\s+대해\s+알아보겠습니다\.?\s*)', ''),
            (r'(많은\s+분들이\s+궁금해합니다\.?\s*)', ''),
            (r'(이번\s+글에서는\s+[^.]+?를\s+살펴보겠습니다\.?\s*)', ''),
            (r'(도움이\s+되셨기를\s+바랍니다\.?\s*)', ''),
            (r'(지금부터\s+함께\s+살펴보시죠\.?\s*)', ''),
        ]
        sanitized = text
        for pattern, repl in replacements:
            sanitized = re.sub(pattern, repl, sanitized, flags=re.MULTILINE | re.IGNORECASE)
        return sanitized.strip()

    @staticmethod
    def create_provenance(
        value: str,
        source_type: SourceType,
        source_id: Optional[str] = None,
        confidence: str = "verified",
        based_on: Optional[List[str]] = None
    ) -> ProvenanceRecord:
        """Helper to create structured ProvenanceRecord."""
        return ProvenanceRecord(
            value=value,
            source_type=source_type,
            source_id=source_id,
            confidence=confidence,
            based_on=based_on or []
        )
