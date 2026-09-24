"""Background task scheduler for automated movie publishing."""
from typing import Dict, Any, Optional
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("scheduler")


class AutomationScheduler:
    """Manages scheduled background jobs."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.scheduler = BackgroundScheduler(timezone=self.settings.APP_TIMEZONE)
        self.is_running = False

    def start(self) -> None:
        """Start scheduler if not already running and register standard cron jobs."""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            self._register_default_jobs()
            logger.info("Scheduler started with timezone: %s", self.settings.APP_TIMEZONE)

    def _register_default_jobs(self) -> None:
        """Register daily morning preparation jobs across all 8 specialized blogs."""
        from app.scheduler.multisite_job import scheduled_all_sites_preparation_job
        from app.scheduler.movie.job import scheduled_preparation_job
        from app.scheduler.travel.job import scheduled_travel_preparation_job

        # 1. Master Multi-Site Job (All 8 Blogs, 4 Posts per Day at 08:00, 12:00, 18:00, 21:00)
        multisite_job_id = "daily_multisite_preparation"
        if not self.scheduler.get_job(multisite_job_id):
            multi_trigger = CronTrigger(
                hour=6,
                minute=0,
                timezone=ZoneInfo(self.settings.APP_TIMEZONE)
            )
            self.scheduler.add_job(
                scheduled_all_sites_preparation_job,
                trigger=multi_trigger,
                id=multisite_job_id,
                name="매일 06:00 KST 전체 8개 블로그 하루 4편 일괄 예약 발행 파이프라인",
                replace_existing=True
            )
            logger.info("Registered master job '%s' (06:00 %s)", multisite_job_id, self.settings.APP_TIMEZONE)

        # 2. Individual fallback jobs
        movie_job_id = "daily_movie_preparation"
        if not self.scheduler.get_job(movie_job_id):
            trigger = CronTrigger(
                hour=6,
                minute=15,
                timezone=ZoneInfo(self.settings.APP_TIMEZONE)
            )
            self.scheduler.add_job(
                scheduled_preparation_job,
                trigger=trigger,
                id=movie_job_id,
                name="매일 06:15 KST 트렌드스팟24(영화) 보충 예약 파이프라인",
                replace_existing=True
            )
            logger.info("Registered fallback job '%s' (06:15 %s)", movie_job_id, self.settings.APP_TIMEZONE)

        travel_job_id = "daily_travel_preparation"
        if not self.scheduler.get_job(travel_job_id):
            travel_trigger = CronTrigger(
                hour=6,
                minute=30,
                timezone=ZoneInfo(self.settings.APP_TIMEZONE)
            )
            self.scheduler.add_job(
                scheduled_travel_preparation_job,
                trigger=travel_trigger,
                id=travel_job_id,
                name="매일 06:30 KST 트래블픽24(여행) 보충 예약 파이프라인",
                replace_existing=True
            )
            logger.info("Registered fallback job '%s' (06:30 %s)", travel_job_id, self.settings.APP_TIMEZONE)

    def shutdown(self) -> None:
        """Safely shut down the scheduler."""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("Scheduler shut down.")

    def get_status(self) -> Dict[str, Any]:
        """Return human-readable status for health and dashboard checks."""
        jobs = []
        if self.is_running:
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": next_run
                })
        return {
            "is_running": self.is_running,
            "jobs_count": len(jobs),
            "jobs": jobs,
            "timezone": self.settings.APP_TIMEZONE
        }


# Singleton scheduler instance
scheduler_instance = AutomationScheduler()


def get_scheduler() -> AutomationScheduler:
    return scheduler_instance
