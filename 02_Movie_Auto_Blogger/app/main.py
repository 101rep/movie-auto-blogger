import sys
if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text

from app.admin.routes import router as admin_router
from app.config import get_settings
from app.database.session import SessionLocal, init_database
from app.scheduler.scheduler import get_scheduler
from app.utils.logging import get_logger, setup_logging

settings = get_settings()
setup_logging(log_dir=settings.LOGS_DIR, log_level=settings.LOG_LEVEL)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown routines."""
    logger.info("Starting up %s v%s...", settings.APP_NAME, settings.APP_VERSION)
    
    # Initialize database tables and seed defaults
    try:
        init_database()
        from app.services.job_service import JobService
        with SessionLocal() as db:
            recovered = JobService.recover_all_stale_jobs(db)
            if recovered:
                logger.info("Startup: recovered %d stale jobs.", len(recovered))
    except Exception as e:
        logger.error("Failed to initialize database or recover stale jobs on startup: %s", str(e), exc_info=True)

    # Register Content Verticals in Platform Registry
    try:
        from app.core.registry import get_platform_registry
        from app.modules.movie.module import MovieModule
        from app.modules.welfare.module import WelfareModule
        from app.modules.entertainment.module import EntertainmentModule
        from app.modules.news.module import NewsModule
        from app.modules.travel.module import TravelModule
        from app.modules.product.module import ProductModule

        registry = get_platform_registry()
        registry.register_module(MovieModule())
        registry.register_module(WelfareModule())
        registry.register_module(EntertainmentModule())
        registry.register_module(NewsModule())
        registry.register_module(TravelModule())
        registry.register_module(ProductModule())
        logger.info("Content Vertical Modules successfully registered in Platform Registry.")
    except Exception as e:
        logger.error("Failed to register vertical modules: %s", str(e), exc_info=True)

    # Start scheduler
    scheduler = get_scheduler()
    scheduler.start()

    yield

    # Graceful shutdown
    logger.info("Shutting down %s...", settings.APP_NAME)
    scheduler.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated Korean movie blogging system for WordPress.",
    lifespan=lifespan
)

# Enable secure session middleware for admin dashboard
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="mab_session",
    max_age=14 * 24 * 3600,  # 14 days
    same_site="lax",
    https_only=settings.COOKIE_SECURE
)

# Mount Static Files for Admin UI
import os
from fastapi.staticfiles import StaticFiles
static_dir = os.path.join(os.path.dirname(__file__), "admin", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register Admin Router
app.include_router(admin_router)


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint.

    Verifies application, database connectivity, and scheduler status.
    Never exposes credentials or internal secrets.
    """
    db_ok = False
    db_error = None
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        db_error = str(e)
        logger.error("Health check database error: %s", db_error)

    scheduler = get_scheduler()
    scheduler_status = scheduler.get_status()

    is_healthy = db_ok

    payload = {
        "status": "healthy" if is_healthy else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timezone": settings.APP_TIMEZONE,
        "database": {
            "status": "connected" if db_ok else "disconnected",
            "type": "PostgreSQL" if "postgres" in settings.DATABASE_URL else "SQLite"
        },
        "scheduler": {
            "status": "running" if scheduler_status.get("is_running") else "stopped",
            "jobs_count": scheduler_status.get("jobs_count", 0)
        }
    }

    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=payload, status_code=status_code)


@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect root path to admin dashboard."""
    return RedirectResponse(url="/admin/", status_code=status.HTTP_302_FOUND)
