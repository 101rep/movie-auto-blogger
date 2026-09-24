"""TMDB (The Movie Database) API adapter implementation."""
from typing import Any, Dict, List, Optional
import httpx

from app.collectors.base import BaseCollector, NormalizedMovie
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("tmdb_collector")


class TMDBMovieProvider(BaseCollector):
    """TMDB API v3/v4 provider adapter."""

    BASE_URL = "https://api.themoviedb.org/3"
    POSTER_BASE_URL = "https://image.tmdb.org/t/p/w780"
    BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/w1280"

    def __init__(self, api_token: Optional[str] = None) -> None:
        settings = get_settings()
        self.token = api_token if api_token is not None else settings.MOVIE_API_TOKEN
        self.language = "ko-KR"

    def _get_headers_and_params(self, params: Optional[Dict[str, Any]] = None) -> tuple[Dict[str, str], Dict[str, Any]]:
        """Determine authentication style (v4 Bearer or v3 api_key param)."""
        headers = {"Accept": "application/json"}
        req_params = dict(params or {})
        req_params.setdefault("language", self.language)

        if not self.token:
            return headers, req_params

        clean_token = self.token.strip()
        # If token is long (JWT / v4 Read Access Token)
        if len(clean_token) > 40:
            headers["Authorization"] = f"Bearer {clean_token}"
        else:
            # 32-character v3 api_key
            req_params["api_key"] = clean_token

        return headers, req_params

    async def health_check(self) -> Dict[str, Any]:
        """Verify TMDB API token and connectivity."""
        if not self.token or not self.token.strip():
            return {
                "success": False,
                "message": "TMDB API 토큰이 설정되지 않았습니다 (.env의 MOVIE_API_TOKEN 확인 필요)"
            }

        headers, params = self._get_headers_and_params()
        url = f"{self.BASE_URL}/authentication"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("success", True):
                        return {"success": True, "message": "TMDB API 정상 연결 및 인증 성공"}
                elif res.status_code in (401, 403):
                    return {
                        "success": False,
                        "message": "TMDB 인증 실패 (401/403): 발급받은 API Read Access Token 또는 API Key를 확인하세요."
                    }
                else:
                    return {
                        "success": False,
                        "message": f"TMDB 서버 응답 오류 (상태 코드: {res.status_code})"
                    }
        except httpx.TimeoutException:
            return {"success": False, "message": "TMDB 서버 응답 시간 초과 (네트워크 상태를 확인하세요)"}
        except Exception as e:
            logger.error("TMDB health check exception: %s", str(e), exc_info=True)
            return {"success": False, "message": f"TMDB 연결 중 오류 발생: {str(e)}"}

        return {"success": False, "message": "TMDB 인증 실패"}

    def _normalize_movie(self, data: Dict[str, Any], credits: Optional[Dict[str, Any]] = None) -> NormalizedMovie:
        """Transform TMDB raw movie JSON into NormalizedMovie model."""
        external_id = str(data.get("id"))
        title = data.get("title") or data.get("original_title") or "제목 없음"
        original_title = data.get("original_title")
        overview = data.get("overview")
        release_date = data.get("release_date")
        runtime = data.get("runtime")
        popularity = float(data.get("popularity") or 0.0)
        vote_average = float(data.get("vote_average") or 0.0)
        vote_count = int(data.get("vote_count") or 0)
        original_language = data.get("original_language")

        # Genres
        genres = []
        if "genres" in data and isinstance(data["genres"], list):
            genres = [g.get("name") for g in data["genres"] if isinstance(g, dict) and g.get("name")]
        elif "genre_ids" in data:
            # Fallback if genre_ids are present in list views
            genres = []

        # Images
        poster_path = data.get("poster_path")
        poster_url = f"{self.POSTER_BASE_URL}{poster_path}" if poster_path else None

        backdrop_path = data.get("backdrop_path")
        backdrop_url = f"{self.BACKDROP_BASE_URL}{backdrop_path}" if backdrop_path else None

        # Credits: Director and Cast
        director = None
        major_cast: List[str] = []

        if credits:
            crew = credits.get("crew", [])
            for member in crew:
                if member.get("job") == "Director":
                    director = member.get("name")
                    break

            cast_list = credits.get("cast", [])
            major_cast = [
                actor.get("name") for actor in cast_list[:8]
                if isinstance(actor, dict) and actor.get("name")
            ]

        # External IDs (IMDb)
        imdb_id = data.get("imdb_id")
        if not imdb_id and "external_ids" in data and isinstance(data["external_ids"], dict):
            imdb_id = data["external_ids"].get("imdb_id")

        source_url = f"https://www.themoviedb.org/movie/{external_id}"

        return NormalizedMovie(
            external_id=external_id,
            source="tmdb",
            title=title,
            original_title=original_title,
            overview=overview,
            release_date=release_date,
            runtime=runtime,
            genres=genres,
            original_language=original_language,
            popularity=popularity,
            vote_average=vote_average,
            vote_count=vote_count,
            director=director,
            major_cast=major_cast,
            imdb_id=imdb_id,
            poster_reference=poster_url,
            backdrop_reference=backdrop_url,
            source_url=source_url,
            raw_json=data,
            source_attribution="TMDB (The Movie Database)"
        )

    async def _fetch_movies_list(self, endpoint: str, page: int = 1) -> List[NormalizedMovie]:
        """Generic fetcher for list endpoints (popular, now_playing, upcoming)."""
        headers, params = self._get_headers_and_params({"page": page})
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code != 200:
                    logger.warning("TMDB request to %s returned status %d: %s", endpoint, res.status_code, res.text)
                    return []
                data = res.json()
                results = data.get("results", [])
                return [self._normalize_movie(item) for item in results]
        except Exception as e:
            logger.error("Error fetching movies from %s: %s", endpoint, str(e), exc_info=True)
            return []

    async def get_popular_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch currently popular movies."""
        return await self._fetch_movies_list("/movie/popular", page=page)

    async def get_now_playing_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch currently playing movies in theaters."""
        return await self._fetch_movies_list("/movie/now_playing", page=page)

    async def get_upcoming_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch upcoming movie releases."""
        return await self._fetch_movies_list("/movie/upcoming", page=page)

    async def get_korean_movies(self, years_back: int = 3, page: int = 1) -> List[NormalizedMovie]:
        """Fetch popular and acclaimed Korean movies from recent years."""
        from datetime import datetime, timezone
        current_year = datetime.now(timezone.utc).year
        min_date = f"{current_year - years_back}-01-01"
        max_date = f"{current_year}-12-31"

        headers, params = self._get_headers_and_params({
            "page": page,
            "with_original_language": "ko",
            "primary_release_date.gte": min_date,
            "primary_release_date.lte": max_date,
            "vote_count.gte": 20,
            "sort_by": "popularity.desc"
        })
        url = f"{self.BASE_URL}/discover/movie"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    results = res.json().get("results", [])
                    return [self._normalize_movie(item) for item in results]
        except Exception as e:
            logger.error("Error fetching Korean movies from discover: %s", str(e))
        return []

    async def get_ott_movies(self, page: int = 1) -> List[NormalizedMovie]:
        """Fetch trending OTT movies available in South Korea (Netflix, Disney+, Watcha, Wave)."""
        headers, params = self._get_headers_and_params({
            "page": page,
            "watch_region": "KR",
            "with_watch_providers": "8|337|97|356",
            "vote_count.gte": 30,
            "sort_by": "popularity.desc"
        })
        url = f"{self.BASE_URL}/discover/movie"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    results = res.json().get("results", [])
                    return [self._normalize_movie(item) for item in results]
        except Exception as e:
            logger.error("Error fetching OTT movies from discover: %s", str(e))
        return []

    async def get_movie_credits(self, movie_id: str) -> Dict[str, Any]:
        """Fetch credits (director and cast) for a specific movie."""
        headers, params = self._get_headers_and_params()
        url = f"{self.BASE_URL}/movie/{movie_id}/credits"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    return res.json()
        except Exception as e:
            logger.error("Failed to fetch credits for movie %s: %s", movie_id, str(e))
        return {}

    async def get_movie_details(self, movie_id: str) -> Optional[NormalizedMovie]:
        """Fetch detailed information including credits and external IDs for a specific movie."""
        headers, params = self._get_headers_and_params({"append_to_response": "credits,external_ids"})
        url = f"{self.BASE_URL}/movie/{movie_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code != 200:
                    return None
                data = res.json()
                credits = data.get("credits") or await self.get_movie_credits(movie_id)
                return self._normalize_movie(data, credits=credits)
        except Exception as e:
            logger.error("Failed to fetch movie details for %s: %s", movie_id, str(e))
            return None

    async def get_image_metadata(self, movie_id: str) -> Dict[str, Any]:
        """Fetch image metadata for a movie."""
        headers, params = self._get_headers_and_params()
        url = f"{self.BASE_URL}/movie/{movie_id}/images"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    return res.json()
        except Exception as e:
            logger.error("Failed to fetch image metadata for movie %s: %s", movie_id, str(e))
        return {}

    async def get_movie_videos(self, movie_id: str) -> List[Dict[str, Any]]:
        """Fetch video clips and official trailers for a movie with language fallback."""
        headers, params = self._get_headers_and_params()
        url = f"{self.BASE_URL}/movie/{movie_id}/videos"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1. Try Korean first
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    results = res.json().get("results", [])
                    if results:
                        return results

                # 2. Fallback to English / original
                fallback_params = dict(params)
                fallback_params.pop("language", None)
                res_fb = await client.get(url, headers=headers, params=fallback_params)
                if res_fb.status_code == 200:
                    return res_fb.json().get("results", [])
        except Exception as e:
            logger.error("Failed to fetch videos for movie %s: %s", movie_id, str(e))
        return []
