from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.review_service import ReviewService

router = APIRouter(prefix="/api/review", tags=["Review"])

@router.post("/{content_id}")
def audit_content_quality(content_id: int, db: Session = Depends(get_db)):
    service = ReviewService(db)
    try:
        result = service.audit_content(content_id)
        return {
            "status": "SUCCESS",
            "audit": result.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))