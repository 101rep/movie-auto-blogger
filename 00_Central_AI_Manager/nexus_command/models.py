from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class RiskLevel(IntEnum):
    LEVEL_0_READ = 0        # 읽기 전용: 자산 조회, 상태 조회, 로그 확인 (즉시 실행)
    LEVEL_1_SAFE = 1        # 안전 제어: 헬스체크, WP-Cron 수동 트리거, 캐시 갱신 (즉시 실행)
    LEVEL_2_SERVICE = 2     # 서비스 제어: 단일 워커 재시작, 1회 수동 포스팅 (간이 확인)
    LEVEL_3_CODE = 3        # 코드/설정 변경: 소스코드 패치, 배포, 전체 서비스 재시작 (인터랙티브 승인 필수)
    LEVEL_4_DESTRUCTIVE = 4 # 파괴적 작업: DB 복원/삭제, 자격증명 변경 (고위험 2중 확인 필수)

class AssetType(str, Enum):
    WORDPRESS_SITE = "WORDPRESS_SITE"
    THREADS_ACCOUNT = "THREADS_ACCOUNT"
    SERVER = "SERVER"
    WORKER = "WORKER"
    DATABASE = "DATABASE"
    API = "API"
    AI_AGENT = "AI_AGENT"
    DESKTOP_APP = "DESKTOP_APP"

class MessageType(str, Enum):
    TEXT = "TEXT"
    USER = "USER"
    AI = "AI"
    SYSTEM = "SYSTEM"
    ACTION_CARD = "ACTION_CARD"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    LOG_VIEW = "LOG_VIEW"
    DIFF_VIEW = "DIFF_VIEW"
    ERROR = "ERROR"

class CardButton(BaseModel):
    label: str
    action_type: str  # e.g., "send_message", "tool_call", "open_url", "approve", "reject"
    payload: str      # text or tool payload or URL
    style: str = "default"  # "primary", "secondary", "danger", "success"

class ActionCard(BaseModel):
    card_type: str = "STATUS"  # STATUS, APPROVAL, LOG, METRICS, ASSET_LIST
    title: str
    subtitle: Optional[str] = None
    status_badge: Optional[str] = None  # "NORMAL", "WARNING", "ERROR", "ACTIVE"
    badge_color: Optional[str] = "blue" # "green", "red", "yellow", "blue", "gray"
    details: List[Dict[str, Any]] = Field(default_factory=list)
    raw_content: Optional[str] = None
    buttons: List[CardButton] = Field(default_factory=list)
    token: Optional[str] = None  # for approval cards

class ChatMessage(BaseModel):
    id: Optional[int] = None
    session_id: str
    sender: str  # "USER", "NEXUS", "SYSTEM"
    msg_type: MessageType = MessageType.TEXT
    content: str
    card: Optional[ActionCard] = None
    risk_level: RiskLevel = RiskLevel.LEVEL_0_READ
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class Asset(BaseModel):
    id: str
    name: str
    type: AssetType
    category: str
    url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    status: str = "ACTIVE"
    health: str = "HEALTHY"
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
    last_checked_at: Optional[str] = None

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    risk_level: RiskLevel
    target_asset_types: List[AssetType] = Field(default_factory=list)

class SessionContext(BaseModel):
    session_id: str
    user_id: str = "owner"
    active_target_asset_id: Optional[str] = None
    active_target_name: Optional[str] = None
    active_error_context: Optional[str] = None
    recent_intents: List[str] = Field(default_factory=list)
    recent_tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    updated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
