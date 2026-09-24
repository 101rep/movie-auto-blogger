"""APScheduler job entrypoint for Movie vertical."""
import asyncio
from app.database.session import SessionLocal
from app.scheduler.movie.pipeline import run_automation_pipeline
from app.utils.logging import get_logger

logger = get_logger("scheduler_movie_job")


def scheduled_preparation_job() -> None:
    """Entrypoint called by APScheduler at 06:00 KST daily for movie pipeline."""
    logger.info("Triggered scheduled daily movie preparation job (06:00 KST)...")
    with SessionLocal() as db:
        asyncio.run(run_automation_pipeline(db, force=False))
