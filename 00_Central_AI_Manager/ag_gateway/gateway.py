from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from .router import route_request
from .logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="AG Gateway", version="0.1.0")

class GeminiPayload(BaseModel):
    mode: str  # Developer, DevOps, Content, Manager
    intent: str  # e.g., "analyze_code", "server_health"
    parameters: Dict[str, Any] = {}

@app.post("/gemini")
async def handle_gemini(payload: GeminiPayload):
    logger.info(f"Received payload: {payload}")
    try:
        result = route_request(payload.dict())
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("Error processing Gemini request")
        raise HTTPException(status_code=500, detail=str(e))
