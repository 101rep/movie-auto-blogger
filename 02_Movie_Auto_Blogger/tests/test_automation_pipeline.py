"""Tests for Phase 5 & 6: Automation Pipeline, Scheduling, and Admin UI."""
from datetime import datetime, time as dtime
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from starlette.testclient import TestClient
from zoneinfo import ZoneInfo

from app.ai.schemas import ArticleOutput, FAQItem, GenerationResult
from app.config import get_settings
from app.database.models import (
    AdminUser,
    AutomationEvent,
    AutomationRun,
    Movie,
    Post,
    PostStatusEnum,
    QualityStatusEnum,
)
from app.publishers.base import PostStatus, PublishResult
from app.scheduler.jobs import (
    calculate_schedule_datetimes,
    parse_kst_time,
    run_automation_pipeline,
)
from app.services.settings_service import SettingsService
from app.utils.security import hash_password
from tests.test_ai_providers import create_sample_article


def test_parse_kst_time_and_schedule_calculation():
    """Verify parsing and calculation of future schedule dates in KST."""
    t1 = parse_kst_time("08:30")
    assert t1.hour == 8
    assert t1.minute == 30

    invalid_t = parse_kst_time("invalid")
    assert invalid_t.hour == 8

    # Calculate schedule datetimes for Asia/Seoul (4 slots)
    dates = calculate_schedule_datetimes("08:00", "12:30", "18:00", "22:00", tz_str="Asia/Seoul", post_count=4)
    assert len(dates) == 4
    assert dates[0].tzinfo == ZoneInfo("Asia/Seoul")
    assert dates[0].hour == 8
    assert dates[1].hour == 12
    assert dates[1].minute == 30
    assert dates[2].hour == 18
    assert dates[3].hour == 22

    # Check that scheduled datetime is in the future
    now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
    for dt in dates:
        assert dt > now_kst


@pytest.mark.asyncio
async def test_automation_pipeline_killswitch_inactive(db_session):
    """When AUTO_PUBLISH is false and force=False, the pipeline halts safely."""
    settings = get_settings()
    settings.AUTO_PUBLISH = False

    run = await run_automation_pipeline(db_session, force=False)

    assert run.status == "completed"
    assert "비활성화" in run.summary
    assert run.generated_count == 0
    assert run.scheduled_count == 0

    # Verify event logged
    events = db_session.query(AutomationEvent).filter(AutomationEvent.run_id == run.id).all()
    event_codes = [e.event_code for e in events]
    assert "AUTOMATION_DISABLED" in event_codes


@pytest.mark.asyncio
async def test_automation_pipeline_full_execution_mocked(db_session):
    """End-to-end automated pipeline: discovery -> enrichment -> AI -> Quality -> WP schedule."""
    settings = get_settings()
    settings.AUTO_PUBLISH = True
    settings.DAILY_POST_COUNT = 1

    # 1. Create a candidate movie in DB
    movie = Movie(
        source="tmdb",
        external_id="99001",
        title="파이프라인 테스트 영화",
        original_title="Pipeline Test Movie",
        release_date="2026-05-10",
        popularity=85.0,
        vote_average=8.2,
        candidate_score=92.5,
        overview="자동화 파이프라인 검증용 줄거리입니다.",
    )
    db_session.add(movie)
    db_session.commit()
    db_session.refresh(movie)

    mock_article = create_sample_article()

    mock_gen_result = GenerationResult(
        success=True,
        article=mock_article,
        requested_provider="openai",
        used_provider="openai",
        used_model="gpt-4o-mini",
        prompt_version="v1.0",
    )

    mock_pub_result = PublishResult(
        success=True,
        remote_post_id=777,
        remote_url="https://movie-blog.example.com/pipeline-test/",
        status=PostStatus.FUTURE,
    )

    with patch("app.services.candidate_service.CandidateService.collect_score_and_persist", new_callable=AsyncMock) as mock_collect, \
         patch("app.services.movie_service.MovieService.enrich_movie_details", new_callable=AsyncMock) as mock_enrich, \
         patch("app.services.article_service.ArticleService.generate_article_for_movie", new_callable=AsyncMock) as mock_gen, \
         patch("app.services.publishing_service.PublishingService.publish_article", new_callable=AsyncMock) as mock_pub:

        mock_collect.return_value = [movie]
        mock_enrich.return_value = movie

        # Post created during article service call
        post = Post(
            movie_id=movie.id,
            title="파이프라인 영화 상세 리뷰",
            slug="pipeline-test-movie",
            rendered_content="<p>테스트 본문</p>",
            status=PostStatusEnum.GENERATED.value,
            quality_status=QualityStatusEnum.PASS.value,
        )
        db_session.add(post)
        db_session.commit()

        mock_gen.return_value = (post, mock_gen_result, QualityStatusEnum.PASS, [])
        mock_pub.return_value = mock_pub_result

        run = await run_automation_pipeline(db_session, force=True)

        assert run.status == "completed"
        assert run.generated_count == 1
        assert run.scheduled_count == 1
        assert run.failed_count == 0

        # Verify events
        events = db_session.query(AutomationEvent).filter(AutomationEvent.run_id == run.id).all()
        codes = [e.event_code for e in events]
        assert "RUN_STARTED" in codes
        assert "DISCOVERY_COMPLETED" in codes
        assert "GENERATION_SUCCESS" in codes
        assert "POST_SCHEDULED" in codes
        assert "RUN_COMPLETED" in codes


@pytest.mark.asyncio
async def test_automation_pipeline_review_routing(db_session):
    """When Quality Gate returns REVIEW, the post is saved as DRAFT on WordPress."""
    movie = Movie(
        source="tmdb",
        external_id="99002",
        title="검토 필요 영화",
        original_title="Review Needed Movie",
        release_date="2026-06-01",
        candidate_score=80.0,
    )
    db_session.add(movie)
    db_session.commit()

    mock_article = create_sample_article()

    mock_gen_result = GenerationResult(
        success=True,
        article=mock_article,
        requested_provider="gemini",
        used_provider="gemini",
        used_model="gemini-1.5-flash",
    )

    mock_pub_result = PublishResult(
        success=True,
        remote_post_id=888,
        remote_url="https://movie-blog.example.com/draft-888/",
        status=PostStatus.DRAFT,
    )

    with patch("app.services.candidate_service.CandidateService.collect_score_and_persist", new_callable=AsyncMock) as mock_collect, \
         patch("app.services.movie_service.MovieService.enrich_movie_details", new_callable=AsyncMock) as mock_enrich, \
         patch("app.services.article_service.ArticleService.generate_article_for_movie", new_callable=AsyncMock) as mock_gen, \
         patch("app.services.publishing_service.PublishingService.publish_article", new_callable=AsyncMock) as mock_pub:

        mock_collect.return_value = [movie]
        mock_enrich.return_value = movie

        post = Post(
            movie_id=movie.id,
            title="검토 기사",
            slug="review-needed-movie",
            rendered_content="<p>검토 본문</p>",
            status=PostStatusEnum.GENERATED.value,
            quality_status=QualityStatusEnum.REVIEW.value,
        )
        db_session.add(post)
        db_session.commit()

        mock_gen.return_value = (post, mock_gen_result, QualityStatusEnum.REVIEW, ["공식 개봉 전 작품으로 정보 검토 권장"])
        mock_pub.return_value = mock_pub_result

        run = await run_automation_pipeline(db_session, force=True)

        assert run.status == "completed"
        # Should be saved as draft, not scheduled
        assert run.scheduled_count == 0

        # Verify SAVED_AS_DRAFT event
        events = db_session.query(AutomationEvent).filter(AutomationEvent.run_id == run.id).all()
        codes = [e.event_code for e in events]
        assert "SAVED_AS_DRAFT" in codes


def test_settings_service_read_and_update(db_session):
    """Verify SettingsService validation and persistence."""
    service = SettingsService()
    current = service.get_all_settings(db_session)
    assert "daily_post_count" in current
    assert "candidate_pool_size" in current

    # Update valid settings
    updated = service.update_settings(
        db_session,
        {
            "daily_post_count": 4,
            "candidate_pool_size": 25,
            "publish_time_1": "08:00",
            "publish_time_2": "12:30",
            "publish_time_3": "18:00",
            "publish_time_4": "22:00",
            "auto_publish": True,
            "primary_ai": "gemini",
            "fallback_ai": "openai",
        }
    )

    assert updated["daily_post_count"] == 4
    assert updated["candidate_pool_size"] == 25
    assert updated["publish_time_1"] == "08:00"
    assert updated["publish_time_2"] == "12:30"
    assert updated["publish_time_3"] == "18:00"
    assert updated["publish_time_4"] == "22:00"
    assert updated["auto_publish"] is True
    assert updated["primary_ai"] == "gemini"

    # Verify toggle
    new_state = service.toggle_auto_publish(db_session)
    assert new_state is False

    # Verify validation error on out-of-range post count
    with pytest.raises(ValueError):
        service.update_settings(db_session, {"daily_post_count": 15})

    # Verify validation error on invalid time format
    with pytest.raises(ValueError):
        service.update_settings(db_session, {"publish_time_1": "99:99"})


def test_admin_api_trigger_and_toggle(client, db_session):
    """Test authenticated admin endpoints for trigger-automation, toggle-automation, and settings."""
    # Ensure admin user
    user = db_session.query(AdminUser).filter(AdminUser.username == "admin").first()
    if not user:
        user = AdminUser(username="admin", hashed_password=hash_password("admin1234!"))
        db_session.add(user)
        db_session.commit()

    # Login
    login_res = client.post("/admin/login", data={"username": "admin", "password": "admin1234!"}, follow_redirects=False)
    assert login_res.status_code == 302

    # Toggle automation endpoint
    toggle_res = client.post("/admin/api/toggle-automation")
    assert toggle_res.status_code == 200
    toggle_data = toggle_res.json()
    assert toggle_data["success"] is True
    assert "auto_publish" in toggle_data

    # Trigger automation endpoint (mocked)
    with patch("app.admin.routes.run_automation_pipeline", new_callable=AsyncMock) as mock_run:
        mock_run_obj = MagicMock()
        mock_run_obj.status = "completed"
        mock_run_obj.run_uuid = "test-uuid-1234"
        mock_run_obj.summary = "완료 테스트"
        mock_run_obj.candidate_count = 5
        mock_run_obj.generated_count = 2
        mock_run_obj.scheduled_count = 2
        mock_run_obj.failed_count = 0
        mock_run.return_value = mock_run_obj

        trigger_res = client.post("/admin/api/trigger-automation")
        assert trigger_res.status_code == 200
        trigger_data = trigger_res.json()
        assert trigger_data["success"] is True
        assert trigger_data["run_uuid"] == "test-uuid-1234"

    # View runs page
    runs_res = client.get("/admin/runs")
    assert runs_res.status_code == 200
    assert "자동화 실행 이력" in runs_res.text

    # View settings page
    settings_res = client.get("/admin/settings")
    assert settings_res.status_code == 200
    assert "운영 환경설정" in settings_res.text

    # Submit settings form
    post_settings = client.post(
        "/admin/settings",
        data={
            "daily_post_count": 4,
            "candidate_pool_size": 20,
            "publish_time_1": "08:00",
            "publish_time_2": "12:30",
            "publish_time_3": "18:00",
            "publish_time_4": "22:00",
            "primary_ai": "openai",
            "fallback_ai": "gemini",
            "openai_model": "gpt-4o-mini",
            "gemini_model": "gemini-1.5-flash",
            "auto_publish": "true",
            "media_upload_enabled": "true",
        },
        follow_redirects=True,
    )
    assert post_settings.status_code == 200
    assert "설정이 성공적으로 저장되었습니다" in post_settings.text

    # View posts list page
    posts_res = client.get("/admin/posts")
    assert posts_res.status_code == 200
    assert "게시글 관리 및 검토" in posts_res.text

    # Create a test post for actions
    m = Movie(source="tmdb", external_id="88811", title="액션 테스트 영화")
    db_session.add(m)
    db_session.commit()

    p = Post(
        movie_id=m.id,
        title="액션 테스트 글",
        slug="action-test-post",
        rendered_content="<p>액션 테스트 본문</p>",
        status=PostStatusEnum.GENERATED.value,
        quality_status=QualityStatusEnum.PASS.value,
    )
    db_session.add(p)
    db_session.commit()

    # View preview page
    preview_res = client.get(f"/admin/posts/{p.id}/preview")
    assert preview_res.status_code == 200
    assert "액션 테스트 글" in preview_res.text

    # Publish now endpoint
    with patch("app.services.publishing_service.PublishingService.publish_article", new_callable=AsyncMock) as mock_pub:
        mock_pub.return_value = PublishResult(
            success=True,
            remote_post_id=999,
            remote_url="https://example.com/now",
            status=PostStatus.PUBLISH,
        )
        pub_res = client.post(f"/admin/api/publish-now/{p.id}")
        assert pub_res.status_code == 200
        assert pub_res.json()["success"] is True

    # Send draft endpoint
    with patch("app.services.publishing_service.PublishingService.publish_article", new_callable=AsyncMock) as mock_pub:
        mock_pub.return_value = PublishResult(
            success=True,
            remote_post_id=998,
            remote_url="https://example.com/draft",
            status=PostStatus.DRAFT,
        )
        draft_res = client.post(f"/admin/api/send-draft/{p.id}")
        assert draft_res.status_code == 200
        assert draft_res.json()["success"] is True

    # Delete post endpoint
    del_res = client.post(f"/admin/api/delete-post/{p.id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True


def test_scheduler_lifecycle_and_status():
    """Verify scheduler registers the daily 06:00 KST job and reports status."""
    from app.scheduler.scheduler import AutomationScheduler
    s = AutomationScheduler()
    s.start()

    status = s.get_status()
    assert status["is_running"] is True
    assert status["jobs_count"] >= 1
    job_ids = [j["id"] for j in status["jobs"]]
    assert "daily_movie_preparation" in job_ids

    s.shutdown()
    assert s.is_running is False

