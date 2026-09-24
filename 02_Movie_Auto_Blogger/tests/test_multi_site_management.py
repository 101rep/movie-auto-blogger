"""Unit and integration tests for Multi-Site registration, admin management, and publishing."""
from unittest.mock import AsyncMock, patch
import pytest
from starlette.testclient import TestClient

from app.database.models import AdminUser, Post, PostStatusEnum, Site
from app.database.session import SessionLocal
from app.main import app
from app.publishers.base import PostStatus, PublishResult
from app.services.publishing_service import PublishingService
from app.utils.security import hash_password


@pytest.fixture
def admin_client():
    """Client with authenticated admin session."""
    client = TestClient(app, follow_redirects=False)
    db = SessionLocal()
    try:
        user = db.query(AdminUser).filter(AdminUser.username == "testadmin_site").first()
        if not user:
            user = AdminUser(
                username="testadmin_site",
                hashed_password=hash_password("admin_pass123!"),
                is_active=True
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

    res = client.post(
        "/admin/login",
        data={"username": "testadmin_site", "password": "admin_pass123!"}
    )
    assert res.status_code == 302
    return client


def test_site_crud_in_admin(admin_client):
    """Verify admin can create, list, toggle, and delete a WordPress site."""
    # 1. List sites
    res = admin_client.get("/admin/sites")
    assert res.status_code == 200
    assert "멀티 사이트 & 버티컬 관리" in res.text

    # 2. Create site
    create_res = admin_client.post(
        "/admin/sites/create",
        data={
            "name": "대한민국 복지 알리미",
            "site_url": "https://welfare24.kr",
            "vertical": "WELFARE",
            "wp_username": "welfare_admin",
            "wp_application_password": "abcd efgh ijkl mnop"
        }
    )
    assert create_res.status_code == 302

    db = SessionLocal()
    try:
        site = db.query(Site).filter(Site.site_url == "https://welfare24.kr").first()
        assert site is not None
        assert site.name == "대한민국 복지 알리미"
        assert site.vertical == "WELFARE"
        assert site.wp_username == "welfare_admin"
        assert site.wp_application_password == "abcdefghijklmnop"  # whitespace stripped
        assert site.is_active is True

        site_id = site.id

        # 3. Toggle status
        toggle_res = admin_client.post(f"/admin/sites/{site_id}/toggle")
        assert toggle_res.status_code == 302
        db.refresh(site)
        assert site.is_active is False

        # 4. Delete site
        del_res = admin_client.post(f"/admin/sites/{site_id}/delete")
        assert del_res.status_code == 302
        deleted = db.query(Site).filter(Site.id == site_id).first()
        assert deleted is None
    finally:
        db.close()


@pytest.mark.asyncio
async def test_publishing_service_with_custom_site():
    """Verify PublishingService publishes non-movie posts using bound site credentials."""
    db = SessionLocal()
    try:
        # Create site
        site = Site(
            name="엔터 매거진",
            site_url="https://k-enternews.com",
            vertical="ENTERTAINMENT",
            wp_username="ent_editor",
            wp_application_password="mockpassword123",
            is_active=True
        )
        db.add(site)
        db.commit()
        db.refresh(site)

        # Create post without movie_id
        post = Post(
            title="테스트 연예 이슈 기사",
            slug="test-enter-issue-01",
            vertical="ENTERTAINMENT",
            site_id=site.id,
            rendered_content="<div class='entertainment-article-wrap'>기사 본문 내용</div>",
            excerpt="연예 기사 요약",
            status=PostStatusEnum.APPROVED.value,
            article_json='{"tags": ["연예", "K컬처", "핫이슈"]}'
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        service = PublishingService()
        mock_result = PublishResult(
            success=True,
            remote_post_id=999,
            remote_url="https://k-enternews.com/test-enter-issue-01"
        )

        with patch("app.publishers.wordpress.WordPressPublisher.publish_post", new_callable=AsyncMock) as mock_pub:
            mock_pub.return_value = mock_result
            result = await service.publish_article(db, post, target_status=PostStatus.PUBLISH)

            assert result.success is True
            assert result.remote_post_id == 999
            db.refresh(post)
            assert post.status == PostStatusEnum.PUBLISHED.value
            assert post.wordpress_post_id == 999
            assert post.wordpress_url == "https://k-enternews.com/test-enter-issue-01"
    finally:
        # Cleanup
        if 'post' in locals() and post.id:
            db.delete(post)
        if 'site' in locals() and site.id:
            db.delete(site)
        db.commit()
        db.close()
