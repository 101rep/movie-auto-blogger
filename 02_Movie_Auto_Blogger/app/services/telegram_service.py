"""Telegram Alert Service for Super Auto Blogger.
Handles notifications for AI credit depletion, provider failover, and post publishing.
"""
from datetime import datetime
from typing import Any, Dict, Optional
import httpx

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("telegram_service")


class TelegramAlertService:
    """Sends real-time operational alerts via Telegram Bot API."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ) -> None:
        settings = get_settings()
        self.bot_token = (bot_token or settings.TELEGRAM_BOT_TOKEN or "").strip()
        self.chat_id = str(chat_id or settings.TELEGRAM_CHAT_ID or "").strip()

    def is_configured(self) -> bool:
        """Check whether both bot token and chat id are set."""
        return bool(self.bot_token and len(self.bot_token) > 10 and self.chat_id)

    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        chat_id: Optional[str] = None
    ) -> bool:
        """Send a formatted text message to the configured or specified chat ID."""
        target_chat = str(chat_id or self.chat_id).strip()
        if not self.bot_token or not target_chat:
            logger.debug("Telegram alert skipped: bot_token or chat_id not configured.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                data = res.json()
                if res.status_code == 200 and data.get("ok"):
                    logger.info("Telegram notification sent successfully to chat %s", target_chat)
                    return True
                else:
                    logger.warning("Telegram send failed: HTTP %d - %s", res.status_code, res.text)
                    return False
        except Exception as e:
            logger.error("Telegram send_message exception: %s", str(e))
            return False

    async def send_credit_depleted_alert(
        self,
        provider: str,
        error_msg: str,
        fallback_provider: str,
        topic: Optional[str] = None
    ) -> bool:
        """Send high-priority alert when an AI provider's credit/quota is depleted."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        topic_line = f"\n• <b>작업 주제</b>: {topic}" if topic else ""
        short_err = (error_msg[:180] + "...") if len(error_msg) > 180 else error_msg

        text = (
            f"🚨 <b>[Super Auto Blogger - AI 크레딧 소진 경고]</b>\n\n"
            f"• <b>발생 시각</b>: {now_str} (KST)\n"
            f"• <b>주 AI 제공자</b>: <code>{provider.upper()}</code>\n"
            f"• <b>상태</b>: 크레딧 소진 / 잔액 부족 (HTTP 402/Quota)\n"
            f"• <b>오류 세부</b>: {short_err}{topic_line}\n\n"
            f"⚡ <b>자동 조치</b>: 예비 AI인 <b>{fallback_provider.upper()}</b>로 즉시 자동 전환되어 글 작성이 중단 없이 계속 진행됩니다!\n\n"
            f"💡 <i>안내: 원활한 운영을 위해 OpenAI/OpenRouter 잔액을 충전해주시거나, 대시보드 환경설정에서 기본 AI를 Gemini로 변경하실 수 있습니다.</i>"
        )
        return await self.send_message(text)

    async def send_failover_alert(
        self,
        primary: str,
        fallback: str,
        reason: str,
        topic: Optional[str] = None
    ) -> bool:
        """Send notification when automated failover is triggered."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        topic_line = f"\n• <b>작업 주제</b>: {topic}" if topic else ""
        short_reason = (reason[:180] + "...") if len(reason) > 180 else reason

        text = (
            f"🔄 <b>[Super Auto Blogger - AI 페일오버 자동 전환]</b>\n\n"
            f"• <b>발생 시각</b>: {now_str} (KST)\n"
            f"• <b>1차 제공자</b>: {primary.upper()} (응답 실패)\n"
            f"• <b>전환 제공자</b>: {fallback.upper()} (대체 투입)\n"
            f"• <b>사유</b>: {short_reason}{topic_line}\n\n"
            f"글 작성이 정상적으로 완수되도록 백업 파이프라인이 즉시 가동되었습니다."
        )
        return await self.send_message(text)

    async def send_publish_alert(
        self,
        site_name: str,
        title: str,
        post_url: str,
        vertical: str = "",
        ai_provider: str = "",
        image_count: int = 1
    ) -> bool:
        """Send notification when a new article is successfully published."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vertical_badge = f"[{vertical.upper()}] " if vertical else ""
        ai_badge = f"• <b>작성 AI</b>: {ai_provider.upper()}\n" if ai_provider else ""

        text = (
            f"📢 <b>[블로그 글 자동 발행 완료]</b>\n\n"
            f"• <b>발행 사이트</b>: <b>{site_name}</b>\n"
            f"• <b>카테고리</b>: {vertical_badge or '블로그'}\n"
            f"• <b>제목</b>: {title}\n"
            f"{ai_badge}"
            f"• <b>본문 이미지</b>: {image_count}장 (대표 썸네일 등록 완료)\n"
            f"• <b>발행 시각</b>: {now_str} (KST)\n\n"
            f"🔗 <a href=\"{post_url}\">발행된 글 바로 확인하기 👉</a>"
        )
        return await self.send_message(text)

    @classmethod
    async def get_recent_updates(cls, bot_token: str) -> Dict[str, Any]:
        """Fetch getUpdates from Telegram to help user find their chat ID."""
        token = bot_token.strip()
        if not token:
            return {"success": False, "message": "봇 토큰이 입력되지 않았습니다."}

        url = f"https://api.telegram.org/bot{token}/getUpdates"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                data = res.json()
                if not data.get("ok"):
                    return {"success": False, "message": f"Telegram API 오류: {data.get('description', '알 수 없는 오류')}"}

                results = data.get("result", [])
                if not results:
                    return {
                        "success": False,
                        "message": "수신된 메시지가 없습니다. 텔레그램 앱에서 생성하신 봇을 검색하여 '/start' 또는 아무 메시지를 보낸 후 다시 조회해주세요."
                    }

                latest = results[-1]
                msg = latest.get("message") or latest.get("channel_post") or {}
                chat = msg.get("chat", {})
                chat_id = chat.get("id")
                first_name = chat.get("first_name", "")
                username = chat.get("username", "")

                return {
                    "success": True,
                    "chat_id": str(chat_id),
                    "first_name": first_name,
                    "username": username,
                    "message": f"성공적으로 감지되었습니다! (Chat ID: {chat_id}, 이름: {first_name})"
                }
        except Exception as e:
            return {"success": False, "message": f"네트워크 통신 오류: {str(e)}"}

    @classmethod
    async def test_connection(cls, bot_token: str, chat_id: str) -> Dict[str, Any]:
        """Send a test message to verify Telegram bot configuration."""
        token = bot_token.strip()
        cid = str(chat_id).strip()

        if not token or not cid:
            return {"success": False, "message": "봇 토큰과 Chat ID를 모두 입력해주세요."}

        service = cls(bot_token=token, chat_id=cid)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_text = (
            f"🎉 <b>[Super Auto Blogger - 텔레그램 연동 성공!]</b>\n\n"
            f"안녕하세요! Super Auto Blogger 텔레그램 알림 시스템이 정상적으로 연결되었습니다.\n\n"
            f"• <b>연결 시각</b>: {now_str} (KST)\n"
            f"• <b>알림 항목</b>: AI 크레딧 소진 경고, 페일오버 자동 전환, 블로그 글 자동 발행 알림\n\n"
            f"앞으로 주요 상황이 발생하면 이 채팅방으로 즉시 안내해 드립니다. 🚀"
        )

        success = await service.send_message(test_text, chat_id=cid)
        if success:
            return {"success": True, "message": "텔레그램 테스트 메시지가 성공적으로 발송되었습니다! 텔레그램 앱을 확인해주세요."}
        else:
            return {
                "success": False,
                "message": "메시지 발송에 실패했습니다. 봇 토큰과 Chat ID가 올바른지, 봇에게 먼저 '/start'를 보냈는지 확인해주세요."
            }