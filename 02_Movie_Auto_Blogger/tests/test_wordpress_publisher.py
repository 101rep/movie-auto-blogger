"""Unit tests for WordPress REST API publisher, media upload, and idempotency protection."""
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from sqlalchemy.orm import Session

from app.database.models import Movie, Post, PostStatusEnum
from app.publishers.base import PostStatus, PublishRequest
from app.publishers.wordpress import WordPressPublisher
from app.services.publishing_service import PublishingService


@pytest.mark.asyncio
async def test_wordpress_health_check_missing_config():
    """Verify health check diagnoses missing site URL or credentials."""
    publisher = WordPressPublisher(site_url="", username="", app_password="")
    res = await publisher.health_check()
    assert res["success"] is False
    assert "누락되었습니다" in res["message"]


@pytest.mark.asyncio
async def test_wordpress_health_check_unauthorized():
    """Verify health check diagnoses 401 unauthorized."""
    publisher = WordPressPublisher(
        site_url="https://myblog.com",
        username="admin",
        app_password="wrong_password"
    )

    mock_resp = httpx.Response(status_code=401, json={"code": "jwt_auth_invalid_token", "message": "Invalid token"})
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await publisher.health_check()
        assert res["success"] is False
        assert "인증 실패" in res["message"]


@pytest.mark.asyncio
async def test_wordpress_health_check_success():
    """Verify health check succeeds with 200 OK from /users/me."""
    publisher = WordPressPublisher(
        site_url="https://myblog.com",
        username="editor",
        app_password="valid_password"
    )

    mock_resp = httpx.Response(status_code=200, json={"id": 1, "name": "에디터", "slug": "editor"})
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await publisher.health_check()
        assert res["success"] is True
        assert "에디터" in res["message"]


@pytest.mark.asyncio
async def test_category_and_tag_reuse():
    """Verify existing categories and tags are reused without redundant creation."""
    publisher = WordPressPublisher(
        site_url="https://myblog.com",
        username="editor",
        app_password="password"
    )

    # Mock search returning existing category ID 12
    existing_cat = [{"id": 12, "name": "애니메이션"}]
    mock_resp = httpx.Response(status_code=200, json=existing_cat)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        cat_id = await publisher.get_or_create_category("애니메이션")
        assert cat_id == 12

    # Verify cached on second call
    cat_id_cached = await publisher.get_or_create_category("애니메이션")
    assert cat_id_cached == 12


@pytest.mark.asyncio
async def test_publish_post_draft_creation():
    """Verify draft post is created with correct payload."""
    publisher = WordPressPublisher(
        site_url="https://myblog.com",
        username="editor",
        app_password="password"
    )

    req = PublishRequest(
        title="테스트 영화 글",
        content="<p>본문 내용입니다.</p>",
        excerpt="요약문입니다.",
        slug="test-movie-post",
        status=PostStatus.DRAFT,
        categories=["애니메이션"],
        tags=["픽사"]
    )

    # Mock slug search (no existing post)
    async def mock_get(url, *args, **kwargs):
        if "posts" in str(url):
            return httpx.Response(status_code=200, json=[])
        return httpx.Response(status_code=200, json=[])

    async def mock_post(url, *args, **kwargs):
        # Return created post
        return httpx.Response(
            status_code=201,
            json={"id": 105, "link": "https://myblog.com/?p=105", "status": "draft"}
        )

    with patch("httpx.AsyncClient.get", side_effect=mock_get), \
         patch("httpx.AsyncClient.post", side_effect=mock_post):
        res = await publisher.publish_post(req)

        assert res.success is True
        assert res.remote_post_id == 105
        assert res.remote_status == "draft"


@pytest.mark.asyncio
async def test_publish_post_future_scheduled():
    """Verify future post includes date_gmt in payload."""
    publisher = WordPressPublisher(
        site_url="https://myblog.com",
        username="editor",
        app_password="password"
    )

    scheduled_iso = "2026-09-14T08:00:00Z"
    req = PublishRequest(
        title="예약 게시글",
        content="<p>내용</p>",
        slug="scheduled-post",
        status=PostStatus.FUTURE,
        scheduled_at=scheduled_iso
    )

    posted_payload = {}

    async def mock_post(url, *args, **kwargs):
        nonlocal posted_payload
        if "json" in kwargs:
            posted_payload = kwargs["json"]
        return httpx.Response(status_code=201, json={"id": 200, "link": "https://myblog.com/?p=200", "status": "future"})

    with patch("httpx.AsyncClient.get", return_value=httpx.Response(status_code=200, json=[])), \
         patch("httpx.AsyncClient.post", side_effect=mock_post):
        res = await publisher.publish_post(req)

        assert res.success is True
        assert res.remote_post_id == 200
        assert posted_payload.get("status") == "future"
        assert posted_payload.get("date_gmt") == scheduled_iso


@pytest.mark.asyncio
async def test_idempotency_protection_updates_existing_post():
    """Verify retry with existing slug updates existing post rather than creating duplicate."""
    publisher = WordPressPublisher(
        site_url="https://myblog.com",
        username="editor",
        app_password="password"
    )

    req = PublishRequest(
        title="중복 방지 영화 글",
        content="<p>수정된 본문</p>",
        slug="existing-unique-slug",
        status=PostStatus.DRAFT
    )

    # Mock slug search returning existing post ID 999
    existing_post = [{"id": 999, "slug": "existing-unique-slug"}]

    target_url_called = ""

    async def mock_get(url, *args, **kwargs):
        return httpx.Response(status_code=200, json=existing_post)

    async def mock_post(url, *args, **kwargs):
        nonlocal target_url_called
        target_url_called = str(url)
        return httpx.Response(status_code=200, json={"id": 999, "link": "https://myblog.com/?p=999", "status": "draft"})

    with patch("httpx.AsyncClient.get", side_effect=mock_get), \
         patch("httpx.AsyncClient.post", side_effect=mock_post):
        res = await publisher.publish_post(req)

        assert res.success is True
        assert res.remote_post_id == 999
        # Verified that POST was sent to /posts/999 (UPDATE) rather than /posts (INSERT)
        assert target_url_called.endswith("/posts/999")


@pytest.mark.asyncio
async def test_publishing_service_coordinates_post_and_persists_id(db_session: Session):
    """Verify PublishingService updates DB Post record with returned remote ID and status."""
    movie = Movie(
        source="tmdb",
        external_id="555",
        title="코디네이터 테스트 영화",
        genres_json=json.dumps(["SF", "액션"], ensure_ascii=False)
    )
    db_session.add(movie)
    db_session.commit()

    post = Post(
        movie_id=movie.id,
        title="코디네이터 테스트 글",
        slug="coordinator-test-slug",
        rendered_content="<p>테스트 본문</p>",
        excerpt="요약문",
        status=PostStatusEnum.GENERATED.value
    )
    db_session.add(post)
    db_session.commit()

    publisher = WordPressPublisher(site_url="https://myblog.com", username="admin", app_password="pw")

    async def mock_post(url, *args, **kwargs):
        return httpx.Response(status_code=201, json={"id": 777, "link": "https://myblog.com/777", "status": "draft"})

    with patch("httpx.AsyncClient.get", return_value=httpx.Response(status_code=200, json=[])), \
         patch("httpx.AsyncClient.post", side_effect=mock_post):
        pub_service = PublishingService(publisher=publisher)
        result = await pub_service.publish_article(db_session, post, target_status=PostStatus.DRAFT)

        assert result.success is True
        assert result.remote_post_id == 777

        # Verify DB Post updated
        db_session.refresh(post)
        assert post.wordpress_post_id == 777
        assert post.wordpress_url == "https://myblog.com/777"
        assert post.status == PostStatusEnum.APPROVED.value
