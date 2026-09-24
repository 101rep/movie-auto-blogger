"""Configuration for Welfare Content Auto Publishing Engine V1.0.
Completely isolated settings and credentials for the 3 welfare blogs.
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"

# Ensure data and image directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class WelfareBlogConfig:
    """Specification and Persona definition for a Welfare Blog."""
    def __init__(
        self,
        blog_key: str,
        site_id: int,
        name: str,
        title: str,
        domain: str,
        wp_user: str,
        wp_pass: str,
        target_audience: str,
        categories: List[str],
        persona_name: str,
        persona_style: str,
        sample_phrases: List[str]
    ):
        self.blog_key = blog_key
        self.site_id = site_id
        self.name = name
        self.title = title
        self.domain = domain.rstrip("/")
        self.wp_user = wp_user
        self.wp_pass = wp_pass
        self.target_audience = target_audience
        self.categories = categories
        self.persona_name = persona_name
        self.persona_style = persona_style
        self.sample_phrases = sample_phrases

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blog_key": self.blog_key,
            "site_id": self.site_id,
            "name": self.name,
            "title": self.title,
            "domain": self.domain,
            "target_audience": self.target_audience,
            "categories": self.categories,
            "persona_name": self.persona_name,
            "persona_style": self.persona_style,
            "sample_phrases": self.sample_phrases
        }


# 3 Dedicated Welfare Blogs Mapping
BLOG_A = WelfareBlogConfig(
    blog_key="BLOG_A",
    site_id=7,
    name="복지픽25",
    title="대한민국 국민을 위한 정부지원금 안내 전문가",
    domain="https://welfare25.travelpick24.com",
    wp_user="ktaehoon80@gmail.com",
    wp_pass="A5XTcottQu6LP8FnKsP4Li57",
    target_audience="전 국민",
    categories=["정부지원금", "생활지원", "긴급지원", "세금혜택", "신청방법"],
    persona_name="친절한 복지 상담사",
    persona_style="쉽고 이해하기 쉬운 설명",
    sample_phrases=[
        "내가 받을 수 있는 지원금인지 먼저 확인해보세요.",
        "신청 조건과 방법을 하나씩 정리했습니다."
    ]
)

BLOG_B = WelfareBlogConfig(
    blog_key="BLOG_B",
    site_id=5,
    name="복지픽23",
    title="청년·가족·주거 전문 복지 정보 채널",
    domain="https://welfare23.travelpick24.com",
    wp_user="ktaehoon80@gmail.com",
    wp_pass="aEfWGRB2saPixGDR5qVybLMI",
    target_audience="20~40대 청년, 신혼부부, 육아가정",
    categories=["청년지원", "신혼부부", "육아지원", "교육지원", "주거지원"],
    persona_name="젊은 가족을 돕는 정책 전문가",
    persona_style="실생활 중심",
    sample_phrases=[
        "월세 부담을 줄일 수 있는 방법을 정리했습니다.",
        "아이를 키우는 가정이라면 확인해야 할 지원제도입니다."
    ]
)

BLOG_C = WelfareBlogConfig(
    blog_key="BLOG_C",
    site_id=6,
    name="복지픽24",
    title="소상공인과 사업자를 위한 정책 지원 전문가",
    domain="https://welfare24.travelpick24.com",
    wp_user="ktaehoon80@gmail.com",
    wp_pass="tjSclWsJhxvlHLJKRqNLULyD",
    target_audience="사업자, 자영업자, 소상공인",
    categories=["정책자금", "창업지원", "사업지원금", "고용지원", "소상공인 혜택"],
    persona_name="사업 컨설턴트",
    persona_style="실무 중심",
    sample_phrases=[
        "사업 운영에 필요한 지원제도를 확인하세요.",
        "신청 조건과 준비서류를 정리했습니다."
    ]
)

WELFARE_BLOGS: Dict[str, WelfareBlogConfig] = {
    "BLOG_A": BLOG_A,
    "BLOG_B": BLOG_B,
    "BLOG_C": BLOG_C
}


class WelfareSettings(BaseSettings):
    """Main Settings for Welfare Engine."""
    APP_NAME: str = "Welfare Content Auto Publishing Engine"
    APP_VERSION: str = "1.0.0"
    APP_TIMEZONE: str = "Asia/Seoul"

    # Database
    DB_PATH: str = str(DATA_DIR / "welfare_engine.db")
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"

    # External APIs
    DATA_GO_KR_API_KEY: str = "14130ed23528ed357f222ef5f43b087401ff3e24e4de8f7332c69ae11aeff06e"
    GEMINI_API_KEY: str = "AQ.Ab8RN6IHrvL3AuScWRwnpo8kO4a3QevZG-oyTRs2bjMcfH8U9A"
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # Telegram Operations Monitoring
    TELEGRAM_BOT_TOKEN: str = "8932770710:AAFtKYRBUwmz9-VZVxgn2TJenA8_k_B6BKs"
    TELEGRAM_ADMIN_CHAT_ID: str = "6290024230"

    # Publishing Strategy
    INITIAL_DAYS: int = 7
    INITIAL_DAILY_POSTS_PER_BLOG: int = 3
    STABILIZED_MIN_POSTS: int = 1
    STABILIZED_MAX_POSTS: int = 3

    # Schedule Slots
    SLOTS_3_POSTS: List[str] = ["09:00", "14:00", "19:30"]
    SLOTS_2_POSTS: List[str] = ["10:00", "18:00"]
    SLOTS_1_POST: List[str] = ["11:30"]

    # Image Card Generation
    THUMBNAIL_SIZE: tuple = (1080, 1080)
    FONT_PATH: str = "C:/Windows/Fonts/malgunbd.ttf"
    FONT_REGULAR_PATH: str = "C:/Windows/Fonts/malgun.ttf"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = WelfareSettings()
