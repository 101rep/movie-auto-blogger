"""Information source demarcation and provenance tracking system.

Enforces clear separation between:
- VERIFIED_FACT: Confirmed by API or authoritative data source.
- USER_EXPERIENCE: Directly provided by user in an interview.
- AI_ANALYSIS: Deduced or structured by AI based on verified facts/experience.
- UNVERIFIED: Unverified assumptions or placeholder data.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Demarcated information source categories."""
    VERIFIED_FACT = "verified_fact"
    USER_EXPERIENCE = "user_experience"
    AI_ANALYSIS = "ai_analysis"
    UNVERIFIED = "unverified"


class ConfidenceLevel(str, Enum):
    """Confidence ratings for factual and experiential assertions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    USER_REPORTED = "user_reported"
    UNVERIFIED = "unverified"


class ProvenanceRecord(BaseModel):
    """Provenance record tracking value, origin, confidence, and derivative basis."""
    value: str = Field(..., description="핵심 주장 또는 데이터 값")
    source_type: SourceType = Field(..., description="출처 유형 (VERIFIED_FACT, USER_EXPERIENCE, AI_ANALYSIS, UNVERIFIED)")
    source_id: Optional[str] = Field(default=None, description="출처 식별자 (예: tmdb_123, interview_02, travel_catalog)")
    confidence: str = Field(default="verified", description="신뢰도 등급 (verified, user_reported, unverified 등)")
    based_on: List[str] = Field(default_factory=list, description="AI_ANALYSIS인 경우 기반이 된 출처 ID 목록")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "confidence": self.confidence,
            "based_on": self.based_on
        }
