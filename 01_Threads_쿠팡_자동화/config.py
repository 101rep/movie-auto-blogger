import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = 'Threads x Coupang Automation'
    APP_ENV: str = 'development'
    APP_URL: str = 'http://localhost:8080'
    SECRET_KEY: str = 'change-me-in-production-threads-coupang-secret-key-32chars'

    DATABASE_URL: str = 'sqlite:///./threads_coupang.db'

    AI_PROVIDER: str = 'gemini' # mock, gemini, openai, grok
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = 'gemini-3.6-flash'

    GROK_API_KEY: Optional[str] = None
    GROK_MODEL: str = 'grok-4.6'

    PRODUCT_PROVIDER: str = 'mock' # mock, coupang
    COUPANG_ACCESS_KEY: Optional[str] = None
    COUPANG_SECRET_KEY: Optional[str] = None

    THREADS_PROVIDER: str = 'real' # mock, real
    THREADS_ACCESS_TOKEN: Optional[str] = None
    THREADS_USER_ID: Optional[str] = None

    ANALYTICS_PROVIDER: str = 'mock'

    PARTNERS_DISCLOSURE: str = '이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.'

    # WordPress Integration (ItemPick24 Product Blog)
    WORDPRESS_ENABLED: bool = True
    WORDPRESS_URL: Optional[str] = 'https://item.travelpick24.com'
    WORDPRESS_USERNAME: Optional[str] = 'ktaehoon80@gmail.com'
    WORDPRESS_APPLICATION_PASSWORD: Optional[str] = 'UWhD nkd8 OLpG Q91f 8dSx 0avk'
    WORDPRESS_AUTO_BRIDGE: bool = False
    # Telegram Courier (Link Courier Bot)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'

settings = Settings()
