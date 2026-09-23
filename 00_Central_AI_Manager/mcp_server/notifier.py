# -*- coding: utf-8 -*-
"""
MCP Gateway Telegram Notifier
Broadcasts important MCP Tool execution results to Admin Telegram.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from mcp_server.mcp_config import mcp_settings

logger = logging.getLogger("MCPNotifier")

async def notify_telegram_mcp_event(tool_name: str, status: str, details: str = "") -> None:
    if not mcp_settings.TELEGRAM_NOTIFY:
        return

    try:
        from telegram_bot.bot import telegram_bot
        icon = "🟢" if status == "SUCCESS" else "⚠️"
        msg = (
            f"⚡ <b>[MCP Gateway 도구 실행 알림]</b>\n\n"
            f"• <b>실행 도구:</b> <code>{tool_name}</code>\n"
            f"• <b>상태:</b> {icon} <b>{status}</b>\n"
            f"• <b>내용:</b> {details}\n\n"
            f"🌐 <i>Antigravity MCP Gateway (Port {mcp_settings.MCP_PORT})</i>"
        )
        await telegram_bot.send_message(mcp_settings.ADMIN_CHAT_ID, msg)
    except Exception as e:
        logger.warning(f"Failed to send Telegram MCP notification: {e}")
