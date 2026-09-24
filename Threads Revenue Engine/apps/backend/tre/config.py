from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_mode: str = "development"
    database_url: str = "sqlite:///./tre.db"
    admin_username: str = "admin"
    admin_password: str = ""
    cors_origin: str = "http://localhost:3000"

    # Threads Integration Settings
    threads_mode: str = "mock"  # "mock" or "real"
    threads_access_token: str = ""
    threads_user_id: str = ""
    threads_app_id: str = ""
    threads_secret: str = ""
    threads_mock: bool = True

    # Instagram Integration Settings
    instagram_mode: str = "mock"  # "mock" or "real"
    instagram_access_token: str = ""
    instagram_business_account_id: str = ""
    instagram_app_id: str = ""
    instagram_app_secret: str = ""
    instagram_mock: bool = True

    # Affiliate / Coupang Settings
    affiliate_mode: str = "mock"  # "mock" or "real"
    coupang_access_key: str = ""
    coupang_secret_key: str = ""
    affiliate_mock: bool = True

    # AG Gateway & Multi-Model AI Settings
    ag_gateway_mode: str = "mock"  # "mock" or "live"
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ai_mock: bool = True
    ai_model: str = "gemini-2.5-flash"

    # Telegram & System
    telegram_mock: bool = True
    telegram_allowed_chat_id: str = "mock-admin"
    telegram_bot_token: str = ""

    queue_mode: str = "db"
    redis_url: str = "redis://localhost:6379/0"
    session_hours: int = 8

    @property
    def is_threads_mock(self) -> bool:
        if self.threads_mode.lower() == "real":
            return False
        return self.threads_mock

    @property
    def is_instagram_mock(self) -> bool:
        if self.instagram_mode.lower() == "real":
            return False
        return self.instagram_mock

    @property
    def is_affiliate_mock(self) -> bool:
        if self.affiliate_mode.lower() == "real":
            return False
        return self.affiliate_mock

@lru_cache
def settings():
    return Settings()
