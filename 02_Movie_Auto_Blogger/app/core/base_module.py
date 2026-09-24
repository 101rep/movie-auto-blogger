"""Abstract base interfaces for Vertical Content Modules."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.verticals import VerticalType, VerticalStatus


class CandidateItem(BaseModel):
    """Normalized content candidate item across all verticals."""
    external_id: str
    vertical: VerticalType
    title: str
    original_title: Optional[str] = None
    summary: Optional[str] = None
    source_attribution: str
    source_url: Optional[str] = None
    score: float = 0.0
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class BaseContentModule(ABC):
    """Contract that every vertical module (Movie, News, Travel, etc.) must fulfill."""

    @property
    @abstractmethod
    def vertical(self) -> VerticalType:
        """Return the vertical enum type."""
        pass

    @property
    @abstractmethod
    def status(self) -> VerticalStatus:
        """Return current implementation/operational status."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify upstream data providers and operational health."""
        pass

    @abstractmethod
    async def collect_candidates(self, db: Session, limit: int = 10) -> List[CandidateItem]:
        """Fetch, normalize, and score candidates for this vertical."""
        pass

    @abstractmethod
    async def enrich_item(self, db: Session, external_id: str) -> Dict[str, Any]:
        """Fetch in-depth metadata required for high-quality article generation."""
        pass

    @abstractmethod
    async def generate_content(self, db: Session, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured article content using AI providers."""
        pass

    @abstractmethod
    def render_html(self, content_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Render responsive, styled HTML article with vertical-specific components."""
        pass

    def extract_metadata(
        self,
        gen_result: Dict[str, Any],
        enriched_data: Dict[str, Any],
        candidate: CandidateItem
    ) -> Dict[str, Any]:
        """Extract standardized publishing metadata (title, excerpt, tags, featured_image_url)."""
        return {
            "title": candidate.title,
            "excerpt": candidate.summary or candidate.title,
            "seo_title": candidate.title,
            "meta_description": candidate.summary or candidate.title,
            "tags": [self.vertical.value if hasattr(self.vertical, "value") else str(self.vertical)],
            "featured_image_url": None,
            "article_json_str": "{}"
        }

    def get_core_entities(self, text: str) -> List[str]:
        """Extract core subject entities from title or text to prevent repetitive coverage."""
        return []

