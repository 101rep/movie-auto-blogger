from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# ==================== Product Schemas ====================
class ProductDTO(BaseModel):
    id: Optional[int] = None
    external_id: str
    name: str
    url: str
    image_url: Optional[str] = ""
    category: str
    price: int
    original_price: Optional[int] = None
    rating: float = 0.0
    review_count: int = 0
    shipping_type: str = "로켓배송"
    description: Optional[str] = ""
    source: str = "coupang"
    raw_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductSaveRequest(BaseModel):
    external_id: str
    name: str
    url: str
    image_url: Optional[str] = ""
    category: str
    price: int
    original_price: Optional[int] = None
    rating: float = 0.0
    review_count: int = 0
    shipping_type: str = "로켓배송"
    description: Optional[str] = ""
    source: str = "coupang"
    raw_data: Optional[Dict[str, Any]] = None

class ProductFilterParams(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_rating: Optional[float] = None
    min_reviews: Optional[int] = None
    sort_by: Optional[str] = "popular"

# ==================== Product Score Schemas ====================
class ProductScoreWeights(BaseModel):
    price: int = 20
    review: int = 20
    purchase: int = 20
    content: int = 15
    problem: int = 15
    seasonality: int = 10

class ProductScoreResult(BaseModel):
    price_score: int
    review_score: int
    rating_score: int
    shipping_score: int
    conversion_score: int
    content_score: int
    seasonality_score: int
    total_score: int
    reason: str

class ProductScoreDTO(ProductScoreResult):
    id: Optional[int] = None
    product_id: int
    created_at: Optional[datetime] = None

class ProductDNAResult(BaseModel):
    target_person: Union[str, List[str]]
    problem: Union[str, List[str]]
    use_case: Union[str, List[str]]
    purchase_reason: Union[str, List[str]]
    purchase_barrier: Union[str, List[str]]
    benefit: Union[str, List[str]]
    keywords: List[str]
    content_angles: List[str]
    evidence: Union[str, List[str]]
    ai_summary: Union[str, List[str]]

    @field_validator("target_person", "problem", "use_case", "purchase_reason", "purchase_barrier", "benefit", "evidence", "ai_summary", mode="before")
    @classmethod
    def stringify_list(cls, v):
        if isinstance(v, list):
            return " / ".join(str(x) for x in v)
        return str(v) if v is not None else ""

class ProductDNADTO(ProductDNAResult):
    id: Optional[int] = None
    product_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ==================== Content Idea Schemas ====================
class ContentIdeaItem(BaseModel):
    angle: str
    hook: str
    target: str
    problem: str
    desire: str
    evidence: str
    purpose: str = "판매"
    content_outline: Optional[str] = None

class ContentIdeaDTO(ContentIdeaItem):
    id: Optional[int] = None
    project_id: Optional[int] = None
    product_id: int
    title: str
    status: str = "대기"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ==================== Threads Writer Schemas ====================
class ThreadsWriterMeta(BaseModel):
    core_message: str
    target: str
    desire: str
    hook: str
    evidence: str
    transition: str
    purpose: str

class ThreadsWriterResult(BaseModel):
    meta: ThreadsWriterMeta
    body: str

# ==================== Comment Schemas ====================
class CommentItem(BaseModel):
    sequence: int
    body: str
    link: Optional[str] = None
    status: str = "ACTIVE"
    delay_seconds: Optional[int] = 120
    link_type: Optional[str] = "DIRECT_AFFILIATE"

class CommentDTO(CommentItem):
    id: Optional[int] = None
    content_id: int
    created_at: Optional[datetime] = None

# ==================== Content Schemas ====================
class ContentCreateRequest(BaseModel):
    project_id: Optional[int] = None
    account_id: Optional[int] = None
    product_id: int
    idea_id: Optional[int] = None
    content_type: str = "THREADS"
    title: str
    body: str
    status: str = "DRAFT"
    comments: Optional[List[CommentItem]] = []
    post_type: Optional[str] = "MONEY_POST"
    hook_style: Optional[str] = "LOSS_AVERSION"
    comment_strategy: Optional[str] = "TIMED_COMMENT"
    affiliate_platform: Optional[str] = "COUPANG"

class ContentDTO(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    account_id: Optional[int] = None
    product_id: int
    idea_id: Optional[int] = None
    content_type: str = "THREADS"
    title: str
    body: str
    status: str = "DRAFT"
    quality_score: Optional[int] = 90
    duplicate_score: Optional[float] = 0.0
    policy_passed: Optional[bool] = True
    post_type: Optional[str] = "MONEY_POST"
    hook_style: Optional[str] = "LOSS_AVERSION"
    comment_strategy: Optional[str] = "TIMED_COMMENT"
    affiliate_platform: Optional[str] = "COUPANG"
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    comments: List[CommentDTO] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ==================== Review & Audit Schemas (Phase 4) ====================
class ReviewAuditResult(BaseModel):
    quality_score: int
    duplicate_score: float
    policy_passed: bool
    cliches_detected: List[str] = []
    feedback: str
    readability_level: str = "우수"
    hook_strength: str = "상"

# ==================== Scheduler Schemas (Phase 4) ====================
class ScheduleRequest(BaseModel):
    content_id: int
    scheduled_at: datetime

# ==================== Analytics & Learning Schemas (Phase 5) ====================
class PerformanceMetricInput(BaseModel):
    content_id: int
    views: int = 0
    likes: int = 0
    replies: int = 0
    reposts: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: int = 0

class LearningReportDTO(BaseModel):
    best_angle: str
    avg_conversion_rate: float
    total_revenue: int
    recommendations: str
    suggested_weight_adjustments: Optional[Dict[str, int]] = None

# ==================== Account Schemas ====================
class AccountDTO(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    platform: str = "THREADS"
    username: str
    display_name: Optional[str] = None
    category: Optional[str] = None
    cluster_type: Optional[str] = "VERTICAL" # VERTICAL, PERSONA, TREND
    target_audience: Optional[str] = None
    tone: Optional[str] = "친근하고 진솔한 일상 어조"
    access_token: Optional[str] = None
    status: str = "ACTIVE"
    warmup_status: Optional[str] = "ACTIVE" # WARMING_UP, ACTIVE
    post_ratio_mode: Optional[str] = "MIX_4_TO_1" # MIX_4_TO_1, DIRECT_ONLY
    organic_streak: Optional[int] = 0
    created_at: Optional[datetime] = None