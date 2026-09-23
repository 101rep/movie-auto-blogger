from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import PromptVersion
from config import settings
from domain_types.schemas import ProductScoreWeights

router = APIRouter(prefix="/api/settings", tags=["Settings"])

# Global in-memory overrides for weights and disclosure during runtime
ACTIVE_SETTINGS = {
    "weights": ProductScoreWeights().model_dump(),
    "partners_disclosure": settings.PARTNERS_DISCLOSURE
}

@router.get("")
def get_system_settings(db: Session = Depends(get_db)):
    prompts = db.query(PromptVersion).all()
    return {
        "weights": ACTIVE_SETTINGS["weights"],
        "partners_disclosure": ACTIVE_SETTINGS["partners_disclosure"],
        "prompts": [
            {
                "id": p.id,
                "name": p.name,
                "version": p.version,
                "prompt": p.prompt,
                "description": p.description,
                "active": p.active
            }
            for p in prompts
        ],
        "providers": {
            "ai": settings.AI_PROVIDER,
            "product": settings.PRODUCT_PROVIDER,
            "threads": settings.THREADS_PROVIDER
        }
    }

@router.post("/weights")
def update_score_weights(weights: ProductScoreWeights):
    ACTIVE_SETTINGS["weights"] = weights.model_dump()
    return {"status": "SUCCESS", "weights": ACTIVE_SETTINGS["weights"]}

@router.post("/disclosure")
def update_partners_disclosure(disclosure: str = Body(..., embed=True)):
    ACTIVE_SETTINGS["partners_disclosure"] = disclosure
    return {"status": "SUCCESS", "partners_disclosure": ACTIVE_SETTINGS["partners_disclosure"]}