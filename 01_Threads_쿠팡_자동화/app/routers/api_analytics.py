from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard")
@router.get("/summary")
def get_analytics_dashboard(db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return service.get_summary_report()

@router.post("/sync/{content_id}")
def sync_post_analytics(content_id: int, db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    try:
        metric = service.sync_metrics_from_provider(content_id)
        return {
            "status": "SUCCESS",
            "content_id": content_id,
            "views": metric.views,
            "clicks": metric.clicks,
            "conversions": metric.conversions,
            "revenue": metric.revenue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))