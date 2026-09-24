import uuid
import hashlib
from typing import Optional, List, Dict, Any
from .base import InstagramProvider
from .schemas import InstagramPublishResult, InstagramInsights, InstagramMediaStatus

class MockInstagramProvider(InstagramProvider):
    """
    Mock Instagram Provider for safe local testing and development.
    Produces deterministic identifiers without external Meta network calls.
    """
    def __init__(self, account_id: Optional[str] = "mock_ig_default"):
        self.default_account_id = account_id

    def publish_image(self, image_url: str, caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        h = hashlib.md5((image_url + caption).encode('utf-8')).hexdigest()[:12]
        media_id = f"mock_ig_img_{h}"
        return InstagramPublishResult(
            media_id=media_id,
            permalink=f"https://www.instagram.com/p/{media_id}/",
            status="SUCCESS",
            media_type="IMAGE"
        )

    def publish_carousel(self, image_urls: List[str], caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        key = "".join(image_urls) + caption
        h = hashlib.md5(key.encode('utf-8')).hexdigest()[:12]
        media_id = f"mock_ig_car_{h}"
        return InstagramPublishResult(
            media_id=media_id,
            permalink=f"https://www.instagram.com/p/{media_id}/",
            status="SUCCESS",
            media_type="CAROUSEL"
        )

    def get_insights(self, media_id: str) -> InstagramInsights:
        seed_val = abs(hash(media_id))
        return InstagramInsights(
            media_id=media_id,
            reach=1500 + (seed_val % 3500),
            likes=120 + (seed_val % 450),
            comments=15 + (seed_val % 60),
            saves=45 + (seed_val % 180),
            shares=20 + (seed_val % 90),
            profile_visits=35 + (seed_val % 110),
            followers_growth=3 + (seed_val % 15)
        )

    def validate_token(self) -> bool:
        return True
