"""Unit tests for IndexNow and Search Engine Indexing Service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.indexnow_service import IndexNowService


@pytest.mark.asyncio
async def test_indexnow_service_submit_urls():
    service = IndexNowService(host="trendspot24.com", key="testkey123")
    assert service.host == "trendspot24.com"
    assert service.key == "testkey123"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        res = await service.submit_urls(["https://trendspot24.com/movie-review/"])
        assert len(res) == 3
        assert all(res.values())
        assert mock_post.call_count == 3


@pytest.mark.asyncio
async def test_indexnow_service_empty_urls():
    service = IndexNowService()
    res = await service.submit_urls([])
    assert res == {}


@pytest.mark.asyncio
async def test_indexnow_service_ping_sitemaps():
    service = IndexNowService(host="trendspot24.com")
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        res = await service.ping_sitemaps()
        assert len(res) == 1
        assert all(res.values())
