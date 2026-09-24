"""Main Daemon Entrypoint for Welfare Content Auto Publishing Engine V1.0.
Starts continuous 24-hour scheduler for autonomous policy ingestion, writing, and publishing.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Rule 3: Enforce Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from welfare_engine.database.session import init_db
from welfare_engine.scheduler.cron import WelfareScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("welfare_engine.main")


async def main_daemon():
    """Start Welfare Engine 24-hour daemon."""
    logger.info("Initializing Welfare Content Engine V1.0...")
    init_db()
    scheduler = WelfareScheduler()
    # Execute at 12-hour intervals for 24-hour continuous tracking
    await scheduler.start_daemon(interval_hours=12)


if __name__ == "__main__":
    try:
        asyncio.run(main_daemon())
    except KeyboardInterrupt:
        logger.info("Welfare Engine stopped by user.")
