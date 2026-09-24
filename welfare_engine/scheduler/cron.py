"""Autonomous 24-Hour Scheduler for Welfare Engine V1.0.
Periodically discovers government welfare policies, triggers the multi-persona pipeline,
schedules WordPress posts, and sends daily reports.
"""
import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import Optional

from welfare_engine.config import settings
from welfare_engine.database.session import init_db
from welfare_engine.worker.pipeline import WelfarePipelineController

logger = logging.getLogger("welfare_engine.scheduler")


class WelfareScheduler:
    """Continuous scheduler executing daily and on-demand welfare publishing cycles."""

    def __init__(
        self,
        pipeline: Optional[WelfarePipelineController] = None,
        launch_date: Optional[date] = None
    ):
        self.pipeline = pipeline or WelfarePipelineController()
        self.launch_date = launch_date or date.today()
        self._running = False

    def get_days_since_launch(self) -> int:
        """Calculate days passed since service launch."""
        return max(1, (date.today() - self.launch_date).days + 1)

    async def run_daily_cycle(self, dry_run: bool = False) -> None:
        """Execute one complete daily cycle."""
        days = self.get_days_since_launch()
        logger.info(f"Triggering scheduled daily cycle (Day {days})...")
        try:
            res = await self.pipeline.run_pipeline(
                target_date=date.today(),
                days_since_launch=days,
                dry_run=dry_run
            )
            logger.info(f"Daily cycle completed with status: {res.get('status')}")
        except Exception as e:
            logger.error(f"Fatal error in daily cycle: {e}", exc_info=True)

    async def start_daemon(self, interval_hours: int = 12) -> None:
        """Run continuous background loop."""
        init_db()
        self._running = True
        logger.info(f"Welfare Engine Daemon started (Interval: {interval_hours}h)...")

        while self._running:
            now = datetime.now()
            logger.info(f"Daemon heartbeat at {now.isoformat()}")

            # Execute cycle
            await self.run_daily_cycle(dry_run=False)

            # Sleep until next interval
            await asyncio.sleep(interval_hours * 3600)

    def stop(self) -> None:
        """Stop the running daemon."""
        self._running = False
        logger.info("Welfare Engine Daemon stopped.")
