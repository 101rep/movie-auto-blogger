from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.bulk_import_service import BulkImportService

router = APIRouter(prefix="/api/bulk", tags=["Bulk"])

class BulkKeywordsRequest(BaseModel):
    keywords: List[str]
    interval_hours: Optional[int] = 4

@router.post("/process")
def process_bulk_keywords(req: BulkKeywordsRequest, db: Session = Depends(get_db)):
    service = BulkImportService(db)
    try:
        res = service.process_bulk_keywords(
            keywords=req.keywords,
            base_interval_hours=req.interval_hours or 4
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))