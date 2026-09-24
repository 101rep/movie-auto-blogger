"""Job lock and execution lifecycle service preventing duplicate and conflicting runs."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
import uuid
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.models import (
    ContentJob,
    JobStatusEnum,
    Movie,
    Post,
    PostStatusEnum,
    utc_now,
)
from app.utils.logging import get_logger

logger = get_logger("job_service")

DEFAULT_STALE_TIMEOUT_MINUTES = 15


def ensure_tz_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensure datetime has timezone info for safe comparisons."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class JobService:
    """Service providing atomic job locks, duplicate prevention, and stale recovery."""

    @staticmethod
    def is_movie_already_processed(db: Session, movie_id: int) -> bool:
        """Check if a movie has already been published or scheduled."""
        existing = db.query(Post).filter(
            Post.movie_id == movie_id,
            Post.status.in_([
                PostStatusEnum.SCHEDULED.value,
                PostStatusEnum.PUBLISHED.value,
                PostStatusEnum.COMPLETED.value,
            ])
        ).first()
        return existing is not None

    @staticmethod
    def claim_movie_job(
        db: Session,
        movie_id: int,
        worker_id: str,
        stale_timeout_minutes: int = DEFAULT_STALE_TIMEOUT_MINUTES
    ) -> Tuple[bool, Optional[ContentJob], str]:
        """Atomically claim a movie for content processing.
        
        Returns:
            (success, job, reason)
        """
        # 1. Check if movie already successfully published
        if JobService.is_movie_already_processed(db, movie_id):
            return False, None, "이미 발행되었거나 예약된 영화입니다."

        now = utc_now()
        stale_cutoff = now - timedelta(minutes=stale_timeout_minutes)

        # 2. Check existing active job for this movie
        existing_job = db.query(ContentJob).filter(
            ContentJob.movie_id == movie_id
        ).order_by(ContentJob.created_at.desc()).first()

        if existing_job:
            # If completed, do not reprocess
            if existing_job.status == JobStatusEnum.COMPLETED.value:
                return False, existing_job, "이미 완료된 작업입니다."

            # If actively locked and not stale
            active_statuses = [
                JobStatusEnum.CLAIMED.value,
                JobStatusEnum.PROCESSING.value,
                JobStatusEnum.PUBLISHING.value,
                JobStatusEnum.QUALITY_CHECK.value,
            ]
            if existing_job.status in active_statuses:
                locked_dt = ensure_tz_aware(existing_job.locked_at)
                if locked_dt and locked_dt > stale_cutoff:
                    # Still running by another worker
                    return False, existing_job, f"다른 작업자({existing_job.locked_by})가 처리 중입니다."
                else:
                    # Stale job! Recover and take over
                    logger.warning(
                        "Recovering stale job %s for movie_id %d (locked by %s at %s)",
                        existing_job.job_uuid, movie_id, existing_job.locked_by, existing_job.locked_at
                    )
                    existing_job.status = JobStatusEnum.CLAIMED.value
                    existing_job.locked_at = now
                    existing_job.locked_by = worker_id
                    existing_job.started_at = now
                    existing_job.last_error = "Stale lock recovered and reassigned"
                    db.commit()
                    db.refresh(existing_job)
                    return True, existing_job, "Stale 작업 회수 후 락 획득 성공"

            # If pending or retry_wait or failed
            existing_job.status = JobStatusEnum.CLAIMED.value
            existing_job.locked_at = now
            existing_job.locked_by = worker_id
            existing_job.started_at = now
            db.commit()
            db.refresh(existing_job)
            return True, existing_job, "기존 작업 락 획득 성공"

        # 3. Create fresh job
        new_job = ContentJob(
            job_uuid=uuid.uuid4().hex[:16],
            movie_id=movie_id,
            job_type="movie_article",
            status=JobStatusEnum.CLAIMED.value,
            locked_at=now,
            locked_by=worker_id,
            started_at=now,
            retry_count=0,
            max_retry=3,
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return True, new_job, "신규 작업 락 획득 성공"

    @staticmethod
    def update_job_status(
        db: Session,
        job: ContentJob,
        status: JobStatusEnum,
        post_id: Optional[int] = None,
        error_msg: Optional[str] = None,
        error_type: Optional[str] = None,
        is_retryable: bool = True
    ) -> ContentJob:
        """Transition job to a new lifecycle status."""
        job.status = status.value
        job.updated_at = utc_now()
        if post_id:
            job.post_id = post_id

        if status == JobStatusEnum.COMPLETED:
            job.finished_at = utc_now()
            job.locked_at = None
            job.locked_by = None
            job.last_error = None
        elif status in (JobStatusEnum.FAILED, JobStatusEnum.RETRY_WAIT):
            job.last_error = error_msg
            job.error_type = error_type
            job.is_retryable = is_retryable
            job.locked_at = None
            job.locked_by = None
            if status == JobStatusEnum.FAILED:
                job.finished_at = utc_now()

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def recover_all_stale_jobs(
        db: Session,
        stale_timeout_minutes: int = DEFAULT_STALE_TIMEOUT_MINUTES
    ) -> List[ContentJob]:
        """Scan and recover any hung/orphaned jobs across the platform."""
        stale_cutoff = utc_now() - timedelta(minutes=stale_timeout_minutes)
        active_statuses = [
            JobStatusEnum.CLAIMED.value,
            JobStatusEnum.PROCESSING.value,
            JobStatusEnum.PUBLISHING.value,
            JobStatusEnum.QUALITY_CHECK.value,
        ]

        stale_jobs = db.query(ContentJob).filter(
            ContentJob.status.in_(active_statuses),
            ContentJob.locked_at < stale_cutoff
        ).all()

        recovered = []
        for job in stale_jobs:
            logger.warning("Recovering orphaned job %s (movie_id=%s, locked_by=%s)", job.job_uuid, job.movie_id, job.locked_by)
            job.status = JobStatusEnum.RETRY_WAIT.value
            job.last_error = f"Server restart or stale timeout recovered (over {stale_timeout_minutes}m)"
            job.locked_at = None
            job.locked_by = None
            recovered.append(job)

        if recovered:
            db.commit()
        return recovered
