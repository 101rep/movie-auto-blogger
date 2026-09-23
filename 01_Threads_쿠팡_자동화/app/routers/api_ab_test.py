from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.ab_test_service import ABTestService

router = APIRouter(prefix="/api/ab-test", tags=["AB-Test"])

class ABTestCreateRequest(BaseModel):
    product_id: int
    variant_a_mode: Optional[str] = "직장인 공감형"
    variant_b_mode: Optional[str] = "짧은 호흡형"
    hours_apart: Optional[int] = 6

@router.post("/create")
def create_ab_test(req: ABTestCreateRequest, db: Session = Depends(get_db)):
    service = ABTestService(db)
    try:
        res = service.create_ab_test_variants(
            product_id=req.product_id,
            variant_a_mode=req.variant_a_mode or "직장인 공감형",
            variant_b_mode=req.variant_b_mode or "짧은 호흡형",
            hours_apart=req.hours_apart or 6
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/winner/{content_a_id}/{content_b_id}")
def get_ab_winner(content_a_id: int, content_b_id: int, db: Session = Depends(get_db)):
    service = ABTestService(db)
    try:
        return service.evaluate_ab_winner(content_a_id, content_b_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))