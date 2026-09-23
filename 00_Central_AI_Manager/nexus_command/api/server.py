from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from nexus_command.config import nexus_settings
from nexus_command.api.routes import router

def create_nexus_app() -> FastAPI:
    app = FastAPI(
        title=nexus_settings.APP_NAME,
        description=nexus_settings.APP_SUBTITLE,
        version=nexus_settings.APP_VERSION
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    UI_DIR = Path(__file__).resolve().parent.parent / "ui"
    static_dir = UI_DIR / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(router)

    return app

app = create_nexus_app()
