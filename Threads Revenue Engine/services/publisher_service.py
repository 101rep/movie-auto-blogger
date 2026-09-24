from typing import Optional, List, Dict, Any
from integrations.threads.base import ThreadsProvider
from integrations.threads.mock_provider import MockThreadsProvider
from integrations.threads.meta_threads_provider import MetaThreadsProvider
from integrations.threads.schemas import ThreadsPublishResult, ThreadsPostStatus, ThreadsInsights
from integrations.threads.exceptions import ThreadsException, ThreadsPublishError, ThreadsVerificationError

class PublisherService:
    """
    Publisher Service Layer for Threads.
    Mediates all thread publishing requests through ThreadsProvider.
    Never calls external APIs directly.
    """
    def __init__(self, provider: Optional[ThreadsProvider] = None, access_token: Optional[str] = None, user_id: Optional[str] = None, mode: str = "mock"):
        if provider:
            self.provider = provider
        elif mode == "real" and access_token:
            self.provider = MetaThreadsProvider(access_token=access_token, user_id=user_id)
        else:
            self.provider = MockThreadsProvider()

    def publish_post(self, text: str, media_urls: Optional[List[str]] = None, key: Optional[str] = None) -> ThreadsPublishResult:
        """
        Publishes top-level post and verifies the result.
        """
        result = self.provider.publish_post(text=text, media_urls=media_urls, key=key)
        if not result.post_id:
            raise ThreadsPublishError("Provider did not return a valid post_id")

        # Verification check
        status = self.provider.get_post_status(result.post_id)
        if status.status != "SUCCESS":
            raise ThreadsVerificationError(f"Post {result.post_id} failed verification check")

        return result

    def publish_reply(self, parent_id: str, text: str, key: Optional[str] = None) -> ThreadsPublishResult:
        """
        Publishes a threaded reply to a parent post and verifies.
        """
        if not parent_id:
            raise ThreadsPublishError("parent_id is required to publish a reply")

        result = self.provider.publish_reply(parent_id=parent_id, text=text, key=key)
        if not result.post_id:
            raise ThreadsPublishError("Provider did not return a valid reply post_id")

        # Verification check
        status = self.provider.get_post_status(result.post_id)
        if status.status != "SUCCESS":
            raise ThreadsVerificationError(f"Reply {result.post_id} failed verification check")

        return result

    def get_status(self, post_id: str) -> ThreadsPostStatus:
        return self.provider.get_post_status(post_id)

    def get_metrics(self, post_id: str) -> ThreadsInsights:
        return self.provider.get_insights(post_id)

    def check_health(self) -> bool:
        return self.provider.validate_token()
