"""Tests for Phase 2: Retry / Failure Recovery System."""
from datetime import datetime, timedelta, timezone
import httpx
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import (
    Base,
    ContentJob,
    JobStatusEnum,
    Movie,
    Post,
    PostStatusEnum,
    utc_now,
)
from app.services.retry_service import (
    ErrorCategory,
    RetryService,
    calculate_backoff_delay,
    classify_error,
)


@pytest.fixture
def db_session():
    """Isolated in-memory SQLite session for testing retry logic."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_classify_error_transient():
    """Verify network and temporary server errors are classified as TRANSIENT."""
    # 1. Timeout
    timeout_err = httpx.ReadTimeout("Read timed out")
    cat, retryable, msg = classify_error(timeout_err)
    assert cat == ErrorCategory.TRANSIENT
    assert retryable is True

    # 2. Connect error
    conn_err = httpx.ConnectError("Connection refused")
    cat, retryable, msg = classify_error(conn_err)
    assert cat == ErrorCategory.TRANSIENT
    assert retryable is True

    # 3. HTTP 429 Rate Limit
    req = httpx.Request("GET", "https://api.themoviedb.org")
    resp_429 = httpx.Response(429, request=req)
    http_429 = httpx.HTTPStatusError("Rate limited", request=req, response=resp_429)
    cat, retryable, msg = classify_error(http_429)
    assert cat == ErrorCategory.TRANSIENT
    assert retryable is True

    # 4. HTTP 503 Bad Gateway
    resp_503 = httpx.Response(503, request=req)
    http_503 = httpx.HTTPStatusError("Service unavailable", request=req, response=resp_503)
    cat, retryable, msg = classify_error(http_503)
    assert cat == ErrorCategory.TRANSIENT
    assert retryable is True


def test_classify_error_permanent():
    """Verify auth and validation errors are classified as PERMANENT."""
    req = httpx.Request("GET", "https://api.themoviedb.org")

    # 1. HTTP 401 Unauthorized
    resp_401 = httpx.Response(401, request=req)
    http_401 = httpx.HTTPStatusError("Unauthorized", request=req, response=resp_401)
    cat, retryable, msg = classify_error(http_401)
    assert cat == ErrorCategory.PERMANENT
    assert retryable is False

    # 2. HTTP 400 Bad Request
    resp_400 = httpx.Response(400, request=req)
    http_400 = httpx.HTTPStatusError("Bad Request", request=req, response=resp_400)
    cat, retryable, msg = classify_error(http_400)
    assert cat == ErrorCategory.PERMANENT
    assert retryable is False

    # 3. Schema / Parsing error
    key_err = KeyError("Missing required field 'title'")
    cat, retryable, msg = classify_error(key_err)
    assert cat == ErrorCategory.PERMANENT
    assert retryable is False


def test_exponential_backoff_delay():
    """Verify backoff interval progression."""
    assert calculate_backoff_delay(1) == timedelta(minutes=1)
    assert calculate_backoff_delay(2) == timedelta(minutes=5)
    assert calculate_backoff_delay(3) == timedelta(minutes=15)
    assert calculate_backoff_delay(4) == timedelta(minutes=30)
    assert calculate_backoff_delay(5) == timedelta(minutes=30)


def test_schedule_job_retry_transient_within_limit(db_session):
    """Verify a transient error schedules retry and sets RETRY_WAIT."""
    now = utc_now()
    job = ContentJob(
        job_uuid="test-transient-job",
        movie_id=101,
        job_type="movie_article",
        status=JobStatusEnum.PROCESSING.value,
        locked_at=now,
        locked_by="worker-1",
        retry_count=0,
        max_retry=3
    )
    db_session.add(job)
    db_session.commit()

    err = httpx.ReadTimeout("TMDB timeout")
    updated = RetryService.schedule_job_retry(db_session, job, err)

    assert updated.status == JobStatusEnum.RETRY_WAIT.value
    assert updated.retry_count == 1
    assert updated.is_retryable is True
    assert updated.next_retry_at is not None
    assert updated.locked_at is None
    assert updated.locked_by is None
    assert updated.error_type == ErrorCategory.TRANSIENT.value


def test_schedule_job_retry_transient_exceed_limit(db_session):
    """Verify exceeding max retries sets status to FAILED."""
    now = utc_now()
    job = ContentJob(
        job_uuid="test-exhausted-job",
        movie_id=102,
        job_type="movie_article",
        status=JobStatusEnum.PROCESSING.value,
        locked_at=now,
        locked_by="worker-1",
        retry_count=3,
        max_retry=3
    )
    db_session.add(job)
    db_session.commit()

    err = httpx.ReadTimeout("Persistent timeout")
    updated = RetryService.schedule_job_retry(db_session, job, err)

    assert updated.status == JobStatusEnum.FAILED.value
    assert updated.is_retryable is False
    assert updated.next_retry_at is None
    assert updated.finished_at is not None


def test_schedule_job_retry_permanent_fails_immediately(db_session):
    """Verify permanent errors immediately fail without scheduling retry."""
    now = utc_now()
    job = ContentJob(
        job_uuid="test-permanent-job",
        movie_id=103,
        job_type="movie_article",
        status=JobStatusEnum.PROCESSING.value,
        locked_at=now,
        locked_by="worker-1",
        retry_count=0,
        max_retry=3
    )
    db_session.add(job)
    db_session.commit()

    req = httpx.Request("GET", "https://api.themoviedb.org")
    err = httpx.HTTPStatusError("Unauthorized", request=req, response=httpx.Response(401, request=req))
    updated = RetryService.schedule_job_retry(db_session, job, err)

    assert updated.status == JobStatusEnum.FAILED.value
    assert updated.is_retryable is False
    assert updated.retry_count == 0
    assert updated.next_retry_at is None
    assert updated.error_type == ErrorCategory.PERMANENT.value


def test_get_due_retry_jobs(db_session):
    """Verify query filters for due vs future retry jobs."""
    now = utc_now()

    # Job due now (10 minutes ago)
    due_job = ContentJob(
        job_uuid="job-due-now",
        movie_id=201,
        job_type="movie_article",
        status=JobStatusEnum.RETRY_WAIT.value,
        retry_count=1,
        max_retry=3,
        next_retry_at=now - timedelta(minutes=10)
    )
    # Job due in future (10 minutes from now)
    future_job = ContentJob(
        job_uuid="job-future",
        movie_id=202,
        job_type="movie_article",
        status=JobStatusEnum.RETRY_WAIT.value,
        retry_count=1,
        max_retry=3,
        next_retry_at=now + timedelta(minutes=10)
    )
    db_session.add_all([due_job, future_job])
    db_session.commit()

    due_list = RetryService.get_due_retry_jobs(db_session)
    due_uuids = [j.job_uuid for j in due_list]

    assert "job-due-now" in due_uuids
    assert "job-future" not in due_uuids


def test_retry_idempotency_protection(db_session):
    """Verify verify_post_idempotency detects already published/scheduled posts."""
    # Add published post
    post = Post(
        movie_id=301,
        title="Published Movie Post",
        slug="published-movie-post",
        status=PostStatusEnum.PUBLISHED.value,
        published_at=utc_now()
    )
    db_session.add(post)
    db_session.commit()

    found = RetryService.verify_post_idempotency(db_session, movie_id=301)
    assert found is not None
    assert found.slug == "published-movie-post"

    not_found = RetryService.verify_post_idempotency(db_session, movie_id=999)
    assert not_found is None
