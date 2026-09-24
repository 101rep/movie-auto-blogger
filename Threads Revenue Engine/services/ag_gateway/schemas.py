from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field

AITaskType = Literal["research", "strategy", "writing", "cardnews", "product", "review", "analytics"]
AIProviderName = Literal["gemini", "claude", "gpt", "mock"]

class AIResponse(BaseModel):
    content: str
    raw_data: Optional[Dict[str, Any]] = None
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    fallback_used: bool = False
    original_error: Optional[str] = None

class AIUsageSummary(BaseModel):
    today_cost_usd: float = 0.0
    total_calls: int = 0
    by_account: Dict[str, float] = Field(default_factory=dict)
    by_model: Dict[str, int] = Field(default_factory=dict)
    by_task: Dict[str, int] = Field(default_factory=dict)
