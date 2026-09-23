from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database.connection import get_db
from services.scheduler_service import SchedulerService
from domain_types.schemas import ScheduleRequest

router = APIRouter(prefix="/api/scheduler", tags=["Scheduler"])

@router.get("/timelines")
def get_account_timelines(db: Session = Depends(get_db)):
    service = SchedulerService(db)
    return service.get_account_timelines()

@router.post("/relay-auto-schedule")
def relay_auto_schedule(db: Session = Depends(get_db)):
    service = SchedulerService(db)
    return service.relay_auto_schedule()

@router.get("/events")
@router.get("/calendar")
def get_calendar_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db)
):
    service = SchedulerService(db)
    s_dt = datetime.fromisoformat(start) if start else None
    e_dt = datetime.fromisoformat(end) if end else None
    return service.get_calendar_events(start_date=s_dt, end_date=e_dt)

@router.post("/schedule")
def schedule_post(req: ScheduleRequest, db: Session = Depends(get_db)):
    service = SchedulerService(db)
    try:
        updated = service.schedule_content(req.content_id, req.scheduled_at)
        return {
            "status": "SUCCESS",
            "content_id": updated.id,
            "scheduled_at": updated.scheduled_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel/{content_id}")
def cancel_post_schedule(content_id: int, db: Session = Depends(get_db)):
    service = SchedulerService(db)
    try:
        updated = service.cancel_schedule(content_id)
        return {"status": "SUCCESS", "message": "예약이 취소되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish/{content_id}")
@router.post("/publish-now/{content_id}")
def publish_post_now(content_id: int, db: Session = Depends(get_db)):
    service = SchedulerService(db)
    try:
        res = service.publish_now(content_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-jitter")
def apply_schedule_jitter(db: Session = Depends(get_db)):
    service = SchedulerService(db)
    try:
        res = service.apply_human_jitter_and_stagger()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))