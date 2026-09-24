"""AI base interfaces and schemas."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FAQItem(BaseModel):
    question: str
    answer: str


class ArticleOutput(BaseModel):
    """Unified article output schema across all AI providers."""
    title: str = Field(description="Article title in Korean")
    slug_hint: str = Field(description="URL-friendly slug hint")
    excerpt: str = Field(description="Short summary for SEO and preview")
    introduction: str = Field(description="Introduction section")
    basic_info_summary: str = Field(description="Overview of basic factual movie information")
    spoiler_free_synopsis: str = Field(description="Spoiler-free plot outline")
    cast_and_director: str = Field(description="Description of director and main cast")
    viewing_points: List[str] = Field(default_factory=list, description="Key points of interest for viewers")
    recommended_for: List[str] = Field(default_factory=list, description="Target audience recommendations")
    similar_movie_notes: List[str] = Field(default_factory=list, description="Similar movies to explore")
    faq: List[FAQItem] = Field(default_factory=list, description="Frequently asked questions and answers")
    conclusion: str = Field(description="Concluding thoughts")
    seo_title: str = Field(description="SEO optimized title")
    meta_description: str = Field(description="Meta description for search engines")
    tags: List[str] = Field(default_factory=list, description="Relevant category and content tags")
    factual_warnings: List[str] = Field(default_factory=list, description="Notices if any facts could not be verified")


class BaseArticleWriter(ABC):
    """Abstract interface for AI article generation providers."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check API connection and credentials."""
        pass

    @abstractmethod
    async def generate_article(
        self,
        movie_data: Dict[str, Any],
        prompt_version: str = "v1.0"
    ) -> ArticleOutput:
        """Generate structured article using provided factual movie data."""
        pass
