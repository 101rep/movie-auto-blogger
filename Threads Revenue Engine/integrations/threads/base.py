from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .schemas import ThreadsPublishResult, ThreadsPostStatus, ThreadsInsights

class ThreadsProvider(ABC):
    """Abstract base provider for Meta Threads."""

    @abstractmethod
    def publish_post(self, text: str, media_urls: Optional[List[str]] = None, key: Optional[str] = None) -> ThreadsPublishResult:
        """Publish a top-level thread (TEXT, IMAGE, or VIDEO)."""
        pass

    @abstractmethod
    def publish_reply(self, parent_id: str, text: str, key: Optional[str] = None) -> ThreadsPublishResult:
        """Publish a reply to an existing thread."""
        pass

    @abstractmethod
    def get_post_status(self, post_id: str) -> ThreadsPostStatus:
        """Fetch remote post status and verification details."""
        pass

    @abstractmethod
    def get_insights(self, post_id: str) -> ThreadsInsights:
        """Fetch engagement metrics for a post."""
        pass

    @abstractmethod
    def validate_token(self) -> bool:
        """Verify token validity."""
        pass

    # Compatibility methods with existing services.contracts.ThreadsProvider
    def publish_text(self, text: str, key: str) -> str:
        res = self.publish_post(text=text, media_urls=None, key=key)
        return res.post_id

    def publish_image(self, text: str, image_url: str, key: str) -> str:
        res = self.publish_post(text=text, media_urls=[image_url], key=key)
        return res.post_id

    def get_post(self, remote_id: str) -> dict:
        status = self.get_post_status(remote_id)
        return {
            "id": status.post_id,
            "text": status.text,
            "status": status.status,
            "parent_id": status.parent_id
        }

    def refresh_token_if_supported(self) -> Optional[str]:
        return None
