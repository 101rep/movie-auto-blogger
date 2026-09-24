from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .schemas import InstagramPublishResult, InstagramInsights, InstagramMediaStatus

class InstagramProvider(ABC):
    """Abstract base provider for Meta Instagram Graph API operations."""

    @abstractmethod
    def publish_image(self, image_url: str, caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        """Publishes a single image post to Instagram."""
        pass

    @abstractmethod
    def publish_carousel(self, image_urls: List[str], caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        """Publishes a multi-slide carousel post to Instagram."""
        pass

    @abstractmethod
    def get_insights(self, media_id: str) -> InstagramInsights:
        """Fetches post engagement and reach metrics."""
        pass

    @abstractmethod
    def validate_token(self) -> bool:
        """Validates current access token against Meta Graph API."""
        pass
