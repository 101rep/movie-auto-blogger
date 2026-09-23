from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.learning_service import LearningService

router = APIRouter(prefix="/api/learning", tags=["Learning"])

@router.get("/insights")
@router.get("/insight")
def get_learning_insights(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    service = LearningService(db)
    insight = service.get_latest_insight(project_id=project_id)
    if not insight:
        # Generate initial insight if none exists
        report = service.analyze_and_learn(project_id=project_id)
        return report.model_dump()
    return {
        "best_angle": insight.best_angle,
        "avg_conversion_rate": insight.avg_conversion_rate,
        "total_revenue": insight.total_revenue,
        "recommendations": insight.recommendations
    }

@router.post("/train")
def trigger_learning_analysis(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    service = LearningService(db)
    try:
        report = service.analyze_and_learn(project_id=project_id)
        return {"status": "SUCCESS", "report": report.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))