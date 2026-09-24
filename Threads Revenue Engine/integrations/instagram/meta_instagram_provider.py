import time
import requests
from typing import Optional, List, Dict, Any
from .base import InstagramProvider
from .schemas import InstagramPublishResult, InstagramInsights, InstagramMediaStatus
from .exceptions import (
    InstagramAuthError,
    InstagramPublishError,
    InstagramRateLimitError,
    InstagramMediaProcessingError
)

class MetaInstagramProvider(InstagramProvider):
    """
    Live Meta Instagram Graph API Provider (v21.0).
    Handles single image and multi-slide carousel publishing, insights, and token checks.
    """
    BASE_URL = "https://graph.facebook.com/v21.0"

    def __init__(self, access_token: Optional[str] = None, business_account_id: Optional[str] = None):
        self.access_token = access_token
        self.business_account_id = business_account_id

    def _require_auth(self):
        if not self.access_token or not self.business_account_id:
            raise InstagramAuthError("Meta Instagram credentials (access_token or business_account_id) are not configured")

    def publish_image(self, image_url: str, caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        self._require_auth()
        target_account = account_id or self.business_account_id

        # 1. Create Media Container
        url = f"{self.BASE_URL}/{target_account}/media"
        params = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token
        }
        res = requests.post(url, data=params, timeout=30)
        if res.status_code != 200:
            err = res.json().get("error", {})
            if "OAuthException" in err.get("type", ""):
                raise InstagramAuthError(err.get("message", "Authentication error"))
            raise InstagramPublishError(f"Failed to create image container: {err.get('message', res.text)}")

        creation_id = res.json().get("id")
        if not creation_id:
            raise InstagramPublishError("No creation_id returned for image")

        # 2. Publish Container
        pub_url = f"{self.BASE_URL}/{target_account}/media_publish"
        pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.access_token}, timeout=30)
        if pub_res.status_code != 200:
            err = pub_res.json().get("error", {})
            raise InstagramPublishError(f"Failed to publish media container: {err.get('message', pub_res.text)}")

        media_id = pub_res.json().get("id")
        return InstagramPublishResult(
            media_id=media_id,
            permalink=f"https://www.instagram.com/p/{media_id}/",
            status="SUCCESS",
            media_type="IMAGE",
            creation_id=creation_id
        )

    def publish_carousel(self, image_urls: List[str], caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        self._require_auth()
        if not image_urls:
            raise InstagramPublishError("At least one image is required for a carousel")
        if len(image_urls) > 10:
            image_urls = image_urls[:10]  # Instagram allows max 10 carousel items

        target_account = account_id or self.business_account_id

        # 1. Create child items
        children_ids = []
        for img in image_urls:
            url = f"{self.BASE_URL}/{target_account}/media"
            params = {
                "image_url": img,
                "is_carousel_item": "true",
                "access_token": self.access_token
            }
            res = requests.post(url, data=params, timeout=30)
            if res.status_code != 200:
                err = res.json().get("error", {})
                raise InstagramPublishError(f"Failed to create carousel child item: {err.get('message', res.text)}")
            child_id = res.json().get("id")
            children_ids.append(child_id)
            time.sleep(0.5)

        # 2. Create carousel parent container
        car_url = f"{self.BASE_URL}/{target_account}/media"
        car_params = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": self.access_token
        }
        car_res = requests.post(car_url, data=car_params, timeout=30)
        if car_res.status_code != 200:
            err = car_res.json().get("error", {})
            raise InstagramPublishError(f"Failed to create carousel container: {err.get('message', car_res.text)}")

        creation_id = car_res.json().get("id")

        # 3. Publish carousel container
        pub_url = f"{self.BASE_URL}/{target_account}/media_publish"
        pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.access_token}, timeout=30)
        if pub_res.status_code != 200:
            err = pub_res.json().get("error", {})
            raise InstagramPublishError(f"Failed to publish carousel: {err.get('message', pub_res.text)}")

        media_id = pub_res.json().get("id")
        return InstagramPublishResult(
            media_id=media_id,
            permalink=f"https://www.instagram.com/p/{media_id}/",
            status="SUCCESS",
            media_type="CAROUSEL",
            creation_id=creation_id
        )

    def get_insights(self, media_id: str) -> InstagramInsights:
        self._require_auth()
        url = f"{self.BASE_URL}/{media_id}/insights"
        params = {
            "metric": "reach,saved,shares,likes,comments",
            "access_token": self.access_token
        }
        res = requests.get(url, params=params, timeout=20)
        if res.status_code != 200:
            return InstagramInsights(media_id=media_id)

        data = res.json().get("data", [])
        metrics = {m.get("name"): m.get("values", [{}])[0].get("value", 0) for m in data}
        return InstagramInsights(
            media_id=media_id,
            reach=metrics.get("reach", 0),
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            saves=metrics.get("saved", 0),
            shares=metrics.get("shares", 0),
            profile_visits=metrics.get("profile_visits", 0)
        )

    def validate_token(self) -> bool:
        if not self.access_token or not self.business_account_id:
            return False
        try:
            url = f"{self.BASE_URL}/{self.business_account_id}"
            res = requests.get(url, params={"access_token": self.access_token}, timeout=10)
            return res.status_code == 200
        except Exception:
            return False
