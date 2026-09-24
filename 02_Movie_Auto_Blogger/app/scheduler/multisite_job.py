"""APScheduler job entrypoint for Universal Multi-Site Daily Automation."""
import asyncio
from app.database.session import SessionLocal
from app.scheduler.multisite_pipeline import run_all_active_sites_pipeline
from app.utils.logging import get_logger

logger = get_logger("scheduler_multisite_job")


def scheduled_all_sites_preparation_job() -> None:
    """Entrypoint called by APScheduler daily at 06:00 KST for all active blogs."""
    logger.info("Triggered scheduled daily multi-site preparation job for all 8 blogs (06:00 KST)...")
    with SessionLocal() as db:
        asyncio.run(run_all_active_sites_pipeline(db, post_count_per_site=4, force=False))
