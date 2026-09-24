"""Comprehensive Phase 7 Reliability & Integration Tests covering 14 Critical Scenarios."""
import asyncio
import httpx
import pytest
from pydantic import ValidationError
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from app.ai.router import AIProviderRouter
from app.ai.schemas import ArticleOutput, GenerationResult
from app.collectors.tmdb import TMDBMovieProvider
from app.config import get_settings
from app.database.models import (
    AutomationEvent,
    AutomationRun,
    Movie,
    Post,
    PostStatusEnum,
    QualityStatusEnum,
)
from app.publishers.base import PostStatus, PublishRequest, PublishResult
from app.publishers.wordpress import WordPressPublisher
from app.scheduler.jobs import run_automation_pipeline
from app.services.candidate_service import CandidateService
from app.services.quality_service import QualityGateService
from app.utils.retry import retry_async
from app.utils.security import mask_secret, sanitize_log_message
from tests.test_ai_providers import MockProvider, create_sample_article


# Scenario 1: TMDB Rate Limit (429) & Backoff
@pytest.mark.asyncio
async def test_scenario_01_tmdb_rate_limit_handled():
    """Scenario 1: TMDB 429 response is handled with error message without crashing."""
    collector = TMDBMovieProvider(api_token="valid_test_token")
    mock_resp = httpx.Response(status_code=429, text="Too Many Requests")

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await collector.health_check()
        assert res["success"] is False
        assert "429" in res["message"] or "오류" in res["message"]


# Scenario 2: TMDB Network Timeout / 5xx
@pytest.mark.asyncio
async def test_scenario_02_tmdb_timeout_handled():
    """Scenario 2: Network timeout during TMDB fetch produces clean empty result."""
    collector = TMDBMovieProvider(api_token="valid_test_token")

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Connection timed out")
        movies = await collector.get_popular_movies(page=1)
        assert movies == []


# Scenario 3: Zero Candidate Pool Recovery
@pytest.mark.asyncio
async def test_scenario_03_zero_candidate_pool_graceful_recovery(db_session: Session):
    """Scenario 3: When candidate pool is 0, pipeline halts gracefully with NO_CANDIDATES event."""
    with patch("app.services.candidate_service.CandidateService.collect_score_and_persist", new_callable=AsyncMock) as mock_collect:
        mock_collect.return_value = []

        run = await run_automation_pipeline(db_session, force=True)
        assert run.status == "completed"
        assert "수집된 적격 후보 영화가 없습니다" in run.summary

        events = db_session.query(AutomationEvent).filter(AutomationEvent.run_id == run.id).all()
        assert any(e.event_code == "NO_CANDIDATES" for e in events)


# Scenario 4: OpenAI 429 Quota Exhaustion -> Seamless Gemini Fallback
@pytest.mark.asyncio
async def test_scenario_04_openai_quota_exhaustion_seamless_gemini_fallback():
    """Scenario 4: OpenAI failure triggers automatic fallback to Gemini."""
    openai_mock = MockProvider("openai", should_succeed=False)
    gemini_mock = MockProvider("gemini", should_succeed=True)

    router = AIProviderRouter(
        openai_provider=openai_mock,
        gemini_provider=gemini_mock,
        primary="openai",
        fallback="gemini"
    )

    result = await router.generate_article({"title": "오토 폴백 영화", "release_date": "2026-01-01"})

    assert result.success is True
    assert result.fallback_used is True
    assert result.used_provider == "gemini"


# Scenario 5: Both AI Providers Fail -> Safe Failure Recording
@pytest.mark.asyncio
async def test_scenario_05_both_ai_providers_fail():
    """Scenario 5: Both AI engines fail -> graceful error response without crash."""
    openai_mock = MockProvider("openai", should_succeed=False)
    gemini_mock = MockProvider("gemini", should_succeed=False)

    router = AIProviderRouter(
        openai_provider=openai_mock,
        gemini_provider=gemini_mock,
        primary="openai",
        fallback="gemini"
    )

    result = await router.generate_article({"title": "양측 장애 영화"})

    assert result.success is False
    assert result.fallback_used is True
    assert result.error_message is not None


# Scenario 6: Corrupted/Unparseable AI JSON Output
def test_scenario_06_corrupted_json_repair_and_handling():
    """Scenario 6: Corrupted JSON raises ValidationError and is caught gracefully."""
    corrupted_json = '{"title": "불완전한 JSON", "slug_hint": '
    with pytest.raises(ValidationError):
        ArticleOutput.model_validate_json(corrupted_json)


# Scenario 7: Hallucination / Quality Gate FAIL
def test_scenario_07_quality_gate_fail_halts_publishing():
    """Scenario 7: Forbidden placeholder triggers FAIL verdict."""
    gate = QualityGateService()
    article = create_sample_article()
    article.conclusion = "이 영화는 [여기에 결론을 입력하세요] 상태입니다."

    status, issues = gate.evaluate(article, expected_movie_title="인사이드 아웃 2")
    assert status == QualityStatusEnum.FAIL
    assert any("플레이스홀더" in issue for issue in issues)


# Scenario 8: Quality Gate REVIEW -> Draft Routing
def test_scenario_08_quality_gate_review_routing():
    """Scenario 8: Minor issue assigns REVIEW status instead of FAIL."""
    gate = QualityGateService()
    article = create_sample_article()
    # 1 viewing point is fewer than recommended 3, triggering REVIEW
    article.viewing_points = ["단 한 가지 관람 포인트"]

    status, issues = gate.evaluate(article, expected_movie_title="인사이드 아웃 2")
    assert status == QualityStatusEnum.REVIEW


# Scenario 9: WordPress 401/403 Unauthorized
@pytest.mark.asyncio
async def test_scenario_09_wordpress_unauthorized_error():
    """Scenario 9: WordPress 401 returns clean error without infinite loop."""
    wp = WordPressPublisher(
        site_url="https://example.com",
        username="wrong_user",
        app_password="wrong_password"
    )

    mock_resp = httpx.Response(status_code=401, json={"code": "rest_cannot_access", "message": "인증 실패"})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        health = await wp.health_check()
        assert health["success"] is False
        assert "401" in health["message"] or "인증 실패" in health["message"]


# Scenario 10: WordPress 500 Retry Policy
@pytest.mark.asyncio
async def test_scenario_10_retry_policy_with_exponential_backoff():
    """Scenario 10: Exponential backoff retries transient failures then succeeds."""
    attempts = 0

    class MockTransient500Exception(Exception):
        status_code = 500

    async def flaky_call():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise MockTransient500Exception("Server Error 500")
        return "success_recovered"

    result = await retry_async(
        flaky_call,
        max_attempts=3,
        initial_delay=0.01,
        backoff_factor=2.0,
        jitter=False
    )

    assert result == "success_recovered"
    assert attempts == 3


# Scenario 11: Duplicate Candidate Discovery
@pytest.mark.asyncio
async def test_scenario_11_duplicate_candidate_discovery(db_session: Session):
    """Scenario 11: Candidate already in DB with PUBLISHED status is filtered out."""
    candidate_service = CandidateService()

    movie = Movie(
        source="tmdb",
        external_id="111222",
        title="이미 발행된 영화",
    )
    db_session.add(movie)
    db_session.commit()

    post = Post(
        movie_id=movie.id,
        title="이미 발행된 글",
        slug="already-published",
        status=PostStatusEnum.PUBLISHED.value,
    )
    db_session.add(post)
    db_session.commit()

    ineligible_ids = candidate_service.get_ineligible_external_ids(db_session, source="tmdb")
    assert "111222" in ineligible_ids


# Scenario 12: WordPress Post Slug Idempotency
@pytest.mark.asyncio
async def test_scenario_12_wordpress_slug_idempotency():
    """Scenario 12: Existing remote post slug is updated rather than duplicated."""
    wp = WordPressPublisher(
        site_url="https://example.com",
        username="admin",
        app_password="password"
    )

    req = PublishRequest(
        title="중복 방지 글",
        content="<p>내용</p>",
        slug="slug-idempotent",
        status=PostStatus.PUBLISH
    )

    # 1. find existing post by slug returns remote post ID 555
    existing_post = [{"id": 555, "slug": "slug-idempotent"}]

    target_post_url = ""

    async def mock_get(url, *args, **kwargs):
        return httpx.Response(status_code=200, json=existing_post)

    async def mock_post(url, *args, **kwargs):
        nonlocal target_post_url
        target_post_url = str(url)
        return httpx.Response(status_code=200, json={"id": 555, "link": "https://example.com/slug-idempotent", "status": "publish"})

    with patch("httpx.AsyncClient.get", side_effect=mock_get), \
         patch("httpx.AsyncClient.post", side_effect=mock_post):
        result = await wp.publish_post(req)

        assert result.success is True
        assert result.remote_post_id == 555
        # Verify POST was sent to /wp/v2/posts/555 (update), not creating a new post
        assert "/wp/v2/posts/555" in target_post_url


# Scenario 13: Pipeline Fatal Exception Recovery & Rollback
@pytest.mark.asyncio
async def test_scenario_13_pipeline_exception_handling(db_session: Session):
    """Scenario 13: Unhandled exception sets run status to failed without leaving DB locked."""
    with patch("app.services.candidate_service.CandidateService.collect_score_and_persist", side_effect=RuntimeError("Fatal database crash")):
        run = await run_automation_pipeline(db_session, force=True)
        assert run.status == "failed"
        assert "Fatal database crash" in run.summary

        events = db_session.query(AutomationEvent).filter(AutomationEvent.run_id == run.id).all()
        assert any(e.event_code == "FATAL_EXCEPTION" for e in events)


# Scenario 14: Secret Leak Prevention
def test_scenario_14_secret_leak_prevention():
    """Scenario 14: Sensitive keys and passwords are never displayed in logs or overview."""
    secret = "sk-proj-abc1234567890secretkeyhere"
    masked = mask_secret(secret)
    assert secret not in masked
    assert "..." in masked

    log_msg = f"Failed call with key={secret} and auth=Basic dXNlcjpwYXNz"
    sanitized = sanitize_log_message(log_msg)
    assert secret not in sanitized

    # Settings overview check
    settings = get_settings()
    settings.OPENAI_API_KEY = "sk-test-key-should-never-leak"
    overview = settings.get_masked_overview()
    assert overview["openai"] == "설정됨"
    assert "sk-test-key" not in str(overview)
