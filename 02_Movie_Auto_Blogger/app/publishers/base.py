"""Base publisher interface."""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PostStatus(str, Enum):
    DRAFT = "draft"
    FUTURE = "future"
    PUBLISH = "publish"


class PublishRequest(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    slug: Optional[str] = None
    status: PostStatus = PostStatus.DRAFT
    scheduled_at: Optional[str] = None
    scheduled_at_local: Optional[str] = None
    featured_media_id: Optional[int] = None
    categories: List[str] = []
    tags: List[str] = []


class PublishResult(BaseModel):
    success: bool
    remote_post_id: Optional[int] = None
    remote_url: Optional[str] = None
    remote_status: Optional[str] = None
    error_message: Optional[str] = None


class BasePublisher(ABC):
    """Abstract publisher interface for WordPress and other CMS targets."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check CMS connectivity and authentication."""
        pass

    @abstractmethod
    async def publish_post(self, request: PublishRequest) -> PublishResult:
        """Create or schedule a post on the CMS."""
        pass

    @abstractmethod
    async def upload_media(
        self,
        file_bytes: bytes,
        filename: str,
        alt_text: str,
        content_type: str = "image/jpeg"
    ) -> Optional[int]:
        """Upload media and return remote media ID."""
        pass
