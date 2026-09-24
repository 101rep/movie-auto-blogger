"""Comprehensive Phase 8 tests for WordPress integration, settings synchronization, and trailer preservation."""
import json
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from sqlalchemy.orm import Session

from app.database.models import Movie, Post, PostStatusEnum
from app.publishers.base import PostStatus
from app.publishers.wordpress import WordPressPublisher
from app.services.publishing_service import PublishingService
from app.services.settings_service import SettingsService


@pytest.mark.asyncio
async def test_phase8_wordpress_health_check_unconfigured():
    """Verify health check returns informative error when WordPress is not configured."""
    publisher = WordPressPublisher(site_url="", username="", app_password="")
    res = await publisher.health_check()
    assert res["success"] is False
    assert "누락되었습니다" in res["message"]


@pytest.mark.asyncio
async def test_phase8_wordpress_health_check_success():
    """Verify health check returns success when credentials are valid."""
    publisher = WordPressPublisher(
        site_url="https://movie-blogger-test.com",
        username="wp_admin",
        app_password="test_password"
    )

    mock_user_data = {"id": 1, "name": "관리자", "slug": "admin"}
    mock_resp = httpx.Response(status_code=200, json=mock_user_data)
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await publisher.health_check()
        assert res["success"] is True
        assert "관리자" in res["message"]


def test_phase8_settings_service_wordpress_credentials(db_session: Session):
    """Verify SettingsService saves and retrieves WordPress connection parameters."""
    service = SettingsService()
    updates = {
        "wordpress_url": "https://my-cinema-blog.com",
        "wordpress_username": "blogger_master",
        "wordpress_app_password": "abcd 1234 efgh 5678",
    }
    updated = service.update_settings(db_session, updates)
    assert updated["wordpress_url"] == "https://my-cinema-blog.com"
    assert updated["wordpress_username"] == "blogger_master"
    assert updated["has_wordpress_app_password"] is True

    # Retrieve again from fresh call
    retrieved = service.get_all_settings(db_session)
    assert retrieved["wordpress_url"] == "https://my-cinema-blog.com"
    assert retrieved["wordpress_username"] == "blogger_master"
    assert retrieved["has_wordpress_app_password"] is True


@pytest.mark.asyncio
async def test_phase8_publishing_service_preserves_youtube_trailer(db_session: Session):
    """Verify PublishingService preserves YouTube trailer embed during internal linking re-render."""
    movie = Movie(
        source="tmdb",
        external_id="888999",
        title="트레일러 보존 테스트 영화",
        original_title="Trailer Preservation Test",
        genres_json=json.dumps(["액션", "SF"], ensure_ascii=False),
        overview="영화 개요입니다.",
        release_date="2026-05-01",
        runtime=125
    )
    db_session.add(movie)
    db_session.commit()

    article_data = {
        "title": "트레일러 보존 테스트 리뷰",
        "slug_hint": "trailer-preservation-test-review",
        "excerpt": "테스트 요약문입니다.",
        "introduction": "영화의 전반적 인상 및 소개 내용입니다.",
        "basic_info_summary": "영화 기본정보 요약 내용입니다.",
        "spoiler_free_synopsis": "스포일러 없는 줄거리 요약 세부 내용입니다.",
        "cast_and_director": "감독 및 주요 출연진 소개입니다.",
        "viewing_points": ["관람 포인트 1", "관람 포인트 2"],
        "conclusion": "마무리 감상 및 총평입니다.",
        "seo_title": "트레일러 보존 테스트 SEO 제목",
        "meta_description": "테스트 메타 설명문입니다.",
        "tags": ["액션", "SF", "트레일러"],
        "faq": []
    }

    post = Post(
        movie_id=movie.id,
        title="트레일러 보존 테스트 리뷰",
        slug="trailer-preservation-test-review",
        article_json=json.dumps(article_data, ensure_ascii=False),
        rendered_content="<p>초기 렌더링 본문</p>",
        meta_description="테스트 메타 설명",
        status=PostStatusEnum.GENERATED.value
    )
    db_session.add(post)
    db_session.commit()

    publisher = WordPressPublisher(
        site_url="https://my-cinema-blog.com",
        username="admin",
        app_password="test-password"
    )

    sent_payload = {}

    async def mock_post_call(url, *args, **kwargs):
        nonlocal sent_payload
        if "/posts" in str(url):
            sent_payload = kwargs.get("json", {})
            return httpx.Response(status_code=201, json={"id": 101, "link": "https://my-cinema-blog.com/?p=101", "status": "draft"})
        return httpx.Response(status_code=200, json={})

    mock_trailer = {
        "video_id": "dQw4w9WgXcQ",
        "title": "공식 예고편",
        "embed_url": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
        "watch_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "source": "tmdb"
    }

    with patch("httpx.AsyncClient.get", return_value=httpx.Response(status_code=200, json=[])), \
         patch("httpx.AsyncClient.post", side_effect=mock_post_call), \
         patch("app.services.trailer_service.TrailerService.get_trailer_info", new_callable=AsyncMock) as mock_get_trailer:
        mock_get_trailer.return_value = mock_trailer
        pub_service = PublishingService(publisher=publisher)
        result = await pub_service.publish_article(db_session, post, target_status=PostStatus.DRAFT)

        assert result.success is True
        assert result.remote_post_id == 101

        # Check that the YouTube trailer iframe/container was embedded in the content sent to WordPress
        content_sent = sent_payload.get("content", "")
        assert "youtube-trailer" in content_sent or "youtube-nocookie.com/embed/dQw4w9WgXcQ" in content_sent
        assert "dQw4w9WgXcQ" in content_sent
