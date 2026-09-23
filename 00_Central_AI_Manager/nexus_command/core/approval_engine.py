import time
import secrets
from typing import Dict, Any, Optional, Tuple
from nexus_command.models import RiskLevel, ActionCard, CardButton

class ApprovalEngine:
    """Manages high-risk action approvals (Level 3 Code/Config, Level 4 Destructive)."""

    def __init__(self) -> None:
        # {token: {"action": str, "params": dict, "description": str, "level": RiskLevel, "session_id": str, "expires_at": float}}
        self._pending: Dict[str, Dict[str, Any]] = {}

    def create_request(
        self,
        session_id: str,
        action_name: str,
        params: Dict[str, Any],
        description: str,
        risk_level: RiskLevel,
        ttl_seconds: int = 600
    ) -> Tuple[str, ActionCard]:
        self._cleanup()
        token = secrets.token_hex(8)
        now = time.time()
        
        self._pending[token] = {
            "session_id": session_id,
            "action": action_name,
            "params": params,
            "description": description,
            "risk_level": risk_level,
            "created_at": now,
            "expires_at": now + ttl_seconds
        }

        level_name = "LEVEL 4 (고위험/파괴적)" if risk_level >= RiskLevel.LEVEL_4_DESTRUCTIVE else "LEVEL 3 (코드/서비스 변경)"
        badge_color = "red" if risk_level >= RiskLevel.LEVEL_4_DESTRUCTIVE else "yellow"

        card = ActionCard(
            card_type="APPROVAL",
            title=f"⚠️ {level_name} 승인 요청",
            subtitle=description,
            status_badge="승인 대기 중",
            badge_color=badge_color,
            details=[
                {"label": "작업 명칭", "value": action_name},
                {"label": "위험도 등급", "value": risk_level.name},
                {"label": "실행 파라미터", "value": str(params)},
                {"label": "유효 시간", "value": f"{ttl_seconds // 60}분 이내 승인 필요"}
            ],
            buttons=[
                CardButton(
                    label="✅ 승인 및 즉시 실행",
                    action_type="approve",
                    payload=token,
                    style="primary"
                ),
                CardButton(
                    label="❌ 작업 취소",
                    action_type="reject",
                    payload=token,
                    style="secondary"
                )
            ],
            token=token
        )

        return token, card

    def get_request(self, token: str) -> Optional[Dict[str, Any]]:
        self._cleanup()
        return self._pending.get(token)

    def resolve_request(self, token: str, approved: bool) -> Optional[Dict[str, Any]]:
        self._cleanup()
        req = self._pending.pop(token, None)
        if not req:
            return None
        req["approved"] = approved
        return req

    def _cleanup(self) -> None:
        now = time.time()
        expired = [t for t, data in self._pending.items() if data["expires_at"] < now]
        for t in expired:
            self._pending.pop(t, None)

approval_engine = ApprovalEngine()
