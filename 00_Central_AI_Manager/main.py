import asyncio
import sys
import os
import logging

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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

logger = logging.getLogger("main")


async def run_task_queue():
    """Background task queue worker."""
    try:
        from agent.task_queue import task_queue
        await task_queue.start()
    except Exception as e:
        logger.error(f"[TaskQueue] Failed to start: {e}")


async def run_ag_gateway():
    """AG Gateway REST API server on Port 8901 (internal only)."""
    try:
        from ag_gateway.ag_server import ag_app
        config = uvicorn.Config(ag_app, host="127.0.0.1", port=8901, log_level="warning")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.error(f"[AG Gateway] Failed to start: {e}")


async def run_nexus_server():
    """NEXUS COMMAND Web Server & Messenger on Port 8888."""
    try:
        config = uvicorn.Config(nexus_app, host="0.0.0.0", port=8888, log_level="warning")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.error(f"[NEXUS Server] Failed to start: {e}")


async def run_daily_purge():
    """Daily data purge (30-day retention) at 00:00 KST."""
    import time
    while True:
        try:
            await asyncio.sleep(86400)  # Run daily
            from agent.memory_db import agent_db
            agent_db.purge_old_data(days=30)
            logger.info("[DataPurge] Old data purged (30-day retention)")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"[DataPurge] Error: {e}")


async def main():
    print("=" * 65)
    print(f"  🤖 [{settings.APP_NAME} v{settings.APP_VERSION} — AG Command Center]")
    print("  기존 서버 프로그램 통합 AI 관제 & 텔레그램 컨트롤 센터 v2.0")
    print("=" * 65)
    print(f"• 단독 관리자 Chat ID: {settings.TELEGRAM_ADMIN_CHAT_ID}")
    print(f"• 텔레그램 봇: @antigravity_courier24_bot")
    print(f"• 연동 어댑터: {[a.name for a in registry.get_all()]}")
    print(f"• 감시 주기: {settings.MONITOR_INTERVAL_SECONDS}초")
    print(f"• 아이템픽24 발행: 텔레그램 URL 수신 즉시 발행 모드 (자동예약 OFF)")
    print(f"• NEXUS COMMAND 메신저: http://127.0.0.1:8888")
    print(f"• AG Gateway: http://127.0.0.1:8901 (내부 전용)")
    print(f"• 다중 턴 대화: SQLite 세션 메모리 (ag_agent.db)")
    print("=" * 65)

    audit_logger.log("SYSTEM", "central_manager_v2_start", 1, "SUCCESS", {"version": settings.APP_VERSION})

    # Initialize agent DB on startup
    try:
        from agent.memory_db import agent_db
        logger.info("[AgentDB] Initialized ag_agent.db")
    except Exception as e:
        logger.warning(f"[AgentDB] Init warning: {e}")

    # Run all services concurrently
    await asyncio.gather(
        telegram_bot.start_polling(),
        health_monitor.start(),
        run_task_queue(),
        run_ag_gateway(),
        run_nexus_server(),
        run_daily_purge(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n[CentralManager v2.0] Gracefully shutting down...")
        telegram_bot.stop()
        health_monitor.stop()
        itempick_queue_service.stop_worker()
