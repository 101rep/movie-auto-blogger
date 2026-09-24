from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class InstagramPublishResult(BaseModel):
    media_id: str
    permalink: str = ""
    status: str = "SUCCESS"
    media_type: str = "IMAGE"
    creation_id: Optional[str] = None

class InstagramInsights(BaseModel):
    media_id: str
    reach: int = 0
    likes: int = 0
    comments: int = 0
    saves: int = 0
    shares: int = 0
    profile_visits: int = 0
    followers_growth: int = 0

class InstagramMediaStatus(BaseModel):
    media_id: str
    status: str = "FINISHED"

class InstagramCarouselSlide(BaseModel):
    page: int
    headline: str
    body: str
    image_prompt: str

class InstagramCarouselData(BaseModel):
    title: str
    template: str = "minimal"
    slides: List[InstagramCarouselSlide] = Field(default_factory=list)
    caption: str = ""
    hashtags: List[str] = Field(default_factory=list)
