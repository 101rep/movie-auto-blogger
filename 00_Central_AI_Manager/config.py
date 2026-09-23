import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    APP_NAME: str = "Gemini Central AI Manager"
    APP_VERSION: str = "2.0.0"
    APP_TIMEZONE: str = "Asia/Seoul"

    TELEGRAM_BOT_TOKEN: str = "8932770710:AAFtKYRBUwmz9-VZVxgn2TJenA8_k_B6BKs"
    TELEGRAM_ADMIN_CHAT_ID: str = "6290024230"

    GEMINI_API_KEY: str = "AQ.Ab8RN6IHrvL3AuScWRwnpo8kO4a3QevZG-oyTRs2bjMcfH8U9A"
    GEMINI_MODEL: str = "gemini-3.6-flash"

    CLOUDWAYS_HOST: str = "139.59.125.237"
    CLOUDWAYS_PORT: int = 22
    CLOUDWAYS_USER: str = "master_amtfargkbx"
    CLOUDWAYS_PASS: str = "bN6TUBm5VAVC"

    THREADS_LOCAL_URL: str = "http://127.0.0.1:8080"
    THREADS_REMOTE_URL: str = "http://139.59.125.237:9000"

    BLOGGER_LOCAL_URL: str = "http://127.0.0.1:8000"
    BLOGGER_REMOTE_URL: str = "http://139.59.125.237:8000"

    MONITOR_INTERVAL_SECONDS: int = 60
    ALERT_ON_FAILURE: bool = True

    AUDIT_DB_PATH: str = str(BASE_DIR / "data" / "audit_log.db")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
