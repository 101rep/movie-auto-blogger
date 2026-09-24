"""Telegram Operations Reporter for Welfare Engine V1.0.
Sends formatted daily operational reports and real-time failure alerts to the administrator.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiohttp

from welfare_engine.config import settings

logger = logging.getLogger("welfare_engine.telegram")


class WelfareTelegramReporter:
    """Manages Telegram briefing and alerting for Welfare Engine."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_ADMIN_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_message(self, text: str) -> bool:
        """Send message via Telegram Bot API."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot token or chat ID is missing. Skipping notification.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, json=payload) as resp:
                    if resp.status == 200:
                        logger.info("Telegram notification sent successfully.")
                        return True
                    else:
                        err_text = await resp.text()
                        logger.warning(f"Telegram API error ({resp.status}): {err_text}")
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")

        return False

    async def send_daily_report(
        self,
        stats: Dict[str, Dict[str, int]],
        errors: List[Dict[str, str]],
        report_date: Optional[str] = None
    ) -> bool:
        """Format and send the official Daily Operational Report."""
        date_str = report_date or datetime.now().strftime("%Y-%m-%d")

        # Stats section
        blog_a = stats.get("BLOG_A", {"scheduled": 0, "success": 0})
        blog_b = stats.get("BLOG_B", {"scheduled": 0, "success": 0})
        blog_c = stats.get("BLOG_C", {"scheduled": 0, "success": 0})

        msg_lines = [
            "🏛️ <b>[복지채널 운영 리포트]</b>",
            f"📅 <b>일자:</b> {date_str}",
            "",
            "<b>BLOG A (복지픽25 - 전 국민 지원금)</b>",
            f"발행 예정: {blog_a['scheduled']}",
            f"성공: {blog_a['success']}",
            "",
            "<b>BLOG B (복지픽23 - 청년·가족·주거)</b>",
            f"발행 예정: {blog_b['scheduled']}",
            f"성공: {blog_b['success']}",
            "",
            "<b>BLOG C (복지픽24 - 소상공인·사업자)</b>",
            f"발행 예정: {blog_c['scheduled']}",
            f"성공: {blog_c['success']}",
            "",
            "<b>오류:</b>"
        ]

        if not errors:
            msg_lines.append("<i>[정상] 발생한 오류가 없습니다. (시스템 정상 가동 중)</i>")
        else:
            for err in errors:
                msg_lines.extend([
                    f"• <b>블로그명:</b> {err.get('blog_name', '알수없음')}",
                    f"  <b>제목:</b> {err.get('title', '무제')}",
                    f"  <b>원인:</b> {err.get('reason', '원인 불명')}",
                    f"  <b>해결 상태:</b> {err.get('status', '조치 대기')}",
                    ""
                ])

        full_message = "\n".join(msg_lines)
        return await self.send_message(full_message)

    async def send_verification_failure_alert(
        self,
        blog_name: str,
        title: str,
        reason: str,
        post_id: Optional[int] = None
    ) -> bool:
        """Send emergency alert when post verification fails."""
        alert_msg = (
            "🚨 <b>[복지채널 발행 검증 실패 경보]</b>\n\n"
            f"• <b>블로그명:</b> {blog_name}\n"
            f"• <b>포스트 ID:</b> {post_id or '미발급'}\n"
            f"• <b>제목:</b> {title}\n"
            f"• <b>원인:</b> {reason}\n"
            "• <b>조치:</b> 재시도 큐 등록 및 관리자 확인 필요"
        )
        return await self.send_message(alert_msg)
