import asyncio
import sys
import os

# Ensure safe UTF-8 streams on Windows
if sys.platform == "win32":
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

from config import settings
from adapters.registry import registry
from telegram_bot.bot import telegram_bot
from monitor.health_checker import health_monitor
from security.audit import audit_logger
from services.itempick_queue_service import itempick_queue_service
import uvicorn
from nexus_command.api.server import app as nexus_app

async def main():
    print("=" * 65)
    print(f"  🤖 [{settings.APP_NAME} v{settings.APP_VERSION}]")
    print("  기존 서버 프로그램 통합 AI 관제 & 텔레그램 컨트롤 센터")
    print("=" * 65)
    print(f"• 단독 관리자 Chat ID: {settings.TELEGRAM_ADMIN_CHAT_ID}")
    print(f"• 텔레그램 봇: @antigravity_courier24_bot")
    print(f"• 연동 어댑터: {[a.name for a in registry.get_all()]}")
    print(f"• 감시 주기: {settings.MONITOR_INTERVAL_SECONDS}초")
    print(f"• 아이템픽24 큐 워커: 가동 (10분 / 1시간 10분 순차 예약)")
    print(f"• NEXUS COMMAND 메신저: http://127.0.0.1:8888")
    print("=" * 65)

    audit_logger.log("SYSTEM", "central_manager_start", 1, "SUCCESS", {"version": settings.APP_VERSION})

    # Run Telegram Bot Polling, Real-time Health Monitor, and ItemPick Queue Worker concurrently
    await asyncio.gather(
        telegram_bot.start_polling(),
        health_monitor.start(),
        itempick_queue_service.start_worker()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[CentralManager] Gracefully shutting down...")
        telegram_bot.stop()
        health_monitor.stop()
        itempick_queue_service.stop_worker()
