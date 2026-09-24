"""Unified article schemas and generation metadata models."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FAQItem(BaseModel):
    """FAQ question and answer pair."""
    question: str = Field(description="자주 묻는 질문 (Korean)")
    answer: str = Field(description="답변 (Korean, 팩트 기반)")


class ArticleOutput(BaseModel):
    """Unified article output schema across all AI providers (OpenAI & Gemini)."""
    title: str = Field(description="블로그 글 제목 (Korean, 20~50자)")
    slug_hint: str = Field(description="URL 슬러그 힌트 (영문/한글 하이픈 형식)")
    excerpt: str = Field(description="글 요약/발췌문 (Korean, 80~150자)")
    introduction: str = Field(description="도입부 (영화의 전반적 인상 및 소개, 200자 이상)")
    basic_info_summary: str = Field(description="영화 기본정보 (장르, 러닝타임, 개봉일, 관람 포인트 개요)")
    theme_symbolism: Optional[str] = Field(
        default=None,
        description="제목의 은유, 상징성 및 원작/모티브 테마 심층 해설 (E-E-A-T 고도화, 150자 이상)"
    )
    spoiler_free_synopsis: str = Field(description="스포일러 없는 줄거리 요약 (핵심 발단/전개, 250자 이상)")
    cast_and_director: str = Field(description="감독 및 주요 출연진 소개 및 연기/연출 특징 (200자 이상)")
    character_dynamics: Optional[str] = Field(
        default=None,
        description="주요 인물 간의 갈등 구도, 대립각 및 캐릭터 케미스트리 심리전 분석 (150자 이상)"
    )
    viewing_points: List[str] = Field(default_factory=list, description="관람 포인트 3~5가지")
    hook_quote: Optional[str] = Field(default=None, description="영화를 관통하는 명대사 또는 감각적인 한 줄 캐치프레이즈")
    director_vision: Optional[str] = Field(default=None, description="감독의 연출 스타일, 미장센, 사운드와 영상미 분석 (E-E-A-T 심층 비평)")
    recommended_for: List[str] = Field(default_factory=list, description="이런 분께 추천합니다 3~4가지")
    not_recommended_for: List[str] = Field(default_factory=list, description="이런 분께는 아쉬울 수 있습니다 (솔직한 비추천 대상 2~3가지)")
    spoiler_deep_dive: Optional[str] = Field(
        default=None,
        description="결말 복선, 상징적 의미 및 심층 해석 (스포일러 주의 아코디언 토글용, 150자 이상)"
    )
    similar_movie_notes: List[str] = Field(default_factory=list, description="함께 살펴볼 비슷한 영화 2~3편과 추천 이유")
    post_credit_scene: Optional[str] = Field(default=None, description="쿠키 영상 유무 및 관람 팁 안내 (스포일러 방지)")
    rating_score: Optional[float] = Field(default=8.5, description="10점 만점 기준 에디터 추천 평점 (예: 8.5)")
    rating_reason: Optional[str] = Field(default=None, description="평점 선정 핵심 이유")
    faq: List[FAQItem] = Field(default_factory=list, description="자주 묻는 질문 2~4개")
    conclusion: str = Field(description="마무리 감상 및 총평 (150자 이상)")
    engagement_question: Optional[str] = Field(
        default=None,
        description="독자 댓글 참여와 체류시간을 유도하는 생각거리 질문 및 토론 유도 문구"
    )
    seo_title: str = Field(description="SEO 검색 최적화 제목 (30~55자)")
    meta_description: str = Field(description="검색엔진 메타 설명문 (100~160자)")
    tags: List[str] = Field(default_factory=list, description="워드프레스 태그 목록 (최대 8개)")
    factual_warnings: List[str] = Field(
        default_factory=list,
        description="제공된 데이터에 없어 검증되지 못한 사실에 대한 안내 또는 주의사항"
    )


class WelfareArticleOutput(BaseModel):
    """Structured output schema for Korean Government Welfare & Benefit articles."""
    title: str = Field(description="블로그 글 제목 (Korean, 20~55자, 핵심 혜택 및 연도/대상 포함)")
    slug_hint: str = Field(description="URL 슬러그 힌트 (영문/한글 하이픈 형식)")
    excerpt: str = Field(description="글 요약/발췌문 (Korean, 80~150자)")
    introduction: str = Field(description="도입부 (정책 도입 배경, 누구를 위한 혜택인지 소개, 200자 이상)")
    target_summary: str = Field(description="지원 대상 및 자격 요건 상세 (소득기준, 연령, 거주지 등, 200자 이상)")
    eligibility_checklist: List[str] = Field(default_factory=list, description="자격 확인 체크리스트 3~5가지")
    benefit_details: str = Field(description="지원 내용 및 지급 혜택 (현금, 바우처, 대출이자 감면 등 구체적 금액, 200자 이상)")
    benefit_highlight: str = Field(description="한눈에 보는 핵심 혜택 한줄 요약 (예: 매월 50만원씩 최대 6개월 지원)")
    application_period: str = Field(description="신청 기간 및 접수 일정 (연중 상시, 또는 구체적 기간)")
    application_steps: List[str] = Field(default_factory=list, description="신청 방법 단계별 가이드 (1단계, 2단계, 3단계 등)")
    required_documents: List[str] = Field(default_factory=list, description="필수 구비 서류 목록 3~5가지")
    official_apply_url: str = Field(description="공식 신청 사이트 URL 또는 정부 포털 링크")
    inquiry_contact: Optional[str] = Field(default=None, description="문의처 전화번호 및 담당 부처 (예: 보건복지상담센터 129)")
    caution_notes: List[str] = Field(default_factory=list, description="신청 시 주의사항 및 중복 수혜 불가 정책 안내 2~3가지")
    faq: List[FAQItem] = Field(default_factory=list, description="자주 묻는 질문 3~4개")
    conclusion: str = Field(description="마무리 안내 및 신청 당부 (150자 이상)")
    seo_title: str = Field(description="SEO 검색 최적화 제목 (30~55자)")
    meta_description: str = Field(description="검색엔진 메타 설명문 (100~160자)")
    tags: List[str] = Field(default_factory=list, description="워드프레스 태그 목록 (최대 8개)")


class EntertainmentArticleOutput(BaseModel):
    """Structured output schema for Entertainment & K-Culture journalism articles."""
    title: str = Field(description="연예 기사/매거진 제목 (Korean, 20~55자, 인물/작품명 및 핵심 쟁점 포함)")
    slug_hint: str = Field(description="URL 슬러그 힌트 (영문/한글 하이픈 형식)")
    excerpt: str = Field(description="글 요약/발췌문 (Korean, 80~150자)")
    introduction: str = Field(description="도입부 (이슈 개요 및 화제 배경, 200자 이상)")
    quick_summary_points: List[str] = Field(default_factory=list, description="핵심 3줄 요약 포인트")
    timeline_events: List[str] = Field(default_factory=list, description="사건/이슈 경과 타임라인 (시간순 정리 3~5단계)")
    key_facts: str = Field(description="확인된 핵심 팩트 분석 (루머 배제, 언론 보도 기반 객관적 서술, 200자 이상)")
    official_statements: Optional[str] = Field(default=None, description="소속사/당사자 공식 입장 및 발표 내용 (150자 이상)")
    public_reactions: str = Field(description="대중 및 팬덤, 업계 반응 종합 (150자 이상)")
    future_outlook: str = Field(description="향후 활동 계획, 방송 일정 및 업계 파장 전망 (150자 이상)")
    faq: List[FAQItem] = Field(default_factory=list, description="이슈 관련 자주 묻는 질문 2~3개")
    conclusion: str = Field(description="에디터 총평 및 시사점 (150자 이상)")
    seo_title: str = Field(description="SEO 검색 최적화 제목 (30~55자)")
    meta_description: str = Field(description="검색엔진 메타 설명문 (100~160자)")
    tags: List[str] = Field(default_factory=list, description="워드프레스 태그 목록 (최대 8개)")


class TravelSpotItem(BaseModel):
    """Normalized tourist attraction or spot highlight."""
    name: str = Field(description="관광지 또는 명소 명칭")
    category: str = Field(default="명소", description="카테고리 (랜드마크, 맛집, 카페, 박물관, 쇼핑 등)")
    description: str = Field(description="명소 소개 및 방문 포인트 (100자 이상)")
    tip: Optional[str] = Field(default=None, description="방문 꿀팁 (예: 일몰 30분 전 방문 추천, 예약 필수 등)")
    image_url: Optional[str] = Field(default=None, description="명소 실시간 고화질 사진 URL")
    image_caption: Optional[str] = Field(default=None, description="사진 캡션/출처 안내")


class TravelItineraryDay(BaseModel):
    """Daily travel itinerary schedule."""
    day: int = Field(description="일차 (예: 1, 2, 3)")
    theme: str = Field(description="해당 일자 테마 (예: 1일차: 핵심 랜드마크와 야경 투어)")
    schedule: List[str] = Field(default_factory=list, description="시간대별/순서별 방문 코스 (오전-점심-오후-저녁-야간)")
    tip: Optional[str] = Field(default=None, description="동선 이동 및 교통 팁")


class TravelArticleOutput(BaseModel):
    """Structured output schema for Travel destination guides and itineraries."""
    title: str = Field(description="여행 가이드 기사 제목 (Korean, 20~55자, 도시명/기간 및 핵심 매력 포함)")
    slug_hint: str = Field(description="URL 슬러그 힌트 (영문/한글 하이픈 형식)")
    excerpt: str = Field(description="글 요약/발췌문 (Korean, 80~150자)")
    hero_image_url: Optional[str] = Field(default=None, description="글 상단 대표 커버 사진 URL")
    introduction: str = Field(description="도입부 (여행지 개요, 왜 지금 가야 하는지, 매력 포인트, 200자 이상)")
    destination_overview: str = Field(description="도시/지역 기본 개요 (비행시간, 시차, 최적 여행시기, 150자 이상)")
    weather_and_clothing: str = Field(description="날씨 및 옷차림 가이드 (월별 기온 특성, 챙겨야 할 의류 및 준비물, 150자 이상)")
    exchange_and_budget: str = Field(description="환율, 화폐 및 1인 예상 경비 가이드 (항공, 숙박, 식비, 일일 경비 breakdown, 150자 이상)")
    itinerary_days: List[TravelItineraryDay] = Field(default_factory=list, description="추천 2박3일 또는 3박4일 상세 일정 코스")
    must_visit_spots: List[TravelSpotItem] = Field(default_factory=list, description="반드시 가봐야 할 핵심 명소 및 맛집 4~6곳")
    transport_tips: str = Field(description="현지 대중교통 및 필수 교통패스 가이드 (지하철, 버스, 패스권 추천, 150자 이상)")
    travel_tips: List[str] = Field(default_factory=list, description="현지 여행 시 유용한 꿀팁 및 주의사항 (치안, 팁문화, 전압 등 3~5가지)")
    faq: List[FAQItem] = Field(default_factory=list, description="여행자들이 가장 궁금해하는 질문 3~4개")
    conclusion: str = Field(description="마무리 총평 및 여행 권유 (150자 이상)")
    seo_title: str = Field(description="SEO 검색 최적화 제목 (30~55자)")
    meta_description: str = Field(description="검색엔진 메타 설명문 (100~160자)")
    tags: List[str] = Field(default_factory=list, description="워드프레스 태그 목록 (최대 8개)")


class NewsArticleOutput(BaseModel):
    """Structured output schema for Factual News & Fact-check Briefings."""
    title: str = Field(description="뉴스 기사 제목 (Korean, 20~55자, 핵심 사안 및 파급효과 포함)")
    slug_hint: str = Field(description="URL 슬러그 힌트 (영문/한글 하이픈 형식)")
    excerpt: str = Field(description="글 요약/발췌문 (Korean, 80~150자)")
    introduction: str = Field(description="도입부 (주요 뉴스 개요 및 보도 배경, 200자 이상)")
    quick_summary_points: List[str] = Field(default_factory=list, description="3줄 핵심 요약 포인트")
    timeline_events: List[str] = Field(default_factory=list, description="주요 경과 및 정책 발표 타임라인 (3~4단계)")
    key_facts: str = Field(description="확인된 공식 팩트 및 데이터 분석 (200자 이상)")
    expert_analysis: Optional[str] = Field(default=None, description="전문가 및 시장의 심층 분석 및 시사점 (150자 이상)")
    public_and_market_impact: str = Field(description="국민 실생활 및 경제/시장에 미치는 실질적 영향 (150자 이상)")
    faq: List[FAQItem] = Field(default_factory=list, description="독자들이 가장 궁금해하는 핵심 질문 2~3개")
    conclusion: str = Field(description="에디터 총평 및 향후 관전 포인트 (150자 이상)")
    seo_title: str = Field(description="SEO 검색 최적화 제목 (30~55자)")
    meta_description: str = Field(description="검색엔진 메타 설명문 (100~160자)")
    tags: List[str] = Field(default_factory=list, description="워드프레스 태그 목록 (최대 8개)")


class GenerationResult(BaseModel):
    """Metadata and content returned from an article generation request."""
    success: bool
    article: Optional[Any] = None
    requested_provider: str
    used_provider: Optional[str] = None
    fallback_used: bool = False
    attempts: int = 1
    prompt_version: str = "v1.0"
    latency_ms: float = 0.0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    error_message: Optional[str] = None
    failure_category: Optional[str] = None

