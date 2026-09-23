import asyncio
import httpx
import json
import logging
from typing import Optional, Dict, Any
from config import settings
from security.permission import permission_engine
from router.intent_router import intent_router
from router.gemini_tools import execute_tool_call
from security.audit import audit_logger

logger = logging.getLogger("telegram_bot")

class TelegramControlBot:
    """Interactive Telegram Console Controller for Gemini Central AI Manager."""

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
                    {"text": "🧵 Threads 결과 (/thread)", "callback_data": "/thread"}
                ],
                [
                    {"text": "🚨 최근 오류 (/error)", "callback_data": "/error"},
                    {"text": "🔄 실패 재실행 (/retry)", "callback_data": "/retry"}
                ],
                [
                    {"text": "🎛️ 운영 대시보드", "callback_data": "/dashboard"},
                    {"text": "🛠️ 원격 코드 수정", "callback_data": "/code"}
                ],
                [
                    {"text": "🚀 WP-Cron 즉시발행", "callback_data": "/cron"},
                    {"text": "💾 DB 백업 스냅샷", "callback_data": "/backup"}
                ],
                [
                    {"text": "☀️ 일일 브리핑", "callback_data": "/report"},
                    {"text": "🔄 전체 재시작", "callback_data": "/restart_all"}
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
                # If HTML parse error, retry without parse_mode
                if "can't parse entities" in res.text or res.status_code == 400:
                    payload.pop("parse_mode", None)
                    retry_res = await client.post(url, json=payload)
                    return retry_res.status_code == 200
                print(f"[TelegramBot Error] Send failed {res.status_code}: {res.text}")
                return False
            except Exception as e:
                print(f"[TelegramBot Error] Send message failed: {e}")
                return False

    async def answer_callback(self, callback_query_id: str, text: str = "처리 중...") -> None:
        url = f"{self.base_url}/answerCallbackQuery"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                await client.post(url, json={"callback_query_id": callback_query_id, "text": text})
            except Exception:
                pass

    async def start_polling(self) -> None:
        self.is_running = True
        print(f"[TelegramBot] @antigravity_courier24_bot 관제 리스너 시작됨 (Admin Chat ID: {self.admin_chat_id})")
        
        # Send startup greeting
        startup_msg = (
            "🌟 <b>[Gemini Central AI Manager 관제센터 활성화]</b>\n\n"
            "사장님, 기존 서버 프로그램 통합 AI 관제 시스템(PHASE 5/6)이 정상 가동되었습니다.\n"
            "Cloudways 서버, 8대 블로그, Threads 자동화가 24시간 실시간 감시되며,\n"
            "매일 09:00 KST 일일 모닝 브리핑 및 보안 인라인 승인 제어가 완벽히 연동되었습니다.\n\n"
            "아래 빠른 버튼을 누르시거나 편하게 명령해 주세요."
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
                        updates = data.get("result", [])
                        for update in updates:
                            self._last_offset = update["update_id"] + 1
                            await self._handle_update(update)
                    elif res.status_code == 409:
                        await asyncio.sleep(5)
                    else:
                        await asyncio.sleep(2)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"[TelegramBot Polling Error] {e}")
                    await asyncio.sleep(3)

    async def _handle_update(self, update: Dict[str, Any]) -> None:
        # 1. Handle Inline Button Clicks
        if "callback_query" in update:
            cb = update["callback_query"]
            cb_id = cb["id"]
            user_id = str(cb["from"]["id"])
            data = cb.get("data", "")
            
            if not permission_engine.is_authorized_user(user_id):
                await self.answer_callback(cb_id, "⛔ 인가되지 않은 사용자입니다.")
                return

            # Interactive Confirmation: Confirm execution
            if data.startswith("confirm:"):
                await self.answer_callback(cb_id, "승인 확인 중...")
                token = data.split(":", 1)[1]
                ok, item, reason = permission_engine.verify_and_consume(token, user_id)
                if ok and item:
                    action_name = item["action"]
                    params = item["params"]
                    res = await execute_tool_call(action_name, params, user_id)
                    audit_logger.log(user_id, f"confirmed_{action_name}", item["level"], "SUCCESS", params)
                    msg = (
                        f"✅ <b>[보안 승인 작업 실행 완료]</b>\n\n"
                        f"• <b>실행 작업</b>: <code>{item['description']}</code>\n"
                        f"• <b>결과 상태</b>: {res.get('status', 'success')}\n"
                        f"• <b>상세 내용</b>: {res.get('message') or res.get('output') or '정상 적용되었습니다.'}"
                    )
                    await self.send_message(user_id, msg, self._get_quick_keyboard())
                else:
                    await self.send_message(user_id, f"❌ {reason}", self._get_quick_keyboard())
                return

            # Interactive Confirmation: Cancel execution
            elif data.startswith("cancel:"):
                await self.answer_callback(cb_id, "취소 처리 중...")
                token = data.split(":", 1)[1]
                ok, reason = permission_engine.cancel_pending(token, user_id)
                await self.send_message(user_id, f"ℹ️ {reason}", self._get_quick_keyboard())
                return

            # Standard button click
            await self.answer_callback(cb_id, "명령 실행 중...")
            response_text, reply_markup = await intent_router.route_and_execute(data, user_id)
            await self.send_message(user_id, response_text, reply_markup or self._get_quick_keyboard())
            return

        # 2. Handle Text Messages
        if "message" in update:
            msg = update["message"]
            user_id = str(msg["from"]["id"])
            text = msg.get("text", "").strip()

            if not permission_engine.is_authorized_user(user_id):
                print(f"[TelegramBot Security] Unauthorized access attempt from User ID: {user_id}")
                await self.send_message(user_id, "⛔ 인가되지 않은 사용자입니다. 관리자만 이용할 수 있습니다.")
                return

            if not text:
                return

            # Execute via IntentRouter
            response_text, reply_markup = await intent_router.route_and_execute(text, user_id)
            await self.send_message(user_id, response_text, reply_markup or self._get_quick_keyboard())

    def stop(self) -> None:
        self.is_running = False

telegram_bot = TelegramControlBot()
