"""Retry and failure recovery service with error classification and exponential backoff."""
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
from typing import Any, Dict, List, Optional, Tuple
import httpx
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.models import (
    ContentJob,
    JobStatusEnum,
    Post,
    PostStatusEnum,
    utc_now,
)
from app.services.job_service import ensure_tz_aware
from app.utils.logging import get_logger

logger = get_logger("retry_service")

# Default exponential backoff delay schedule in minutes: 1m -> 5m -> 15m -> 30m
DEFAULT_BACKOFF_SCHEDULE_MINUTES = [1, 5, 15, 30]
DEFAULT_MAX_RETRIES = 3


class ErrorCategory(str, Enum):
    """Categorization of failure types for smart recovery."""
    TRANSIENT = "TRANSIENT"      # Temporary failures suitable for automatic retry
    PERMANENT = "PERMANENT"      # Fatal or logical failures that will not resolve on retry
    UNKNOWN = "UNKNOWN"          # Unclassified error


def classify_error(exc: Exception) -> Tuple[ErrorCategory, bool, str]:
    """Classify an exception into transient vs permanent.
    
    Returns:
        (ErrorCategory, is_retryable, explanation_string)
    """
    err_str = str(exc).lower()

    # 1. Network & Timeout exceptions (Transient)
    if isinstance(exc, (
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        TimeoutError,
        ConnectionError,
        ConnectionResetError,
        ConnectionRefusedError,
    )):
        return ErrorCategory.TRANSIENT, True, f"Network/Timeout transient error: {str(exc)}"

    if any(term in err_str for term in ["timeout", "timed out", "connection reset", "connection refused", "network is unreachable"]):
        return ErrorCategory.TRANSIENT, True, f"Network/Timeout detected in message: {str(exc)}"

    # 2. HTTP Status errors
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code == 429:
            return ErrorCategory.TRANSIENT, True, f"HTTP 429 Rate Limit exceeded: {str(exc)}"
        elif code in (500, 502, 503, 504):
            return ErrorCategory.TRANSIENT, True, f"HTTP {code} Server Error (transient): {str(exc)}"
        elif code in (401, 403):
            return ErrorCategory.PERMANENT, False, f"HTTP {code} Authentication/Permission failed: {str(exc)}"
        elif code in (400, 404, 422):
            return ErrorCategory.PERMANENT, False, f"HTTP {code} Client/Validation error: {str(exc)}"

    # Check status codes embedded in error messages
    if "429" in err_str or "rate limit" in err_str or "quota exceeded" in err_str:
        return ErrorCategory.TRANSIENT, True, f"Rate limit or quota detected: {str(exc)}"
    if any(f"http {code}" in err_str or f"status {code}" in err_str or f"status_code={code}" in err_str for code in [500, 502, 503, 504]):
        return ErrorCategory.TRANSIENT, True, f"5xx server error detected: {str(exc)}"
    if any(f"http {code}" in err_str or f"status {code}" in err_str or f"status_code={code}" in err_str for code in [401, 403]):
        return ErrorCategory.PERMANENT, False, f"Authentication/Permission failure detected: {str(exc)}"

    # 3. Schema & Validation errors (Permanent)
    if isinstance(exc, (ValidationError, json.JSONDecodeError, KeyError, IndexError, TypeError, AttributeError)):
        return ErrorCategory.PERMANENT, False, f"Data/Schema validation error: {str(exc)}"

    # Default fallback: Treat unclassified as Transient if it appears environmental, else Permanent
    return ErrorCategory.TRANSIENT, True, f"Unclassified error (defaulting to retryable): {str(exc)}"


def calculate_backoff_delay(
    retry_count: int,
    schedule_minutes: Optional[List[int]] = None
) -> timedelta:
    """Calculate backoff duration based on retry attempt index.
    
    1st retry -> 1 min
    2nd retry -> 5 min
    3rd retry -> 15 min
    4th+ retry -> 30 min
    """
    schedule = schedule_minutes or DEFAULT_BACKOFF_SCHEDULE_MINUTES
    idx = max(0, retry_count - 1)
    if idx < len(schedule):
        minutes = schedule[idx]
    else:
        minutes = schedule[-1]
    return timedelta(minutes=minutes)


class RetryService:
    """Manages failure recovery, exponential backoff, and idempotent retry execution."""

    @staticmethod
    def schedule_job_retry(
        db: Session,
        job: ContentJob,
        exc: Exception,
        max_retries: Optional[int] = None,
        schedule_minutes: Optional[List[int]] = None
    ) -> ContentJob:
        """Evaluate exception and either transition job to RETRY_WAIT or FAILED."""
        category, is_retryable, explanation = classify_error(exc)
        max_limit = max_retries if max_retries is not None else (job.max_retry or DEFAULT_MAX_RETRIES)

        now = utc_now()
        job.updated_at = now
        job.last_error = f"[{category.value}] {explanation[:400]}"
        job.error_type = category.value
        job.locked_at = None
        job.locked_by = None

        if not is_retryable:
            # Permanent error: fail immediately without retry
            job.status = JobStatusEnum.FAILED.value
            job.is_retryable = False
            job.next_retry_at = None
            job.finished_at = now
            logger.warning(
                "Job %s failed PERMANENTLY: %s (is_retryable=False)",
                job.job_uuid, explanation
            )
        else:
            # Transient error: check if max retries exceeded
            if job.retry_count < max_limit:
                job.retry_count += 1
                delay = calculate_backoff_delay(job.retry_count, schedule_minutes)
                job.next_retry_at = now + delay
                job.status = JobStatusEnum.RETRY_WAIT.value
                job.is_retryable = True
                logger.info(
                    "Job %s scheduled for retry %d/%d at %s (+%s) due to: %s",
                    job.job_uuid, job.retry_count, max_limit, job.next_retry_at, delay, explanation
                )
            else:
                # Retries exhausted
                job.status = JobStatusEnum.FAILED.value
                job.is_retryable = False
                job.next_retry_at = None
                job.finished_at = now
                logger.error(
                    "Job %s FAILED after exhausting all %d retries. Last error: %s",
                    job.job_uuid, job.retry_count, explanation
                )

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_due_retry_jobs(db: Session, limit: int = 10) -> List[ContentJob]:
        """Query jobs currently in RETRY_WAIT whose next_retry_at has arrived."""
        now = utc_now()
        candidates = db.query(ContentJob).filter(
            ContentJob.status == JobStatusEnum.RETRY_WAIT.value
        ).all()

        due_jobs = []
        for job in candidates:
            if job.next_retry_at is None:
                due_jobs.append(job)
            else:
                retry_dt = ensure_tz_aware(job.next_retry_at)
                if retry_dt and retry_dt <= now:
                    due_jobs.append(job)

            if len(due_jobs) >= limit:
                break

        return due_jobs

    @staticmethod
    def verify_post_idempotency(db: Session, movie_id: int) -> Optional[Post]:
        """Check if an article for this movie has already reached published or scheduled state."""
        return db.query(Post).filter(
            Post.movie_id == movie_id,
            Post.status.in_([
                PostStatusEnum.SCHEDULED.value,
                PostStatusEnum.PUBLISHED.value,
                PostStatusEnum.COMPLETED.value
            ])
        ).first()
