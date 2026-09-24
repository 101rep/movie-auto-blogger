"""Application settings and configuration management."""
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.utils.security import is_secret_configured, mask_secret


class Settings(BaseSettings):
    """Application configuration with strict validation and safe defaults."""

    # Core
    APP_NAME: str = "Super Auto Blogger"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    APP_TIMEZONE: str = "Asia/Seoul"
    COOKIE_SECURE: bool = False
    SECRET_KEY: str = Field(
        default="movie-auto-blogger-insecure-default-change-me-in-production-32bytes-secret",
        description="Secret key for session cookie encryption"
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./data/movie_blogger.db",
        description="Database connection URL (PostgreSQL in production, SQLite in local dev)"
    )

    # Admin Credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"  # Used to initialize admin account if not present

    # External Provider Credentials (Never exposed in UI or API responses)
    MOVIE_API_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    WORDPRESS_URL: Optional[str] = None
    WORDPRESS_USERNAME: Optional[str] = None
    WORDPRESS_APPLICATION_PASSWORD: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    OMDB_API_KEY: Optional[str] = None
    PEXELS_API_KEY: Optional[str] = None
    PIXABAY_API_KEY: Optional[str] = None
    KAKAO_REST_API_KEY: Optional[str] = None
    MOIS_PUBLIC_API_KEY: Optional[str] = None
    DATA_GO_KR_API_KEY: Optional[str] = "14130ed23528ed357f222ef5f43b087401ff3e24e4de8f7332c69ae11aeff06e"

    # Telegram Notification Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # AI Model Settings
    PRIMARY_AI: str = "openai"       # openai | gemini
    FALLBACK_AI: str = "gemini"      # gemini | openai
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # Operational Settings
    DAILY_POST_COUNT: int = 4
    CANDIDATE_POOL_SIZE: int = 30
    PUBLISH_TIME_1: str = "08:00"
    PUBLISH_TIME_2: str = "12:00"
    PUBLISH_TIME_3: str = "18:00"
    PUBLISH_TIME_4: str = "21:00"
    PUBLISH_APPLY_JITTER: bool = True
    PUBLISH_JITTER_MIN_MINUTES: int = -8
    PUBLISH_JITTER_MAX_MINUTES: int = 8
    AUTO_PUBLISH: bool = False       # Automation ON/OFF
    MEDIA_UPLOAD_ENABLED: bool = True
    INDEXNOW_KEY: Optional[str] = "trendspot24indexnowkey20260915"
    ADSENSE_CLIENT_ID: Optional[str] = None
    ADSENSE_ENABLED: bool = True

    # Directory Paths
    DATA_DIR: str = "data"
    LOGS_DIR: str = "logs"

    CTR_MODE: bool = True  # Enable CTR‑optimized titles

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    # Safe status helpers (returns human-readable status, never raw keys)
    @property
    def movie_api_status(self) -> str:
        return "설정됨" if is_secret_configured(self.MOVIE_API_TOKEN) else "미설정"

    @property
    def openai_status(self) -> str:
        return "설정됨" if is_secret_configured(self.OPENAI_API_KEY) else "미설정"

    @property
    def gemini_status(self) -> str:
        return "설정됨" if is_secret_configured(self.GEMINI_API_KEY) else "미설정"

    @property
    def youtube_status(self) -> str:
        return "설정됨" if is_secret_configured(self.YOUTUBE_API_KEY) else "미설정"

    @property
    def omdb_status(self) -> str:
        return "설정됨" if is_secret_configured(self.OMDB_API_KEY) else "미설정"

    @property
    def wordpress_status(self) -> str:
        if self.WORDPRESS_URL and self.WORDPRESS_USERNAME and is_secret_configured(self.WORDPRESS_APPLICATION_PASSWORD):
            return "설정됨"
        return "미설정"

    @property
    def telegram_status(self) -> str:
        if is_secret_configured(self.TELEGRAM_BOT_TOKEN) and self.TELEGRAM_CHAT_ID:
            return "연동 완료"
        elif is_secret_configured(self.TELEGRAM_BOT_TOKEN):
            return "토큰 설정됨(Chat ID 필요)"
        return "미설정"

    def get_masked_overview(self) -> dict:
        """Return non-sensitive dictionary representation for admin status views."""
        return {
            "app_name": self.APP_NAME,
            "version": self.APP_VERSION,
            "timezone": self.APP_TIMEZONE,
            "database_type": "PostgreSQL" if "postgres" in self.DATABASE_URL else "SQLite",
            "movie_api": self.movie_api_status,
            "openai": self.openai_status,
            "gemini": self.gemini_status,
            "youtube": self.youtube_status,
            "wordpress": self.wordpress_status,
            "telegram": self.telegram_status,
            "wordpress_url": self.WORDPRESS_URL or "미설정",
            "primary_ai": self.PRIMARY_AI,
            "fallback_ai": self.FALLBACK_AI,
            "openai_model": self.OPENAI_MODEL,
            "gemini_model": self.GEMINI_MODEL,
            "daily_post_count": self.DAILY_POST_COUNT,
            "candidate_pool_size": self.CANDIDATE_POOL_SIZE,
            "publish_time_1": self.PUBLISH_TIME_1,
            "publish_time_2": self.PUBLISH_TIME_2,
            "publish_time_3": self.PUBLISH_TIME_3,
            "publish_time_4": self.PUBLISH_TIME_4,
            "auto_publish": self.AUTO_PUBLISH,
            "media_upload_enabled": self.MEDIA_UPLOAD_ENABLED,
        }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
