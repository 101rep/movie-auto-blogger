"""Unit tests for TMDB movie collector adapter with mocked HTTP responses."""
import pytest
import httpx
from unittest.mock import patch, AsyncMock
from app.collectors.tmdb import TMDBMovieProvider


@pytest.mark.asyncio
async def test_tmdb_health_check_missing_token():
    """Verify health check gracefully handles missing API token."""
    provider = TMDBMovieProvider(api_token="")
    result = await provider.health_check()
    assert result["success"] is False
    assert "설정되지 않았습니다" in result["message"]


@pytest.mark.asyncio
async def test_tmdb_health_check_invalid_token():
    """Verify health check diagnoses 401 unauthorized."""
    provider = TMDBMovieProvider(api_token="invalid_token_12345")
    mock_response = httpx.Response(status_code=401, json={"status_code": 7, "status_message": "Invalid API key"})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await provider.health_check()
        assert result["success"] is False
        assert "인증 실패" in result["message"]


@pytest.mark.asyncio
async def test_tmdb_health_check_success():
    """Verify health check succeeds on 200 response."""
    provider = TMDBMovieProvider(api_token="valid_test_token")
    mock_response = httpx.Response(status_code=200, json={"success": True, "status_message": "Success."})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await provider.health_check()
        assert result["success"] is True
        assert "정상 연결" in result["message"]


@pytest.mark.asyncio
async def test_tmdb_popular_movies_normalization():
    """Verify popular movies response is correctly parsed and normalized."""
    provider = TMDBMovieProvider(api_token="test_token")
    mock_data = {
        "page": 1,
        "results": [
            {
                "id": 1022789,
                "title": "인사이드 아웃 2",
                "original_title": "Inside Out 2",
                "overview": "13살이 된 라일리의 머릿속 감정 컨트롤 본부에 새로운 감정들이 등장한다.",
                "release_date": "2024-06-12",
                "popularity": 1450.8,
                "vote_average": 7.6,
                "vote_count": 4500,
                "poster_path": "/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg",
                "backdrop_path": "/xg27NrXi7VXCGUr7MG75UqLl6Vg.jpg",
                "original_language": "en"
            }
        ]
    }
    mock_response = httpx.Response(status_code=200, json=mock_data)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        movies = await provider.get_popular_movies(page=1)

        assert len(movies) == 1
        movie = movies[0]
        assert movie.external_id == "1022789"
        assert movie.title == "인사이드 아웃 2"
        assert movie.original_title == "Inside Out 2"
        assert movie.source == "tmdb"
        assert movie.popularity == 1450.8
        assert movie.vote_average == 7.6
        assert movie.vote_count == 4500
        assert "https://image.tmdb.org/t/p/w780/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg" in movie.poster_reference
        assert "https://image.tmdb.org/t/p/w1280/xg27NrXi7VXCGUr7MG75UqLl6Vg.jpg" in movie.backdrop_reference
        assert "themoviedb.org/movie/1022789" in movie.source_url


@pytest.mark.asyncio
async def test_tmdb_movie_details_and_credits_enrichment():
    """Verify detailed movie endpoint combines movie payload and credits (director/cast)."""
    provider = TMDBMovieProvider(api_token="test_token")

    movie_json = {
        "id": 496243,
        "title": "기생충",
        "original_title": "Parasite",
        "overview": "전원백수로 살 길 막막하지만 사이는 좋은 기택 가족.",
        "release_date": "2019-05-30",
        "runtime": 132,
        "genres": [{"id": 35, "name": "코미디"}, {"id": 53, "name": "스릴러"}],
        "popularity": 85.0,
        "vote_average": 8.5,
        "vote_count": 17000
    }

    credits_json = {
        "id": 496243,
        "cast": [
            {"name": "송강호", "order": 0},
            {"name": "이선균", "order": 1},
            {"name": "조여정", "order": 2},
            {"name": "최우식", "order": 3}
        ],
        "crew": [
            {"name": "봉준호", "job": "Director", "department": "Directing"}
        ]
    }

    async def mock_router(url, *args, **kwargs):
        if "credits" in str(url):
            return httpx.Response(status_code=200, json=credits_json)
        return httpx.Response(status_code=200, json=movie_json)

    with patch("httpx.AsyncClient.get", side_effect=mock_router):
        movie = await provider.get_movie_details("496243")

        assert movie is not None
        assert movie.title == "기생충"
        assert movie.runtime == 132
        assert "코미디" in movie.genres
        assert "스릴러" in movie.genres
        assert movie.director == "봉준호"
        assert "송강호" in movie.major_cast
        assert "최우식" in movie.major_cast
