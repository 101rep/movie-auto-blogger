from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.autopilot_service import AutopilotService

router = APIRouter(prefix="/api/autopilot", tags=["Autopilot"])

class AutopilotRequest(BaseModel):
    keyword: str
    hours_later: Optional[int] = 2
    account_id: Optional[int] = None

@router.post("/run")
def run_autopilot_pipeline(req: AutopilotRequest, db: Session = Depends(get_db)):
    service = AutopilotService(db)
    try:
        res = service.run_autopilot(
            keyword=req.keyword,
            schedule_hours_later=req.hours_later or 2,
            account_id=req.account_id
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GoldenPickRequest(BaseModel):
    min_score: Optional[int] = 90
    account_id: Optional[int] = None

@router.post("/golden-pick")
def run_golden_pick_pipeline(req: Optional[GoldenPickRequest] = None, db: Session = Depends(get_db)):
    service = AutopilotService(db)
    try:
        min_score = req.min_score if req and req.min_score is not None else 90
        account_id = req.account_id if req else None
        res = service.run_golden_pick(min_score=min_score, account_id=account_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))