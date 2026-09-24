from typing import Optional, List, Dict, Any
from integrations.instagram.base import InstagramProvider
from integrations.instagram.mock_provider import MockInstagramProvider
from integrations.instagram.meta_instagram_provider import MetaInstagramProvider
from integrations.instagram.schemas import InstagramPublishResult, InstagramInsights, InstagramCarouselData
from integrations.instagram.exceptions import InstagramException, InstagramPublishError, InstagramAuthError

class InstagramService:
    """
    Instagram Service Layer.
    Mediates all Instagram publishing, carousel structuring, and metric retrieval.
    Never calls external Graph APIs directly.
    """
    def __init__(
        self,
        provider: Optional[InstagramProvider] = None,
        access_token: Optional[str] = None,
        business_account_id: Optional[str] = None,
        mode: str = "mock"
    ):
        if provider:
            self.provider = provider
        elif mode == "real" and access_token and business_account_id:
            self.provider = MetaInstagramProvider(access_token=access_token, business_account_id=business_account_id)
        else:
            self.provider = MockInstagramProvider()

    def publish_image(self, image_url: str, caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        if not image_url:
            raise InstagramPublishError("image_url is required to publish an image post")
        return self.provider.publish_image(image_url=image_url, caption=caption, account_id=account_id)

    def publish_carousel(self, image_urls: List[str], caption: str, account_id: Optional[str] = None) -> InstagramPublishResult:
        if not image_urls:
            raise InstagramPublishError("At least one image URL is required for carousel publishing")
        return self.provider.publish_carousel(image_urls=image_urls, caption=caption, account_id=account_id)

    def publish_cardnews(self, cardnews: InstagramCarouselData, image_urls: Optional[List[str]] = None, account_id: Optional[str] = None) -> InstagramPublishResult:
        """
        Convenience method to publish cardnews data with either provided image URLs
        or simulated slide image URLs.
        """
        urls = image_urls or [f"https://images.unsplash.com/photo-sample-{s.page}.jpg" for s in cardnews.slides]
        caption = cardnews.caption or f"{cardnews.title}\n\n" + " ".join(cardnews.hashtags)
        return self.publish_carousel(image_urls=urls, caption=caption, account_id=account_id)

    def get_metrics(self, media_id: str) -> InstagramInsights:
        return self.provider.get_insights(media_id)

    def check_health(self) -> bool:
        return self.provider.validate_token()
