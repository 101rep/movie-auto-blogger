from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ThreadsPublishRequest(BaseModel):
    text: str
    media_urls: Optional[List[str]] = None
    media_type: str = "TEXT"  # TEXT, IMAGE, VIDEO
    reply_to_id: Optional[str] = None
    idempotency_key: Optional[str] = None

class ThreadsPublishResult(BaseModel):
    post_id: str
    platform_id: str
    creation_id: Optional[str] = None
    permalink: Optional[str] = None
    status: str = "SUCCESS"

class ThreadsPostStatus(BaseModel):
    post_id: str
    text: str
    status: str
    created_at: Optional[str] = None
    parent_id: Optional[str] = None

class ThreadsInsights(BaseModel):
    views: int = 0
    likes: int = 0
    replies: int = 0
    reposts: int = 0
    quotes: int = 0
