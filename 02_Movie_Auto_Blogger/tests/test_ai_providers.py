"""Unit tests for OpenAI, Gemini, and AIProviderRouter with mocked responses."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.base import BaseArticleWriter
from app.ai.openai_provider import OpenAIArticleProvider
from app.ai.gemini_provider import GeminiArticleProvider
from app.ai.router import AIProviderRouter
from app.ai.schemas import ArticleOutput, FAQItem, GenerationResult


def create_sample_article() -> ArticleOutput:
    """Create a realistic sample ArticleOutput for testing."""
    return ArticleOutput(
        title="영화 인사이드 아웃 2 줄거리 및 출연진 개봉일 총정리",
        slug_hint="inside-out-2-review",
        excerpt="13살이 된 라일리의 감정 컨트롤 본부에 불안, 당황, 부럽, 따분 등 새로운 감정들이 찾아오면서 펼쳐지는 따뜻한 성장 이야기입니다.",
        introduction="디즈니 픽사의 레전드 애니메이션 인사이드 아웃이 한층 더 성숙해진 사춘기 라일리의 이야기로 우리 곁에 돌아왔습니다. 누구나 겪었던 유년기와 사춘기의 감정 변화를 유쾌하고 깊이 있게 그려냅니다.",
        basic_info_summary="켈시 만 감독 연출, 에이미 포일러, 마야 호크 등이 목소리 연기를 펼친 디즈니 픽사의 2024년 대표 애니메이션 영화입니다.",
        theme_symbolism="새로운 감정 '불안이'는 현대인이 마주하는 미래에 대한 통제 욕구와 불확실성을 상징하며, 진정한 자아 성장은 모든 감정을 포용하는 데서 시작된다는 은유를 담고 있습니다.",
        spoiler_free_synopsis="고등학교 진학을 앞둔 라일리는 절친들과 함께 하키 캠프에 참가하게 됩니다. 하지만 갑작스러운 사춘기 경보와 함께 감정 본부에 불안이, 당황이, 부럽이, 따분이가 찾아오며 기존의 기쁨이 일행과 대립하게 됩니다.",
        cast_and_director="신예 켈시 만 감독의 섬세한 연출과 불안이 역을 완벽히 소화한 마야 호크의 몰입감 넘치는 목소리 연기가 돋보입니다.",
        character_dynamics="기존 감정 컨트롤 본부를 이끌던 '기쁨이'와 새로운 리더로 나선 '불안이' 간의 주도권 경쟁은 자아 형성 과정에서 겪는 혼란과 조화를 입체적으로 보여줍니다.",
        viewing_points=[
            "새롭게 합류한 사춘기 감정 캐릭터들의 개성 넘치는 매력",
            "청소년기 자아 형성의 고뇌를 시각화한 감동적인 스토리텔링",
            "남녀노소 모두의 공감을 자아내는 따뜻한 픽사 특유의 메시지"
        ],
        recommended_for=[
            "성장통과 불안을 겪어본 모든 성인 관객",
            "자녀와 함께 깊은 이야기를 나누고 싶은 가족 관객",
            "픽사 애니메이션 특유의 감동을 사랑하는 팬"
        ],
        spoiler_deep_dive="후반부 라일리의 불안 발작 시퀀스는 완벽해지려는 강박을 내려놓고 불완전한 자신을 인정하는 순간 평온을 되찾는 깊은 카타르시스를 선사합니다.",
        similar_movie_notes=[
            "인사이드 아웃 1편: 감정 세계의 탄생과 어린 시절 라일리의 이야기",
            "소울(Soul): 인생의 의미와 불꽃을 찾아가는 어른들을 위한 애니메이션"
        ],
        faq=[
            FAQItem(question="쿠키 영상이 존재하나요?", answer="엔딩 크레딧 이후 짧은 쿠키 영상이 포함되어 있습니다."),
            FAQItem(question="1편을 보지 않아도 이해할 수 있나요?", answer="단독 관람도 충분히 재미있지만 1편을 먼저 보시면 감동이 두 배가 됩니다.")
        ],
        conclusion="인사이드 아웃 2는 단순한 애니메이션을 넘어, 우리 마음속의 모든 감정이 소중함을 일깨워주는 위로와 치유의 명작입니다.",
        engagement_question="여러분은 사춘기 시절 어떤 감정이 마음속 본부를 가장 크게 지배했었나요? 댓글로 나눠주세요!",
        seo_title="인사이드 아웃 2 줄거리와 결말 포인트 총정리",
        meta_description="인사이드 아웃 2의 새로운 감정 캐릭터들과 스포일러 없는 줄거리, 관람 포인트를 알기 쉽게 정리해 드립니다.",
        tags=["인사이드아웃2", "디즈니픽사", "애니메이션영화", "영화추천"],
        factual_warnings=[]
    )


class MockProvider(BaseArticleWriter):
    """Controllable mock writer for router tests."""

    def __init__(self, name: str, should_succeed: bool = True, return_article: ArticleOutput = None):
        self.name = name
        self.should_succeed = should_succeed
        self.return_article = return_article or create_sample_article()

    async def health_check(self):
        return {"success": self.should_succeed, "message": f"{self.name} Mock Status"}

    async def generate_article(self, movie_data, prompt_version="v1.0", additional_instruction=None):
        if self.should_succeed:
            return GenerationResult(
                success=True,
                article=self.return_article,
                requested_provider=self.name,
                used_provider=self.name,
                prompt_tokens=150,
                completion_tokens=400,
                total_tokens=550,
                latency_ms=120.0
            )
        return GenerationResult(
            success=False,
            requested_provider=self.name,
            used_provider=self.name,
            error_message=f"{self.name} API Timeout",
            failure_category="TIMEOUT"
        )


@pytest.mark.asyncio
async def test_openai_provider_missing_key():
    """Verify OpenAI provider gracefully handles missing API key."""
    provider = OpenAIArticleProvider(api_key="")
    health = await provider.health_check()
    assert health["success"] is False

    result = await provider.generate_article({"title": "기생충"})
    assert result.success is False
    assert result.failure_category == "MISSING_CREDENTIALS"


@pytest.mark.asyncio
async def test_gemini_provider_missing_key():
    """Verify Gemini provider gracefully handles missing API key."""
    provider = GeminiArticleProvider(api_key="")
    health = await provider.health_check()
    assert health["success"] is False

    result = await provider.generate_article({"title": "기생충"})
    assert result.success is False
    assert result.failure_category == "MISSING_CREDENTIALS"


@pytest.mark.asyncio
async def test_router_primary_openai_success():
    """Scenario 1: Primary (OpenAI) succeeds without calling fallback."""
    openai_mock = MockProvider("openai", should_succeed=True)
    gemini_mock = MockProvider("gemini", should_succeed=True)

    router = AIProviderRouter(
        openai_provider=openai_mock,
        gemini_provider=gemini_mock,
        primary="openai",
        fallback="gemini"
    )

    result = await router.generate_article({"title": "인사이드 아웃 2"})

    assert result.success is True
    assert result.used_provider == "openai"
    assert result.fallback_used is False
    assert result.article is not None


@pytest.mark.asyncio
async def test_router_primary_fails_fallback_gemini_succeeds():
    """Scenario 2: Primary (OpenAI) fails -> Fallback (Gemini) succeeds."""
    openai_mock = MockProvider("openai", should_succeed=False)
    gemini_mock = MockProvider("gemini", should_succeed=True)

    router = AIProviderRouter(
        openai_provider=openai_mock,
        gemini_provider=gemini_mock,
        primary="openai",
        fallback="gemini"
    )

    result = await router.generate_article({"title": "인사이드 아웃 2"})

    assert result.success is True
    assert result.used_provider == "gemini"
    assert result.fallback_used is True
    assert result.attempts == 2


@pytest.mark.asyncio
async def test_router_primary_gemini_fails_fallback_openai_succeeds():
    """Scenario 3 & 4: Reversed priority (Gemini primary fails -> OpenAI fallback succeeds)."""
    openai_mock = MockProvider("openai", should_succeed=True)
    gemini_mock = MockProvider("gemini", should_succeed=False)

    router = AIProviderRouter(
        openai_provider=openai_mock,
        gemini_provider=gemini_mock,
        primary="gemini",
        fallback="openai"
    )

    result = await router.generate_article({"title": "인사이드 아웃 2"})

    assert result.success is True
    assert result.used_provider == "openai"
    assert result.fallback_used is True


@pytest.mark.asyncio
async def test_router_both_providers_fail():
    """Scenario 5: Both providers fail -> returns failure with failure_category."""
    openai_mock = MockProvider("openai", should_succeed=False)
    gemini_mock = MockProvider("gemini", should_succeed=False)

    router = AIProviderRouter(
        openai_provider=openai_mock,
        gemini_provider=gemini_mock,
        primary="openai",
        fallback="gemini"
    )

    result = await router.generate_article({"title": "인사이드 아웃 2"})

    assert result.success is False
    assert result.failure_category == "ALL_PROVIDERS_FAILED"
    assert "both failed" in result.error_message
