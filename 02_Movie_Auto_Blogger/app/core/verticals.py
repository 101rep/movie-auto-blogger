"""Vertical domain constants, enumeration, and capability metadata."""
from enum import Enum
from typing import Dict, Any, List


class VerticalType(str, Enum):
    """Supported content verticals in the publishing platform."""
    MOVIE = "MOVIE"
    NEWS = "NEWS"
    WELFARE = "WELFARE"              # 대한민국 복지 / 정부지원금
    ENTERTAINMENT = "ENTERTAINMENT"  # 연예 / K-컬처 뉴스
    TRAVEL = "TRAVEL"
    GAME = "GAME"
    PRODUCT = "PRODUCT"
    CUSTOM = "CUSTOM"


class VerticalStatus(str, Enum):
    """Operational status of a vertical module."""
    PRODUCTION = "PRODUCTION"     # Fully active, generating & publishing
    PREVIEW = "PREVIEW"           # In testing/preview mode
    DEVELOPMENT = "DEVELOPMENT"   # Under development
    COMING_SOON = "COMING_SOON"   # Placeholder/interface ready for future integration


VERTICAL_METADATA: Dict[VerticalType, Dict[str, Any]] = {
    VerticalType.MOVIE: {
        "name_ko": "영화 매거진",
        "description": "TMDB 기반 최신/인기 영화 분석, 공식 예고편, E-E-A-T 리뷰 및 평점",
        "status": VerticalStatus.PRODUCTION,
        "primary_provider": "TMDB",
        "supported_features": ["trailer", "spec_card", "cookie_scene", "faq", "scoring"]
    },
    VerticalType.WELFARE: {
        "name_ko": "복지 & 지원금 포털",
        "description": "정부24, 복지로 기반 청년/취업/육아/생계/주거 복지 정책, 자격요건, 지원금액, 신청 가이드",
        "status": VerticalStatus.PRODUCTION,
        "primary_provider": "BOKJIRO_GOV",
        "supported_features": ["eligibility_checklist", "benefit_highlight", "step_by_step_guide", "official_cta", "faq", "schema_gov"]
    },
    VerticalType.ENTERTAINMENT: {
        "name_ko": "연예 & K-컬처 매거진",
        "description": "실시간 핫이슈, 방송/드라마/음악 팩트 브리핑, 타임라인, 대중 반응 및 공식 입장",
        "status": VerticalStatus.PRODUCTION,
        "primary_provider": "K_ENTER_NEWS",
        "supported_features": ["issue_summary", "timeline_flow", "statement_reaction", "media_note", "faq", "schema_news"]
    },
    VerticalType.NEWS: {
        "name_ko": "뉴스 & 팩트 브리핑",
        "description": "다중 출처 사실 기반 독립적 요약 분석 및 출처 인용 저널리즘",
        "status": VerticalStatus.PRODUCTION,
        "primary_provider": "NEWS_API",
        "supported_features": ["multi_source_dedup", "fact_extraction", "citation", "faq"]
    },
    VerticalType.TRAVEL: {
        "name_ko": "여행 & 명소 가이드",
        "description": "국내외 도시/명소 기반 추천 코스, 여행 준비물, 환율·예산, 교통패스, 액티비티 총정리",
        "status": VerticalStatus.PRODUCTION,
        "primary_provider": "TOUR_API_GLOBAL",
        "supported_features": ["itinerary_cards", "spot_highlights", "weather_exchange", "cost_breakdown", "faq", "schema_travel"]
    },
    VerticalType.GAME: {
        "name_ko": "게임 리뷰 (예정)",
        "description": "신작 게임 공략, 사양 가이드, 평점 및 플레이 팁",
        "status": VerticalStatus.COMING_SOON,
        "primary_provider": "CUSTOM",
        "supported_features": ["specs", "gameplay", "tips", "faq"]
    },
    VerticalType.PRODUCT: {
        "name_ko": "상품 정보 & 스펙 비교",
        "description": "쿠팡, 오늘의집 등 실사용 스펙 비교, 내돈내산 솔직 리뷰 종합, 장단점 분석",
        "status": VerticalStatus.PRODUCTION,
        "primary_provider": "COMMERCE_CURATION",
        "supported_features": ["spec_comparison", "pros_cons", "key_takeaways", "buyer_guide", "faq"]
    }
}
