"""Facade and backward-compatibility layer for scheduler jobs.

Re-exports jobs and pipelines from specialized modular packages:
- app.scheduler.movie: Movie vertical automation pipeline, jobs, and retries.
- app.scheduler.travel: Travel vertical automation pipeline and jobs.
"""

from app.scheduler.movie.pipeline import run_automation_pipeline
from app.scheduler.movie.job import scheduled_preparation_job
from app.scheduler.movie.retries import (
    process_due_retries,
    sync_published_posts_status,
    scheduled_retry_job,
)
from app.scheduler.travel.pipeline import run_travel_automation_pipeline
from app.scheduler.travel.job import scheduled_travel_preparation_job

__all__ = [
    "run_automation_pipeline",
    "scheduled_preparation_job",
    "process_due_retries",
    "sync_published_posts_status",
    "scheduled_retry_job",
    "run_travel_automation_pipeline",
    "scheduled_travel_preparation_job",
]
