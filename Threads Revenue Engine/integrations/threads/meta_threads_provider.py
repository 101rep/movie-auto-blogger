import time
import requests
from typing import Optional, List, Dict, Any
from .base import ThreadsProvider
from .schemas import ThreadsPublishResult, ThreadsPostStatus, ThreadsInsights
from .exceptions import ThreadsException, ThreadsAuthError, ThreadsRateLimitError, ThreadsPublishError, ThreadsVerificationError

class MetaThreadsProvider(ThreadsProvider):
    """
    Official Meta Threads Graph API v1.0 Client.
    Follows Meta Graph API specification with 2-step media container publishing.
    """
    GRAPH_URL = "https://graph.threads.net/v1.0"

    def __init__(self, access_token: Optional[str] = None, user_id: Optional[str] = None):
        self.access_token = access_token
        self.user_id = user_id

        # Auto-resolve user_id if access_token is present but user_id is not provided
        if self.access_token and not self.user_id:
            try:
                me_res = requests.get(
                    f"{self.GRAPH_URL}/me",
                    params={"fields": "id,username", "access_token": self.access_token},
                    timeout=8
                )
                if me_res.status_code == 200:
                    self.user_id = me_res.json().get("id")
            except Exception:
                pass

    def _ensure_configured(self):
        if not self.access_token or not self.user_id:
            raise ThreadsAuthError("Threads access_token or user_id is not configured")

    def publish_post(self, text: str, media_urls: Optional[List[str]] = None, key: Optional[str] = None) -> ThreadsPublishResult:
        self._ensure_configured()
        try:
            image_url = media_urls[0] if media_urls else None
            media_type = "IMAGE" if image_url else "TEXT"
            payload = {
                "media_type": media_type,
                "text": text,
                "access_token": self.access_token
            }
            if image_url:
                payload["image_url"] = image_url

            # Step 1: Create media container
            create_res = requests.post(
                f"{self.GRAPH_URL}/{self.user_id}/threads",
                data=payload,
                timeout=15
            )
            if create_res.status_code in [401, 403]:
                raise ThreadsAuthError(create_res.text)
            if create_res.status_code == 429:
                raise ThreadsRateLimitError(create_res.text)
            create_res.raise_for_status()

            creation_id = create_res.json().get("id")
            if not creation_id:
                raise ThreadsPublishError("Failed to obtain container creation_id from Meta API")

            # Polling/wait for container processing
            time.sleep(2)

            # Step 2: Publish container
            pub_res = requests.post(
                f"{self.GRAPH_URL}/{self.user_id}/threads_publish",
                data={
                    "creation_id": creation_id,
                    "access_token": self.access_token
                },
                timeout=15
            )
            if pub_res.status_code in [401, 403]:
                raise ThreadsAuthError(pub_res.text)
            if pub_res.status_code == 429:
                raise ThreadsRateLimitError(pub_res.text)
            pub_res.raise_for_status()

            post_id = pub_res.json().get("id")
            if not post_id:
                raise ThreadsPublishError("Failed to obtain post_id from publish step")

            return ThreadsPublishResult(
                post_id=f"th_{post_id}",
                platform_id=str(post_id),
                creation_id=creation_id,
                permalink=f"https://www.threads.net/@user/post/{post_id}"
            )
        except (ThreadsException, requests.exceptions.RequestException) as e:
            if isinstance(e, ThreadsException):
                raise
            raise ThreadsPublishError(f"HTTP error during Threads publish: {e}")

    def publish_reply(self, parent_id: str, text: str, key: Optional[str] = None) -> ThreadsPublishResult:
        self._ensure_configured()
        try:
            clean_parent = parent_id.replace("th_", "").replace("mock_", "").replace("rep_", "")
            payload = {
                "media_type": "TEXT",
                "text": text,
                "reply_to_id": clean_parent,
                "access_token": self.access_token
            }

            # Step 1: Create reply container
            create_res = requests.post(
                f"{self.GRAPH_URL}/{self.user_id}/threads",
                data=payload,
                timeout=15
            )
            if create_res.status_code in [401, 403]:
                raise ThreadsAuthError(create_res.text)
            if create_res.status_code == 429:
                raise ThreadsRateLimitError(create_res.text)
            create_res.raise_for_status()

            creation_id = create_res.json().get("id")
            if not creation_id:
                raise ThreadsPublishError("Failed to obtain reply creation_id")

            time.sleep(2)

            # Step 2: Publish reply container
            pub_res = requests.post(
                f"{self.GRAPH_URL}/{self.user_id}/threads_publish",
                data={
                    "creation_id": creation_id,
                    "access_token": self.access_token
                },
                timeout=15
            )
            if pub_res.status_code in [401, 403]:
                raise ThreadsAuthError(pub_res.text)
            pub_res.raise_for_status()

            reply_id = pub_res.json().get("id")
            return ThreadsPublishResult(
                post_id=f"th_{reply_id}",
                platform_id=str(reply_id),
                creation_id=creation_id
            )
        except (ThreadsException, requests.exceptions.RequestException) as e:
            if isinstance(e, ThreadsException):
                raise
            raise ThreadsPublishError(f"HTTP error during Threads reply: {e}")

    def get_post_status(self, post_id: str) -> ThreadsPostStatus:
        self._ensure_configured()
        clean_id = post_id.replace("th_", "").replace("mock_", "")
        try:
            res = requests.get(
                f"{self.GRAPH_URL}/{clean_id}",
                params={
                    "fields": "id,text,timestamp,media_type",
                    "access_token": self.access_token
                },
                timeout=10
            )
            if res.status_code == 200:
                data = res.json()
                return ThreadsPostStatus(
                    post_id=post_id,
                    text=data.get("text", ""),
                    status="SUCCESS",
                    created_at=data.get("timestamp")
                )
            raise ThreadsVerificationError(f"Failed to verify post status: {res.status_code}")
        except Exception as e:
            raise ThreadsVerificationError(f"Status check error: {e}")

    def get_insights(self, post_id: str) -> ThreadsInsights:
        self._ensure_configured()
        clean_id = post_id.replace("th_", "").replace("mock_", "")
        try:
            res = requests.get(
                f"{self.GRAPH_URL}/{clean_id}/insights",
                params={
                    "metric": "views,likes,replies,reposts,quotes",
                    "access_token": self.access_token
                },
                timeout=10
            )
            if res.status_code == 200:
                items = res.json().get("data", [])
                metrics = {}
                for it in items:
                    metrics[it.get("name")] = it.get("values", [{}])[0].get("value", 0)
                return ThreadsInsights(
                    views=metrics.get("views", 0),
                    likes=metrics.get("likes", 0),
                    replies=metrics.get("replies", 0),
                    reposts=metrics.get("reposts", 0),
                    quotes=metrics.get("quotes", 0)
                )
            return ThreadsInsights()
        except Exception:
            return ThreadsInsights()

    def validate_token(self) -> bool:
        if not self.access_token:
            return False
        try:
            res = requests.get(
                f"{self.GRAPH_URL}/me",
                params={"fields": "id", "access_token": self.access_token},
                timeout=6
            )
            return res.status_code == 200
        except Exception:
            return False

    def refresh_token_if_supported(self) -> Optional[str]:
        """Refreshes Long-Lived Token (extends validity for 60 days)."""
        if not self.access_token:
            return None
        try:
            res = requests.get(
                "https://graph.threads.net/refresh_access_token",
                params={
                    "grant_type": "th_refresh_token",
                    "access_token": self.access_token
                },
                timeout=10
            )
            if res.status_code == 200:
                new_token = res.json().get("access_token")
                if new_token:
                    self.access_token = new_token
                    return new_token
        except Exception:
            pass
        return None
