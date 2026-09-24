# -*- coding: utf-8 -*-
"""
AG Gateway Server — Port 8901 (Internal Only)
기존 Multi-LLM Router를 감싸는 내부 REST API
/ag/generate: Gemini + Multi-LLM 라우팅
/ag/tasks: 작업 큐 조회
/ag/health: 헬스 체크
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger("ag_gateway_server")

# ── App ──────────────────────────────────────────────────────────────────────
ag_app = FastAPI(title="AG Gateway", version="2.0.0", docs_url=None, redoc_url=None)

AG_INTERNAL_TOKEN = os.getenv("AG_INTERNAL_TOKEN", "ag_internal_7788")
MAX_CONCURRENT = 5
_semaphore = asyncio.Semaphore(MAX_CONCURRENT)


def _verify_token(token: str = ""):
    if token != AG_INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid AG internal token")


# ── Request Models ─────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str
    user_id: str = "system"
    task_type: str = "chat"       # chat | content | code | experimental
    model: str = ""               # optional override
    max_tokens: int = 2000
    cost_limit_usd: float = 0.10  # per-request cost cap
    idempotency_key: str = ""


class TaskQueryRequest(BaseModel):
    user_id: str = ""
    status: str = ""
    limit: int = 20


# ── Endpoints ────────────────────────────────────────────────────────────────

@ag_app.get("/ag/health")
async def ag_health():
    return {"status": "HEALTHY", "service": "AG Gateway", "version": "2.0.0", "ts": time.time()}


@ag_app.post("/ag/generate")
async def ag_generate(req: GenerateRequest, x_ag_token: str = Header(default="")):
    _verify_token(x_ag_token)

    async with _semaphore:
        try:
            from agent.memory_db import agent_db

            # Create task record
            task_id = agent_db.create_task(req.user_id, req.idempotency_key or None)

            # Route to appropriate LLM
            result = await _route_llm(req, task_id)

            # Record cost
            if result.get("usage"):
                usage = result["usage"]
                agent_db.record_cost(
                    provider=result.get("provider", "gemini"),
                    model=result.get("model", ""),
                    input_tokens=usage.get("input", 0),
                    output_tokens=usage.get("output", 0),
                    task_id=task_id
                )

            agent_db.update_task(task_id, "done", result=str(result.get("text", ""))[:300])
            return {"status": "success", "task_id": task_id, "text": result.get("text", ""), "provider": result.get("provider")}

        except Exception as e:
            logger.exception(f"[AG Gateway] /ag/generate error: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@ag_app.post("/ag/tasks")
async def ag_tasks(req: TaskQueryRequest, x_ag_token: str = Header(default="")):
    _verify_token(x_ag_token)
    from agent.memory_db import agent_db
    tasks = agent_db.get_tasks(
        user_id=req.user_id or None,
        status=req.status or None,
        limit=req.limit
    )
    return {"status": "success", "tasks": tasks, "count": len(tasks)}


@ag_app.post("/ag/costs")
async def ag_costs(x_ag_token: str = Header(default=""), days: int = 30):
    _verify_token(x_ag_token)
    from agent.memory_db import agent_db
    return agent_db.get_cost_summary(days=days)


# Keep original /gemini endpoint for backward compat
@ag_app.post("/gemini")
async def legacy_gemini(payload: Dict[str, Any], x_ag_token: str = Header(default="")):
    _verify_token(x_ag_token)
    from ag_gateway.router import route_request
    try:
        result = route_request(payload)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── LLM Router ───────────────────────────────────────────────────────────────

async def _route_llm(req: GenerateRequest, task_id: str) -> Dict[str, Any]:
    """Route to Gemini (default) or other providers based on task_type."""
    import httpx
    from config import settings

    task_type = req.task_type.lower()

    # Gemini for content and chat (default)
    if task_type in ("content", "chat", "") or not req.model:
        model = req.model or getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
        api_key = settings.GEMINI_API_KEY
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json={
                "contents": [{"role": "user", "parts": [{"text": req.prompt}]}]
            })
            if resp.status_code == 200:
                data = resp.json()
                text = "".join(
                    p.get("text", "") for p in data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                )
                usage = data.get("usageMetadata", {})
                return {"text": text, "provider": "gemini", "model": model, "usage": {
                    "input": usage.get("promptTokenCount", 0),
                    "output": usage.get("candidatesTokenCount", 0)
                }}
            raise Exception(f"Gemini API error {resp.status_code}: {resp.text[:200]}")

    # Other providers (code → Claude, experimental → Grok) — circuit breaker pattern
    else:
        from router.gemini_tools import execute_tool_call
        result = await execute_tool_call("execute_llm_task", {
            "task_type": task_type,
            "prompt": req.prompt,
            "model": req.model
        }, req.user_id)
        return {"text": result.get("text", str(result)), "provider": task_type, "model": req.model}


# ── Server Runner ─────────────────────────────────────────────────────────────

def run_ag_gateway():
    """Run AG Gateway on port 8901 (internal only)."""
    logger.info("Starting AG Gateway on port 8901...")
    uvicorn.run(ag_app, host="127.0.0.1", port=8901, log_level="warning")


async def start_ag_gateway_async():
    """Async wrapper for use in asyncio.gather."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_ag_gateway)
