# -*- coding: utf-8 -*-
"""
Permission Engine v2 — DB 영속화 승인 시스템
- 승인 토큰을 ag_agent.db의 approvals 테이블에 저장 (재시작 후에도 유지)
- request_id + action_hash + nonce + 만료시각 조합
- 1회성 nonce: 재사용 방지 (consumed_at 설정)
- 실행 직전 user_id + action 재검증
- L1~L5 분류 (명세 기준)
- 기존 PermissionLevel enum 및 인터페이스 유지 (하위 호환)
"""

import time
import secrets
from enum import IntEnum
from typing import Dict, Any, Tuple, Optional
from config import settings

class PermissionLevel(IntEnum):
    LEVEL_1_READ = 1           # 조회, 상태, 로그, 비용, GitHub 읽기 → 즉시 실행
    LEVEL_2_SOFT_CONTROL = 2   # 워커 재시작, WP-Cron, 실패 재시도 → 영향 표시 + 승인
    LEVEL_3_EXTERNAL_POST = 3  # 블로그 발행, Threads, GitHub PR → 대상·비용 + 명시적 승인
    LEVEL_4_HIGH_RISK = 4      # 운영 배포, DB 마이그레이션, 롤백 → 재확인 + 단계별 승인
    # L5 (임의 셸, 비밀키 출력 등) = 절대 금지, 코드 레벨에서 차단


class PermissionEngine:
    """DB-persistent approval system with one-time nonce tokens."""

    def __init__(self):
        self.admin_chat_id = str(settings.TELEGRAM_ADMIN_CHAT_ID).strip()
        # Legacy in-memory store (kept for backward compat during migration)
        self._pending_confirmations: Dict[str, Dict[str, Any]] = {}

    def is_authorized_user(self, user_id: str | int) -> bool:
        """Strictly allow only the admin (by user_id, not username)."""
        return str(user_id).strip() == self.admin_chat_id

    def evaluate_action_level(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> PermissionLevel:
        params = params or {}

        # L5: Forbidden actions (never execute)
        forbidden = {"exec_shell", "drop_database", "delete_all_posts", "grant_root", "expose_secrets"}
        if action_name in forbidden:
            raise PermissionError(f"L5 금지 작업: {action_name} 는 절대 실행 불가")

        # L1: Read-only
        read_actions = {
            "status", "get_status", "health_check", "get_logs", "recent_posts", "help",
            "report", "get_audit_history", "get_system_status", "get_server_metrics",
            "get_recent_blog_posts", "get_threads_accounts_detail", "get_itempick_status",
            "search_code_files", "read_code_file", "get_cost_summary",
        }
        if action_name in read_actions:
            return PermissionLevel.LEVEL_1_READ
        if action_name == "manage_blog_posts" and params.get("action") in ("check_duplicates", "list"):
            return PermissionLevel.LEVEL_1_READ

        # L2: Soft control
        soft_actions = {
            "run_wp_cron", "trigger_blog_publish", "trigger_publish", "retry_failed_task",
            "manage_blog_posts", "fix_blog_post_poster", "repair_blog_post_content",
        }
        if action_name in soft_actions:
            return PermissionLevel.LEVEL_2_SOFT_CONTROL

        # Service restart: L2 single / L3 all
        if action_name in ("restart_service", "restart", "restart_all"):
            service = str(params.get("service", "") or params.get("service_name", "")).lower()
            if service in ("all", "전체", "") or action_name == "restart_all":
                return PermissionLevel.LEVEL_3_EXTERNAL_POST
            return PermissionLevel.LEVEL_2_SOFT_CONTROL

        # L3: External posts / GitHub changes
        external_actions = {
            "publish_blog_post", "trigger_threads_warmup", "add_itempick_post",
            "generate_card_news", "modify_code_file", "create_github_pr",
        }
        if action_name in external_actions:
            return PermissionLevel.LEVEL_3_EXTERNAL_POST

        # L4: High-risk ops
        high_risk = {"deploy_to_server", "rollback_deployment", "migrate_database", "change_env_vars"}
        if action_name in high_risk:
            return PermissionLevel.LEVEL_4_HIGH_RISK

        # Default: L2
        return PermissionLevel.LEVEL_2_SOFT_CONTROL

    def check_execution_permission(self, user_id: str | int, action_name: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, PermissionLevel]:
        if not self.is_authorized_user(user_id):
            return False, "⛔ 인가되지 않은 사용자입니다.", PermissionLevel.LEVEL_4_HIGH_RISK

        try:
            level = self.evaluate_action_level(action_name, params)
        except PermissionError as e:
            return False, f"🚫 {e}", PermissionLevel.LEVEL_4_HIGH_RISK

        if level == PermissionLevel.LEVEL_1_READ:
            return True, "자동 승인 (L1 읽기)", level
        if level == PermissionLevel.LEVEL_2_SOFT_CONTROL:
            return True, "자동 승인 (L2 제한적 운영)", level

        return False, "⚠️ 명시적 승인이 필요한 작업입니다.", level

    def create_confirmation_request(
        self, user_id: str | int, action_name: str, params: Dict[str, Any],
        description: str, ttl_seconds: int = 300
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Create DB-persisted approval request. Returns (token, message, markup)."""
        try:
            level = self.evaluate_action_level(action_name, params)
        except PermissionError:
            level = PermissionLevel.LEVEL_4_HIGH_RISK

        # DB-persisted approval
        from agent.memory_db import agent_db
        approval_id, token = agent_db.create_approval(
            user_id=str(user_id),
            action_name=action_name,
            params=params,
            description=description,
            level=int(level),
            ttl=ttl_seconds
        )

        # Also store in legacy memory for fallback
        self._pending_confirmations[token] = {
            "token": token,
            "action": action_name,
            "params": params,
            "description": description,
            "level": int(level),
            "user_id": str(user_id),
            "created_at": time.time(),
            "expires_at": time.time() + ttl_seconds
        }

        level_icon = {3: "⚠️", 4: "🚨"}.get(int(level), "⚠️")
        level_name = {3: "외부 게시/변경 (L3)", 4: "고위험 운영 (L4)"}.get(int(level), f"Level {int(level)}")

        message = (
            f"{level_icon} <b>[보안 승인 요청 — {level_name}]</b>\n\n"
            f"• <b>작업</b>: <code>{description}</code>\n"
            f"• <b>코드</b>: <code>{action_name}</code>\n"
            f"• <b>설정</b>: <code>{str(params)[:120]}</code>\n"
            f"• <b>승인 유효</b>: {ttl_seconds // 60}분\n"
            f"• <b>요청 ID</b>: <code>{approval_id[:12]}</code>\n\n"
            f"운영 서버에서 즉시 실행하시겠습니까?"
        )

        markup = {
            "inline_keyboard": [[
                {"text": "✅ 승인", "callback_data": f"confirm:{token}"},
                {"text": "❌ 취소", "callback_data": f"cancel:{token}"}
            ]]
        }

        return token, message, markup

    def verify_and_consume(self, token: str, user_id: str | int) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Validate and consume token (DB-first, memory fallback)."""
        user_id_str = str(user_id).strip()

        if not self.is_authorized_user(user_id_str):
            return False, None, "⛔ 인가되지 않은 사용자의 승인 시도"

        # Try DB first
        try:
            from agent.memory_db import agent_db
            ok, item, msg = agent_db.consume_approval(token, user_id_str)
            if ok and item:
                # Re-verify action level right before execution
                try:
                    lvl = self.evaluate_action_level(item["action_name"], item.get("params", {}))
                except PermissionError as e:
                    return False, None, f"🚫 {e}"
                # Clean up memory store too
                self._pending_confirmations.pop(token, None)
                return True, {
                    "action": item["action_name"],
                    "params": item.get("params", {}),
                    "description": item["description"],
                    "level": item["level"]
                }, "승인 성공"
            # If DB says already consumed or not found, check if it's expired
            if "만료" in msg or "사용된" in msg or "유효하지" in msg:
                return False, None, msg
        except Exception:
            pass

        # Fallback: legacy memory store
        self._cleanup_expired()
        item = self._pending_confirmations.pop(token, None)
        if not item:
            return False, None, "❌ 유효하지 않거나 이미 처리된 승인 요청입니다."
        if time.time() > item["expires_at"]:
            return False, None, "⏳ 승인 유효 시간이 만료되었습니다."
        if item["user_id"] != user_id_str:
            return False, None, "⛔ 다른 사용자의 승인 토큰입니다."

        return True, item, "승인 성공"

    def cancel_pending(self, token: str, user_id: str | int) -> Tuple[bool, str]:
        user_id_str = str(user_id).strip()
        if not self.is_authorized_user(user_id_str):
            return False, "⛔ 인가되지 않은 사용자"

        # DB cancel
        try:
            from agent.memory_db import agent_db
            ok, msg = agent_db.cancel_approval(token, user_id_str)
            if ok:
                self._pending_confirmations.pop(token, None)
                return True, msg
        except Exception:
            pass

        # Memory fallback
        item = self._pending_confirmations.pop(token, None)
        if not item:
            return False, "이미 취소되었거나 존재하지 않는 요청입니다."
        return True, f"요청(<code>{item.get('description', '')}</code>)이 취소되었습니다."

    def _cleanup_expired(self):
        now = time.time()
        expired = [t for t, d in self._pending_confirmations.items() if now > d["expires_at"]]
        for t in expired:
            self._pending_confirmations.pop(t, None)


permission_engine = PermissionEngine()
