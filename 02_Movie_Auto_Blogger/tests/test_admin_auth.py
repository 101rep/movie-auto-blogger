"""Unit tests for admin authentication and dashboard access."""
from fastapi.testclient import TestClient


def test_unauthenticated_dashboard_redirects_to_login(client: TestClient):
    """Accessing /admin without session should redirect to /admin/login."""
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


def test_admin_login_page_renders(client: TestClient):
    """GET /admin/login should display the Korean login page."""
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert "AUTO BLOGGER" in response.text
    assert "관리자 아이디" in response.text


def test_admin_login_invalid_credentials(client: TestClient):
    """POST /admin/login with invalid password returns 401."""
    response = client.post(
        "/admin/login",
        data={"username": "testadmin", "password": "wrongpassword"},
        follow_redirects=False
    )
    assert response.status_code == 401
    assert "일치하지 않습니다" in response.text


def test_admin_login_success_and_dashboard_access(client: TestClient):
    """POST /admin/login with correct credentials establishes session and loads dashboard."""
    response = client.post(
        "/admin/login",
        data={"username": "testadmin", "password": "testpass1234!"},
        follow_redirects=False
    )
    assert response.status_code == 302
    assert response.headers["location"] == "/admin"

    # Subsequent request using session cookie
    dashboard_res = client.get("/admin")
    assert dashboard_res.status_code == 200
    assert "시스템 대시보드" in dashboard_res.text
    assert "testadmin" in dashboard_res.text


def test_admin_logout(client: TestClient):
    """Logging in and then logging out clears session and prevents dashboard access."""
    # Login
    client.post(
        "/admin/login",
        data={"username": "testadmin", "password": "testpass1234!"},
        follow_redirects=False
    )
    # Logout
    logout_res = client.get("/admin/logout", follow_redirects=False)
    assert logout_res.status_code == 302
    assert logout_res.headers["location"] == "/admin/login"

    # Verify dashboard now redirects
    dash_res = client.get("/admin", follow_redirects=False)
    assert dash_res.status_code == 302
    assert dash_res.headers["location"] == "/admin/login"


def test_admin_help_page_access(client: TestClient):
    """GET /admin/help should be protected by auth and render comprehensive operations hub."""
    # Unauthenticated -> redirect to login
    res_unauth = client.get("/admin/help", follow_redirects=False)
    assert res_unauth.status_code == 302
    assert res_unauth.headers["location"] == "/admin/login"

    # Authenticate
    client.post(
        "/admin/login",
        data={"username": "testadmin", "password": "testpass1234!"},
        follow_redirects=False
    )

    # Authenticated -> 200 OK with key guide sections
    res_auth = client.get("/admin/help")
    assert res_auth.status_code == 200
    assert "운영 & 보안 가이드 허브" in res_auth.text
    assert "trendspot24.com" in res_auth.text
    assert "Cloudways" in res_auth.text
    assert "139.59.125.237" in res_auth.text
    assert "구글 서치 콘솔" in res_auth.text
    assert "네이버 서치어드바이저" in res_auth.text

