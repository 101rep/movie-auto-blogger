from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ProductItem(BaseModel):
    product_id: str
    name: str
    category: str = "일반"
    original_url: str
    affiliate_url: str
    price: int = 0
    original_price: Optional[int] = None
    image_url: Optional[str] = None
    rating: float = 4.5
    review_count: int = 0
    shipping_type: str = "일반배송"  # 로켓배송 / 일반배송
    description: Optional[str] = None
    source: str = "coupang"
    score: float = 0.0

class DeeplinkResult(BaseModel):
    original_url: str
    shorten_url: str

class AffiliateReport(BaseModel):
    clicks: int = 0
    orders: int = 0
    commission: int = 0
    date: Optional[str] = None
