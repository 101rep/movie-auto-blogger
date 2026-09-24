import hashlib
from typing import Optional, List, Dict, Any
from .base import ThreadsProvider
from .schemas import ThreadsPublishResult, ThreadsPostStatus, ThreadsInsights
from .exceptions import ThreadsPublishError

class MockThreadsProvider(ThreadsProvider):
    """
    Idempotent mock provider for local development, offline E2E, and automated testing.
    """
    def __init__(self, session_factory=None):
        self.session_factory = session_factory
        self.published: Dict[str, Dict[str, Any]] = {}
        self.idempotency_store: Dict[str, str] = {}

    def publish_post(self, text: str, media_urls: Optional[List[str]] = None, key: Optional[str] = None) -> ThreadsPublishResult:
        if key and key in self.idempotency_store:
            post_id = self.idempotency_store[key]
            existing = self.published[post_id]
            if existing["text"] != text:
                raise ThreadsPublishError("Idempotency key collision with different content")
            return ThreadsPublishResult(
                post_id=post_id,
                platform_id=post_id.replace("mock_", ""),
                permalink=f"https://www.threads.net/@user/post/{post_id}"
            )

        post_id = f"mock_{hashlib.sha256((key or text).encode()).hexdigest()[:12]}"
        self.published[post_id] = {
            "id": post_id,
            "text": text,
            "media_urls": media_urls or [],
            "parent_id": None,
            "status": "SUCCESS"
        }
        if key:
            self.idempotency_store[key] = post_id

        return ThreadsPublishResult(
            post_id=post_id,
            platform_id=post_id.replace("mock_", ""),
            permalink=f"https://www.threads.net/@user/post/{post_id}"
        )

    def publish_reply(self, parent_id: str, text: str, key: Optional[str] = None) -> ThreadsPublishResult:
        if key and key in self.idempotency_store:
            reply_id = self.idempotency_store[key]
            return ThreadsPublishResult(
                post_id=reply_id,
                platform_id=reply_id.replace("mock_", "")
            )

        reply_id = f"mock_rep_{hashlib.sha256((key or text).encode()).hexdigest()[:12]}"
        self.published[reply_id] = {
            "id": reply_id,
            "text": text,
            "parent_id": parent_id,
            "status": "SUCCESS"
        }
        if key:
            self.idempotency_store[key] = reply_id

        return ThreadsPublishResult(
            post_id=reply_id,
            platform_id=reply_id.replace("mock_", "")
        )

    def get_post_status(self, post_id: str) -> ThreadsPostStatus:
        item = self.published.get(post_id, {
            "id": post_id,
            "text": "mock verified content",
            "parent_id": None,
            "status": "SUCCESS"
        })
        return ThreadsPostStatus(
            post_id=item["id"],
            text=item.get("text", ""),
            status=item.get("status", "SUCCESS"),
            parent_id=item.get("parent_id")
        )

    def get_insights(self, post_id: str) -> ThreadsInsights:
        return ThreadsInsights(views=1250, likes=42, replies=7, reposts=3, quotes=1)

    def validate_token(self) -> bool:
        return True
