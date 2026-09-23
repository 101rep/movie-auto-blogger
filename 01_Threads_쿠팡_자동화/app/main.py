from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from config import settings
from database.connection import engine, Base
from database.seed import run_seed
from app.routers import (
    views,
    api_products,
    api_workflow,
    api_settings,
    api_review,
    api_scheduler,
    api_analytics,
    api_learning,
    api_accounts,
    api_autopilot,
    api_ab_test,
    api_bulk,
    api_pick,
    api_wordpress
)

import os
import asyncio
from worker import run_worker_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB tables exist and default seed runs
    Base.metadata.create_all(bind=engine)
    try:
        run_seed()
    except Exception as e:
        print(f"Seed startup notice: {e}")
    
    # Start background auto-scheduler and self-learning worker if enabled
    worker_task = None
    if os.getenv("ENABLE_WORKER", "true").lower() in ("true", "1", "yes"):
        worker_task = asyncio.create_task(run_worker_loop(interval_seconds=60))
    
    yield
    
    # Shutdown
    if worker_task:
        worker_task.cancel()

app = FastAPI(
    title=settings.APP_NAME,
    description="Threads x Coupang Automation Engine (Full Autonomous System)",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "threads_automation", "version": "2.0.0"}

# Register Routers
app.include_router(views.router)
app.include_router(api_products.router)
app.include_router(api_workflow.router)
app.include_router(api_settings.router)
app.include_router(api_review.router)
app.include_router(api_scheduler.router)
app.include_router(api_analytics.router)
app.include_router(api_learning.router)
app.include_router(api_accounts.router)
app.include_router(api_autopilot.router)
app.include_router(api_ab_test.router)
app.include_router(api_bulk.router)
app.include_router(api_pick.router)
app.include_router(api_wordpress.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "ERROR", "message": f"처리 중 오류가 발생했습니다: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)