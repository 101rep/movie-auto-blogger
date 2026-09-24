"""Tests for Phase 1: Job Lock, Duplicate Execution Prevention, and Stale Job Recovery."""
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.orm import Session

from app.database.models import (
    ContentJob,
    JobStatusEnum,
    Movie,
    Post,
    PostStatusEnum,
    utc_now,
)
from app.services.job_service import JobService


def test_atomic_claim_fresh_movie(db_session: Session):
    """Test claiming a fresh movie successfully creates a locked ContentJob."""
    movie = Movie(
        source="tmdb",
        external_id="lock_test_101",
        title="락 테스트 영화 1",
    )
    db_session.add(movie)
    db_session.commit()

    success, job, msg = JobService.claim_movie_job(db_session, movie.id, worker_id="worker_A")
    assert success is True
    assert job is not None
    assert job.status == JobStatusEnum.CLAIMED.value
    assert job.locked_by == "worker_A"
    assert job.locked_at is not None


def test_duplicate_movie_claim_blocked(db_session: Session):
    """Test that a second worker cannot claim an active movie being processed."""
    movie = Movie(
        source="tmdb",
        external_id="lock_test_102",
        title="락 테스트 영화 2",
    )
    db_session.add(movie)
    db_session.commit()

    # Worker A claims movie
    success_a, job_a, _ = JobService.claim_movie_job(db_session, movie.id, worker_id="worker_A")
    assert success_a is True

    # Worker B tries to claim the same movie concurrently
    success_b, job_b, reason_b = JobService.claim_movie_job(db_session, movie.id, worker_id="worker_B")
    assert success_b is False
    assert "worker_A" in reason_b or "처리 중" in reason_b


def test_completed_movie_reexecution_prevented(db_session: Session):
    """Test that once a job or post is published/completed, it cannot be re-executed."""
    movie = Movie(
        source="tmdb",
        external_id="lock_test_103",
        title="완료된 영화 3",
    )
    db_session.add(movie)
    db_session.commit()

    success, job, _ = JobService.claim_movie_job(db_session, movie.id, worker_id="worker_A")
    assert success is True

    # Mark as completed
    JobService.update_job_status(db_session, job, JobStatusEnum.COMPLETED)

    # Attempt to claim again
    success_retry, _, reason = JobService.claim_movie_job(db_session, movie.id, worker_id="worker_C")
    assert success_retry is False
    assert "완료" in reason or "이미" in reason


def test_already_published_post_blocks_claim(db_session: Session):
    """Test that an existing published or scheduled post blocks claiming."""
    movie = Movie(
        source="tmdb",
        external_id="lock_test_104",
        title="이미 발행된 영화 4",
    )
    db_session.add(movie)
    db_session.commit()

    post = Post(
        movie_id=movie.id,
        title="발행된 포스트",
        slug="published-post-slug",
        status=PostStatusEnum.PUBLISHED.value
    )
    db_session.add(post)
    db_session.commit()

    success, _, reason = JobService.claim_movie_job(db_session, movie.id, worker_id="worker_D")
    assert success is False
    assert "발행" in reason or "예약" in reason


def test_stale_job_recovery(db_session: Session):
    """Test that an abandoned or stale locked job is recovered after timeout."""
    movie = Movie(
        source="tmdb",
        external_id="lock_test_105",
        title="행 걸린 영화 5",
    )
    db_session.add(movie)
    db_session.commit()

    # Simulate hung job locked 30 minutes ago
    old_time = utc_now() - timedelta(minutes=30)
    stale_job = ContentJob(
        job_uuid="stale_uuid_105",
        movie_id=movie.id,
        status=JobStatusEnum.PROCESSING.value,
        locked_at=old_time,
        locked_by="crashed_worker",
        started_at=old_time
    )
    db_session.add(stale_job)
    db_session.commit()

    # Recovery scan
    recovered = JobService.recover_all_stale_jobs(db_session, stale_timeout_minutes=15)
    assert len(recovered) >= 1
    assert any(j.job_uuid == "stale_uuid_105" for j in recovered)

    db_session.refresh(stale_job)
    assert stale_job.status == JobStatusEnum.RETRY_WAIT.value
    assert stale_job.locked_at is None

    # New worker can now claim it
    success, job, _ = JobService.claim_movie_job(db_session, movie.id, worker_id="new_worker")
    assert success is True
    assert job.locked_by == "new_worker"
    assert job.status == JobStatusEnum.CLAIMED.value


def test_job_status_lifecycle_transitions(db_session: Session):
    """Test the full linear state transitions of a content job."""
    movie = Movie(source="tmdb", external_id="lock_test_106", title="상태전이 영화 6")
    db_session.add(movie)
    db_session.commit()

    success, job, _ = JobService.claim_movie_job(db_session, movie.id, worker_id="worker_lifecycle")
    assert job.status == JobStatusEnum.CLAIMED.value

    job = JobService.update_job_status(db_session, job, JobStatusEnum.PROCESSING)
    assert job.status == JobStatusEnum.PROCESSING.value

    job = JobService.update_job_status(db_session, job, JobStatusEnum.QUALITY_CHECK)
    assert job.status == JobStatusEnum.QUALITY_CHECK.value

    job = JobService.update_job_status(db_session, job, JobStatusEnum.PUBLISHING)
    assert job.status == JobStatusEnum.PUBLISHING.value

    job = JobService.update_job_status(db_session, job, JobStatusEnum.COMPLETED)
    assert job.status == JobStatusEnum.COMPLETED.value
    assert job.finished_at is not None
    assert job.locked_by is None
