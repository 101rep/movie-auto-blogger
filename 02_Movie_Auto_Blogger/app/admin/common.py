"""Admin common utilities, templates setup, and authentication helpers."""
import os
from typing import Any, Optional
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.utils.logging import get_logger

logger = get_logger("admin.common")

# Set up Jinja2 templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

STATUS_KOREAN = {
    "COLLECTED": "영화 수집",
    "GENERATING": "AI 작성중",
    "GENERATED": "생성 완료",
    "APPROVED": "초안 완료",
    "SCHEDULED": "예약 대기",
    "PUBLISHED": "발행 완료",
    "REVIEW": "검토 필요",
    "FAILED": "생성 실패",
    "DRAFT": "임시글",
}

QUALITY_KOREAN = {
    "PASS": "검수 통과",
    "REVIEW": "검토 필요",
    "FAIL": "기준 미달",
}

RUN_STATUS_KOREAN = {
    "COMPLETED": "완료",
    "RUNNING": "실행 중",
    "FAILED": "실패",
}

def status_to_korean(val: Optional[str]) -> str:
    if not val:
        return "-"
    return STATUS_KOREAN.get(str(val).upper(), str(val))

def quality_to_korean(val: Optional[str]) -> str:
    if not val:
        return "-"
    return QUALITY_KOREAN.get(str(val).upper(), str(val))

def run_status_to_korean(val: Optional[str]) -> str:
    if not val:
        return "-"
    return RUN_STATUS_KOREAN.get(str(val).upper(), str(val))

def to_kst_datetime(val: Optional[Any]) -> str:
    """Convert UTC datetime to clean KST datetime string (YYYY-MM-DD HH:MM)."""
    if not val:
        return "-"
    try:
        kst_tz = ZoneInfo("Asia/Seoul")
        if isinstance(val, datetime):
            if val.tzinfo is None:
                val = val.replace(tzinfo=timezone.utc)
            return val.astimezone(kst_tz).strftime("%m-%d %H:%M")
        return str(val)[:16]
    except Exception:
        return str(val)[:16]

templates.env.filters["ko_status"] = status_to_korean
templates.env.filters["ko_quality"] = quality_to_korean
templates.env.filters["ko_run_status"] = run_status_to_korean
templates.env.filters["kst_datetime"] = to_kst_datetime

def get_current_admin(request: Request) -> Optional[str]:
    """Extract authenticated admin username from session cookie."""
    return request.session.get("admin_user")
