import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

NEXUS_DIR = Path(__file__).resolve().parent
CENTRAL_DIR = NEXUS_DIR.parent

class NexusSettings(BaseSettings):
    APP_NAME: str = "NEXUS COMMAND"
    APP_SUBTITLE: str = "Private AI Messenger & Unified Command Center"
    APP_VERSION: str = "1.0.0"
    
    # Server & Port
    NEXUS_HOST: str = "0.0.0.0"
    NEXUS_PORT: int = 8888
    
    # Security
    ADMIN_PIN: str = "7788"  # Default 4-digit PIN for private owner authentication
    SESSION_SECRET: str = "nexus-secret-key-antigravity-unified-command"
    COOKIE_NAME: str = "nexus_session_token"
    SESSION_EXPIRE_HOURS: int = 720  # 30 days
    
    # AI Engine
    GEMINI_API_KEY: str = "AQ.Ab8RN6IHrvL3AuScWRwnpo8kO4a3QevZG-oyTRs2bjMcfH8U9A"
    GEMINI_MODEL: str = "gemini-3.6-flash"
    
    # DB Path
    DB_PATH: str = str(NEXUS_DIR / "data" / "nexus_command.db")
    
    # Telegram Secondary Channel
    TELEGRAM_BOT_TOKEN: str = "8932770710:AAFtKYRBUwmz9-VZVxgn2TJenA8_k_B6BKs"
    TELEGRAM_ADMIN_CHAT_ID: str = "6290024230"
    
    # Target Runtimes
    CLOUDWAYS_HOST: str = "139.59.125.237"
    CLOUDWAYS_PORT: int = 22
    CLOUDWAYS_USER: str = "master_amtfargkbx"
    CLOUDWAYS_PASS: str = "bN6TUBm5VAVC"
    
    THREADS_REMOTE_URL: str = "http://139.59.125.237:9000"
    THREADS_LOCAL_URL: str = "http://127.0.0.1:8080"
    
    BLOGGER_REMOTE_URL: str = "http://139.59.125.237:8000"
    BLOGGER_LOCAL_URL: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(
        env_file=str(CENTRAL_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

nexus_settings = NexusSettings()
