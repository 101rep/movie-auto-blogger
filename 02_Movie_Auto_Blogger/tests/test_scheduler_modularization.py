"""Test scheduler modularization and backward compatibility."""
import pytest


def test_scheduler_modular_imports():
    """Verify that specialized scheduler packages can be imported directly."""
    from app.scheduler.travel import (
        run_travel_automation_pipeline,
        scheduled_travel_preparation_job,
    )
    from app.scheduler.movie import (
        run_automation_pipeline,
        scheduled_preparation_job,
        process_due_retries,
        sync_published_posts_status,
        scheduled_retry_job,
    )

    assert callable(run_travel_automation_pipeline)
    assert callable(scheduled_travel_preparation_job)
    assert callable(run_automation_pipeline)
    assert callable(scheduled_preparation_job)
    assert callable(process_due_retries)
    assert callable(sync_published_posts_status)
    assert callable(scheduled_retry_job)


def test_scheduler_jobs_facade_backward_compatibility():
    """Verify that existing code importing from app.scheduler.jobs continues to work seamlessly."""
    from app.scheduler.jobs import (
        run_automation_pipeline,
        scheduled_preparation_job,
        process_due_retries,
        sync_published_posts_status,
        scheduled_retry_job,
        run_travel_automation_pipeline,
        scheduled_travel_preparation_job,
    )

    assert callable(run_automation_pipeline)
    assert callable(scheduled_preparation_job)
    assert callable(process_due_retries)
    assert callable(sync_published_posts_status)
    assert callable(scheduled_retry_job)
    assert callable(run_travel_automation_pipeline)
    assert callable(scheduled_travel_preparation_job)


def test_scheduler_common_utilities():
    """Test calculate_schedule_datetimes and parse_kst_time."""
    from app.scheduler.common import calculate_schedule_datetimes, parse_kst_time

    parsed = parse_kst_time("09:45")
    assert parsed.hour == 9
    assert parsed.minute == 45

    # Test fallback
    fallback = parse_kst_time("invalid")
    assert fallback.hour == 8
    assert fallback.minute == 0

    slots = calculate_schedule_datetimes(
        time1_str="08:00",
        time2_str="12:00",
        time3_str="18:00",
        time4_str="22:00",
        post_count=4,
    )
    assert len(slots) == 4
    for dt in slots:
        assert dt.tzinfo is not None
