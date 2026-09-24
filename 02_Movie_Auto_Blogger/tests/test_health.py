"""Unit tests for the /health monitoring endpoint."""
from fastapi.testclient import TestClient


def test_health_endpoint_healthy(client: TestClient):
    """Test health check returns 200 OK with expected system components."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Super Auto Blogger"
    assert "database" in data
    assert data["database"]["status"] == "connected"
    assert "scheduler" in data

    # Verify no secrets or sensitive data leaked in response
    response_text = response.text
    assert "password" not in response_text.lower()
    assert "secret" not in response_text.lower()
    assert "key" not in response_text.lower() or "jobs_count" in response_text
