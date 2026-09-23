import time
import secrets
from enum import IntEnum
from typing import Dict, Any, Tuple, Optional
from config import settings

class PermissionLevel(IntEnum):
    LEVEL_1_READ = 1          # 조회, 상태 확인, 로그 확인 (자동 승인)
    LEVEL_2_SOFT_CONTROL = 2  # 소프트 제어: 단일 서비스 헬스체크, 크론 수동 실행, 1회 발행 (자동 승인 + 감사 기록)
    LEVEL_3_CONFIG = 3        # 민감 제어: 전체 서비스 재시작, 스케줄 변경, 환경 설정 (인라인 버튼 승인 필수)
    LEVEL_4_DESTRUCTIVE = 4   # 파괴적 작업: DB 초기화, 일괄 삭제, 전체 강제 종료 (고위험 인라인 승인 필수)

class PermissionEngine:
    """Validates user authorization and action permissions with interactive confirmation support."""

    def __init__(self) -> None:
        self.admin_chat_id = str(settings.TELEGRAM_ADMIN_CHAT_ID).strip()
        # Pending confirmation store: {token: {"action": str, "params": dict, "description": str, "level": int, "user_id": str, "created_at": float, "expires_at": float}}
        self._pending_confirmations: Dict[str, Dict[str, Any]] = {}

    def is_authorized_user(self, user_id: str | int) -> bool:
        """Strictly allow only the authorized owner/admin."""
        return str(user_id).strip() == self.admin_chat_id

    def evaluate_action_level(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> PermissionLevel:
        """Determine safety level for a given action and its parameters."""
        params = params or {}
        
        read_actions = {
            "status", "get_status", "health_check", "get_logs", 
            "recent_posts", "help", "report", "get_audit_history",
            "get_system_status", "get_server_metrics", "get_recent_blog_posts"
        }
        soft_actions = {
            "run_wp_cron", "trigger_blog_publish", "trigger_publish"
        }
        
        # If restarting a single specific service vs ALL
        if action_name in ("restart_service", "restart", "restart_all"):
            service = str(params.get("service", "") or params.get("service_name", "")).lower()
            if service in ("all", "전체", "") or action_name == "restart_all":
                return PermissionLevel.LEVEL_3_CONFIG
            return PermissionLevel.LEVEL_2_SOFT_CONTROL

        config_actions = {"update_config", "change_schedule", "set_daily_count", "set_env"}
        destructive_actions = {"drop_db", "delete_all", "kill_all", "reset_hard", "delete_posts"}

        if action_name in read_actions:
            return PermissionLevel.LEVEL_1_READ
        elif action_name in soft_actions:
            return PermissionLevel.LEVEL_2_SOFT_CONTROL
        elif action_name in config_actions:
            return PermissionLevel.LEVEL_3_CONFIG
        elif action_name in destructive_actions:
            return PermissionLevel.LEVEL_4_DESTRUCTIVE
        
        return PermissionLevel.LEVEL_2_SOFT_CONTROL

    def check_execution_permission(self, user_id: str | int, action_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, PermissionLevel]:
        """Check if action can be auto-executed or requires interactive confirmation."""
        if not self.is_authorized_user(user_id):
            return False, "⛔ 인가되지 않은 사용자입니다. 접근이 거부되었습니다.", PermissionLevel.LEVEL_4_DESTRUCTIVE

        level = self.evaluate_action_level(action_name, params)
        if level in (PermissionLevel.LEVEL_1_READ, PermissionLevel.LEVEL_2_SOFT_CONTROL):
            return True, "자동 승인되었습니다.", level
        else:
            return False, "⚠️ 고위험/민감 작업으로 관리자의 명시적 승인이 필요합니다.", level

    def create_confirmation_request(
        self, 
        user_id: str | int, 
        action_name: str, 
        params: Dict[str, Any], 
        description: str,
        ttl_seconds: int = 300
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Create a pending confirmation token and generate interactive prompt message with inline buttons."""
        self._cleanup_expired()
        
        token = f"conf_{secrets.token_hex(3)}"
        level = self.evaluate_action_level(action_name, params)
        now = time.time()
        
        self._pending_confirmations[token] = {
            "token": token,
            "action": action_name,
            "params": params,
            "description": description,
            "level": int(level),
            "user_id": str(user_id).strip(),
            "created_at": now,
            "expires_at": now + ttl_seconds
        }

        level_name = "민감 제어 (Level 3)" if level == PermissionLevel.LEVEL_3_CONFIG else "고위험 제어 (Level 4)"
        level_icon = "⚠️" if level == PermissionLevel.LEVEL_3_CONFIG else "🚨"

        message = (
            f"{level_icon} <b>[보안 제어 승인 요청 - {level_name}]</b>\n\n"
            f"• <b>대상 작업</b>: <code>{description}</code>\n"
            f"• <b>작업 코드</b>: <code>{action_name}</code>\n"
            f"• <b>상세 설정</b>: <code>{params}</code>\n"
            f"• <b>승인 유효 시간</b>: 5분 이내\n\n"
            f"위 작업을 Cloudways 운영 서버에서 즉시 실행하시겠습니까?\n"
            f"아래 승인 버튼을 누르시면 안전하게 작업이 수행됩니다."
        )

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ 작업 실행 승인", "callback_data": f"confirm:{token}"},
                    {"text": "❌ 요청 취소", "callback_data": f"cancel:{token}"}
                ]
            ]
        }

        return token, message, reply_markup

    def verify_and_consume(self, token: str, user_id: str | int) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Validate token and consume it if valid, returning action info."""
        self._cleanup_expired()

        if not self.is_authorized_user(user_id):
            return False, None, "⛔ 인가되지 않은 사용자의 승인 시도입니다."

        item = self._pending_confirmations.pop(token, None)
        if not item:
            return False, None, "❌ 유효하지 않거나 이미 처리/만료된 승인 요청입니다."

        if time.time() > item["expires_at"]:
            return False, None, "⏳ 승인 유효 시간(5분)이 만료되었습니다. 다시 요청해 주세요."

        return True, item, "승인 성공"

    def cancel_pending(self, token: str, user_id: str | int) -> Tuple[bool, str]:
        """Cancel a pending action."""
        if not self.is_authorized_user(user_id):
            return False, "⛔ 인가되지 않은 사용자입니다."

        item = self._pending_confirmations.pop(token, None)
        if not item:
            return False, "이미 취소되었거나 존재하지 않는 요청입니다."

        return True, f"요청(<code>{item.get('description', '')}</code>)이 안전하게 취소되었습니다."

    def _cleanup_expired(self) -> None:
        """Remove expired tokens."""
        now = time.time()
        expired = [t for t, data in self._pending_confirmations.items() if now > data["expires_at"]]
        for t in expired:
            self._pending_confirmations.pop(t, None)

permission_engine = PermissionEngine()
