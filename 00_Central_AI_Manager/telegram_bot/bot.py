import asyncio
import httpx
import json
import logging
from typing import Optional, Dict, Any, List
from config import settings
from security.permission import permission_engine
from router.intent_router import intent_router
from router.gemini_tools import execute_tool_call
from security.audit import audit_logger

logger = logging.getLogger("telegram_bot")

class TelegramControlBot:
    """AG Command Center v2.0 — Telegram Bot with multi-turn agent and group chat blocking."""

    def __init__(self) -> None:
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.admin_chat_id = str(settings.TELEGRAM_ADMIN_CHAT_ID).strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.is_running = False
        self._last_offset = 0

    def _get_quick_keyboard(self) -> Dict[str, Any]:
        return {
            "inline_keyboard": [
                [
                    {"text": "📊 전체 상태 (/status)", "callback_data": "/status"},
                    {"text": "🖥️ 서버 점검 (/server)", "callback_data": "/server"}
                ],
                [
                    {"text": "✍️ WP 발행결과 (/blog)", "callback_data": "/blog"},
                    {"text": "🧵 Threads (/thread)", "callback_data": "/thread"}
                ],
                [
                    {"text": "📋 작업 현황 (/tasks)", "callback_data": "/tasks"},
                    {"text": "💰 비용 조회 (/cost)", "callback_data": "/cost"}
                ],
                [
                    {"text": "🚨 승인 대기 (/approvals)", "callback_data": "/approvals"},
                    {"text": "🔄 실패 재실행 (/retry)", "callback_data": "/retry"}
                ],
                [
                    {"text": "📸 인스타 카드뉴스 (/card)", "callback_data": "/card"},
                    {"text": "🎛️ 운영 대시보드", "callback_data": "/dashboard"}
                ],
                [
                    {"text": "🛠️ 코드 수정 (/code)", "callback_data": "/code"},
                    {"text": "🚀 WP-Cron 즉시발행", "callback_data": "/cron"}
                ],
                [
                    {"text": "☀️ 일일 브리핑", "callback_data": "/report"},
                    {"text": "📈 방문자 보고 (/traffic)", "callback_data": "/traffic"}
                ],
                [
                    {"text": "💾 DB 백업", "callback_data": "/backup"},
                    {"text": "🔄 서비스 재시작", "callback_data": "/restart_all"}
                ],
                [
                    {"text": "🌐 8대 블로그 보기", "callback_data": "/sites"},
                    {"text": "🧵 7대 Threads 보기", "callback_data": "/threads_all"}
                ],
                [
                    {"text": "🛡️ 블로그 자체검수", "callback_data": "/audit_blogs"},
                    {"text": "✨ 블로그 자가복구", "callback_data": "/heal_blogs"}
                ],
                [
                    {"text": "🔍 Threads 실검증", "callback_data": "/check_threads"},
                    {"text": "🔍 WP 실검증", "callback_data": "/check_wordpress"}
                ],
                [
                    {"text": "🔄 실패작업 복구", "callback_data": "/retry_failed"},
                    {"text": "📜 실행 로그", "callback_data": "/log"}
                ]
            ]
        }

    async def send_message(self, chat_id: str | int, text: str, reply_markup: Optional[Dict[str, Any]] = None) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": str(chat_id),
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    return True
                if "can't parse entities" in res.text or res.status_code == 400:
                    payload.pop("parse_mode", None)
                    retry_res = await client.post(url, json=payload)
                    return retry_res.status_code == 200
                logger.warning(f"[TelegramBot] Send failed {res.status_code}: {res.text[:200]}")
                return False
            except Exception as e:
                logger.warning(f"[TelegramBot] Send error: {e}")
                return False

    async def send_photo(self, chat_id: str | int, photo_path: str, caption: str = "") -> bool:
        """Send a single photo/screenshot to Telegram."""
        url = f"{self.base_url}/sendPhoto"
        if not os.path.exists(photo_path):
            return False
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(photo_path, "rb") as f:
                    files = {"photo": f}
                    data = {"chat_id": str(chat_id), "caption": caption[:1024], "parse_mode": "HTML"}
                    res = await client.post(url, data=data, files=files)
                    return res.status_code == 200
        except Exception as e:
            logger.warning(f"[TelegramBot] sendPhoto error: {e}")
            return False

    async def send_media_group(self, chat_id: str | int, image_paths: List[str], caption: str = "") -> bool:
        """Send multiple images as an Instagram-style album (media group)."""
        url = f"{self.base_url}/sendMediaGroup"
        
        media_list = []
        files = {}
        
        for idx, p in enumerate(image_paths):
            attach_name = f"photo_{idx}"
            item = {"type": "photo", "media": f"attach://{attach_name}"}
            if idx == 0 and caption:
                item["caption"] = caption[:1024]
                item["parse_mode"] = "HTML"
            media_list.append(item)
            try:
                files[attach_name] = open(p, "rb")
            except Exception as e:
                logger.error(f"Cannot open image {p}: {e}")

        if not files:
            return False

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                data = {"chat_id": str(chat_id), "media": json.dumps(media_list)}
                res = await client.post(url, data=data, files=files)
                return res.status_code == 200
        except Exception as e:
            logger.error(f"[TelegramBot] sendMediaGroup error: {e}")
            return False
        finally:
            for f in files.values():
                f.close()

    async def answer_callback(self, callback_query_id: str, text: str = "처리 중...") -> None:
        url = f"{self.base_url}/answerCallbackQuery"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                await client.post(url, json={"callback_query_id": callback_query_id, "text": text})
            except Exception:
                pass

    async def start_polling(self) -> None:
        self.is_running = True
        logger.info(f"[TelegramBot] @antigravity_courier24_bot v2.0 시작 (Admin: {self.admin_chat_id})")

        # Set task_queue notify function
        try:
            from agent.task_queue import task_queue
            task_queue.set_notify_fn(self.send_message)
            from agent.deploy_agent import deploy_agent
            deploy_agent.set_notify_fn(self.send_message)
        except Exception as e:
            logger.warning(f"[TelegramBot] TaskQueue/DeployAgent bind error: {e}")

        startup_msg = (
            "🌟 <b>[AG Command Center v2.0 활성화]</b>\n\n"
            "사장님, 개인 AI 관제센터 v2.0이 정상 가동되었습니다.\n\n"
            "🆕 <b>새 기능:</b>\n"
            "• 다중 턴 대화 (이전 문맥 기억)\n"
            "• 백그라운드 작업 큐 (/tasks)\n"
            "• 비용 추적 (/cost)\n"
            "• DB 영속 승인 시스템\n"
            "• 그룹 채팅 차단\n"
            "• 프롬프트 인젝션 방어\n\n"
            "아래 버튼을 누르시거나 자연어로 편하게 말씀해 주세요."
        )
        await self.send_message(self.admin_chat_id, startup_msg, self._get_quick_keyboard())

        async with httpx.AsyncClient(timeout=45.0) as client:
            while self.is_running:
                try:
                    url = f"{self.base_url}/getUpdates"
                    params = {"offset": self._last_offset, "timeout": 30}
                    res = await client.get(url, params=params)

                    if res.status_code == 200:
                        data = res.json()
                        for update in data.get("result", []):
                            self._last_offset = update["update_id"] + 1
                            await self._handle_update(update)
                    elif res.status_code == 409:
                        await asyncio.sleep(5)
                    else:
                        await asyncio.sleep(2)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"[TelegramBot Polling Error] {e}")
                    await asyncio.sleep(3)

    async def _handle_update(self, update: Dict[str, Any]) -> None:
        # ── Callback Query (Inline Button) ────────────────────────────────────
        if "callback_query" in update:
            cb = update["callback_query"]
            cb_id = cb["id"]
            user_id = str(cb["from"]["id"])
            chat_type = cb.get("message", {}).get("chat", {}).get("type", "private")
            data = cb.get("data", "")

            # Group chat blocking
            if chat_type != "private":
                await self.answer_callback(cb_id, "⛔ 그룹 채팅에서는 관리 명령을 사용할 수 없습니다.")
                return

            if not permission_engine.is_authorized_user(user_id):
                await self.answer_callback(cb_id, "⛔ 인가되지 않은 사용자입니다.")
                return

            # DB-persistent approval: confirm
            if data.startswith("confirm:"):
                await self.answer_callback(cb_id, "승인 확인 중...")
                token = data.split(":", 1)[1]
                ok, item, reason = permission_engine.verify_and_consume(token, user_id)
                if ok and item:
                    action_name = item["action"]
                    params = item["params"]
                    # Re-verify before execution
                    allowed, _, level = permission_engine.check_execution_permission(user_id, action_name, params)
                    if not allowed:
                        await self.send_message(user_id, f"❌ 실행 직전 권한 검증 실패: {action_name}", self._get_quick_keyboard())
                        return
                    res = await execute_tool_call(action_name, params, user_id)
                    audit_logger.log(user_id, f"confirmed_{action_name}", item["level"], "SUCCESS", params)
                    msg = (
                        f"✅ <b>[승인 작업 실행 완료]</b>\n\n"
                        f"• <b>작업</b>: <code>{item['description']}</code>\n"
                        f"• <b>결과</b>: {res.get('status', 'success')}\n"
                        f"• <b>상세</b>: {res.get('message') or res.get('output') or '정상 완료'}"
                    )
                    await self.send_message(user_id, msg, self._get_quick_keyboard())
                else:
                    await self.send_message(user_id, f"❌ {reason}", self._get_quick_keyboard())
                return

            # Approval cancel
            elif data.startswith("cancel:"):
                await self.answer_callback(cb_id, "취소 처리 중...")
                token = data.split(":", 1)[1]
                ok, reason = permission_engine.cancel_pending(token, user_id)
                await self.send_message(user_id, f"ℹ️ {reason}", self._get_quick_keyboard())
                return

            # Standard button
            await self.answer_callback(cb_id, "명령 실행 중...")
            response_text, reply_markup = await intent_router.route_and_execute(data, user_id)
            await self.send_message(user_id, response_text, reply_markup or self._get_quick_keyboard())
            return

        # ── Text Message ──────────────────────────────────────────────────────
        if "message" in update:
            msg = update["message"]
            chat = msg.get("chat", {})
            chat_type = chat.get("type", "private")
            user_id = str(msg["from"]["id"])
            text = msg.get("text", "").strip()

            # Group chat: silently ignore all management commands
            if chat_type != "private":
                logger.info(f"[TelegramBot] Group message ignored from {user_id} in {chat.get('id')}")
                return

            if not permission_engine.is_authorized_user(user_id):
                logger.warning(f"[TelegramBot Security] Unauthorized attempt from user_id={user_id}")
                await self.send_message(user_id, "⛔ 인가되지 않은 사용자입니다. 관리자만 이용할 수 있습니다.")
                return

            if not text:
                return

            # Special: /reset — start new conversation session
            if text.lower() in ("/reset", "대화초기화", "새대화"):
                from agent.conversation_manager import conversation_manager
                conversation_manager.reset(user_id)
                await self.send_message(user_id, "🔄 <b>대화 세션이 초기화되었습니다.</b>\n새로운 대화를 시작하세요!", self._get_quick_keyboard())
                return

            # Route to intent router (Tier1 fast) → Tier2 multi-turn agent
            response_text, reply_markup = await intent_router.route_and_execute(text, user_id)
            await self.send_message(user_id, response_text, reply_markup or self._get_quick_keyboard())

    def stop(self) -> None:
        self.is_running = False


telegram_bot = TelegramControlBot()
