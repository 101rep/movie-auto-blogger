"""APScheduler job entrypoint for Travel vertical."""
import asyncio
from app.database.session import SessionLocal
from app.scheduler.travel.pipeline import run_travel_automation_pipeline
from app.utils.logging import get_logger

logger = get_logger("scheduler_travel_job")


def scheduled_travel_preparation_job() -> None:
    """Entrypoint called by APScheduler at 06:30 KST daily for travel pipeline."""
    logger.info("Triggered scheduled daily travel preparation job (06:30 KST)...")
    with SessionLocal() as db:
        asyncio.run(run_travel_automation_pipeline(db, force=False))
