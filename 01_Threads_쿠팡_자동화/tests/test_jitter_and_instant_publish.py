import pytest
from database.connection import SessionLocal
from database.models import Account, Content
from services.scheduler_service import SchedulerService

def test_human_jitter_applied_to_schedules():
    db = SessionLocal()
    try:
        service = SchedulerService(db)
        res = service.apply_human_jitter_and_stagger()
        assert res["status"] == "SUCCESS"
        assert res["updated_count"] >= 0

        # Verify scheduled contents don't all have 00 seconds
        scheduled = db.query(Content).filter(Content.status == "SCHEDULED").all()
        if scheduled:
            non_zero_seconds = [c for c in scheduled if c.scheduled_at and c.scheduled_at.second != 0]
            assert len(non_zero_seconds) > 0, "Human jitter must produce realistic non-zero seconds"
    finally:
        db.close()

def test_publish_next_for_account_validation():
    db = SessionLocal()
    try:
        service = SchedulerService(db)
        with pytest.raises(ValueError):
            service.publish_next_for_account(999999)
    finally:
        db.close()

def test_outbound_logs_and_scheduled_process():
    from services.outbound_service import OutboundInteractionService
    db = SessionLocal()
    try:
        acc = db.query(Account).first()
        assert acc is not None

        # Test logs fetching
        logs_data = OutboundInteractionService.get_outbound_logs(db, acc.id)
        assert "logs" in logs_data
        assert "today_count" in logs_data
        assert logs_data["daily_limit"] == 10
        assert logs_data["remaining_today"] >= 0

        # Test scheduled outbound process
        sched_res = OutboundInteractionService.process_scheduled_outbound_for_accounts(db)
        assert sched_res["status"] in ("SUCCESS", "SLEEP_HOURS")
    finally:
        db.close()

def test_anti_burst_overdue_guard():
    from datetime import datetime, timedelta
    db = SessionLocal()
    try:
        service = SchedulerService(db)
        now = datetime.utcnow()
        # Find or create 2 scheduled contents for the same account in the past (overdue)
        acc = db.query(Account).first()
        assert acc is not None

        c1 = db.query(Content).filter(Content.account_id == acc.id, Content.status == "SCHEDULED").first()
        if c1:
            c1.scheduled_at = now - timedelta(hours=2) # 2 hours overdue
            db.commit()

            # Calling process_due_schedules should publish at most 1 item for this account in this run
            published = service.process_due_schedules(min_interval_minutes=60)
            assert len(published) <= 1
    finally:
        db.close()


