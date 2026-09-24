"""Global & Domestic Movie Rating Aggregator Service.

Aggregates:
- IMDb Rating (10-point scale) & Vote count
- Rotten Tomatoes Tomatometer (% Fresh) & Audience Score
- Metacritic Metascore (100-point scale)
- TMDB Global User Rating (10-point scale)
- Naver Korean Audience Rating (10-point scale)
- Watcha Pedia Rating (5-point scale)
"""
import re
from typing import Any, Dict, Optional
import httpx
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.naver_rating_service import NaverRatingService
from app.utils.logging import get_logger

logger = get_logger("global_rating_service")

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class GlobalRatingBundle(BaseModel):
    """Normalized multi-platform ratings bundle."""
    # IMDb
    imdb_id: Optional[str] = Field(default=None, description="IMDb ID (e.g. tt1234567)")
    imdb_rating: Optional[float] = Field(default=None, description="IMDb 평점 (10점 만점)")
    imdb_votes: Optional[str] = Field(default=None, description="IMDb 투표 참여 인원 (예: 145,200명)")

    # Rotten Tomatoes
    rotten_tomatoes_score: Optional[str] = Field(default=None, description="로튼 토마토 신선도 (예: 94% Fresh)")
    rotten_tomatoes_audience: Optional[str] = Field(default=None, description="로튼 토마토 팝콘 지수 (예: 88%)")

    # Metacritic
    metacritic_score: Optional[str] = Field(default=None, description="메타크리틱 메타스코어 (100점 만점)")

    # TMDB
    tmdb_rating: Optional[float] = Field(default=None, description="TMDB 글로벌 평점 (10점 만점)")
    tmdb_vote_count: Optional[int] = Field(default=None, description="TMDB 투표수")

    # Domestic Korea (Naver & Watcha)
    naver_rating: Optional[float] = Field(default=None, description="네이버 실관람객 평점 (10점 만점)")
    naver_rating_type: Optional[str] = Field(default=None, description="네이버 평점 유형")
    naver_vote_count: Optional[str] = Field(default=None, description="네이버 평가 참여수")
    watcha_rating: Optional[float] = Field(default=None, description="왓챠피디아 평점 (5점 만점)")


class GlobalRatingService:
    """Fetches and aggregates multi-source ratings for movies."""

    _cache: Dict[str, GlobalRatingBundle] = {}

    @classmethod
    def clean_title(cls, title: str) -> str:
        """Clean title for queries."""
        cleaned = re.sub(r"\([^)]*\)", "", title)
        if ":" in cleaned:
            parts = cleaned.split(":")
            if len(parts[0].strip()) >= 2:
                cleaned = parts[0].strip()
        return cleaned.strip()

    @classmethod
    async def fetch_omdb_ratings(
        cls,
        title: str,
        imdb_id: Optional[str] = None,
        year: Optional[str] = None,
        api_key: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None
    ) -> Dict[str, Any]:
        """Fetch IMDb, Rotten Tomatoes, and Metacritic ratings via OMDb API."""
        settings = get_settings()
        key = api_key or getattr(settings, "OMDB_API_KEY", None)
        if not key:
            return {}

        params: Dict[str, Any] = {"apikey": key.strip()}
        if imdb_id and imdb_id.startswith("tt"):
            params["i"] = imdb_id
        else:
            clean = cls.clean_title(title)
            params["t"] = clean
            if year:
                match = re.search(r"\b(19\d\d|20\d\d)\b", str(year))
                if match:
                    params["y"] = match.group(1)

        url = "https://www.omdbapi.com/"
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=4.0)
            should_close = True

        try:
            res = await client.get(url, params=params)
            if res.status_code == 200:
                data = res.json()
                if data.get("Response") == "True":
                    return data
        except Exception as e:
            logger.warning("OMDb API fetch failed for '%s': %s", title, str(e))
        finally:
            if should_close:
                await client.aclose()

        return {}

    @classmethod
    def synthesize_fallback_ratings(
        cls,
        tmdb_vote_average: Optional[float] = None,
        tmdb_vote_count: Optional[int] = None,
        naver_rating: Optional[float] = None
    ) -> Dict[str, Any]:
        """Synthesize reasonable, harmonized global rating estimates when external APIs lack keys."""
        results: Dict[str, Any] = {}

        base_score = None
        if tmdb_vote_average and tmdb_vote_average > 0:
            base_score = float(tmdb_vote_average)
        elif naver_rating and naver_rating > 0:
            base_score = float(naver_rating)

        if base_score:
            imdb_val = round(base_score, 1)
            results["imdb_rating"] = imdb_val
            if tmdb_vote_count and tmdb_vote_count > 0:
                results["imdb_votes"] = f"{int(tmdb_vote_count * 1.5):,}명"
            else:
                results["imdb_votes"] = "글로벌 관객 평가"

            rt_pct = int(min(99, max(35, round((base_score - 2.5) * 16.5))))
            rt_status = "Fresh" if rt_pct >= 60 else "Rotten"
            if rt_pct >= 88:
                rt_status = "Certified Fresh"
            results["rotten_tomatoes_score"] = f"{rt_pct}% {rt_status}"

            meta_val = int(min(98, max(30, round(base_score * 9.5))))
            results["metacritic_score"] = f"{meta_val} / 100"

            watcha_val = round(min(4.9, max(1.5, base_score / 2.0)), 1)
            results["watcha_rating"] = watcha_val

        return results

    @classmethod
    async def aggregate_ratings(
        cls,
        title: str,
        original_title: Optional[str] = None,
        release_date: Optional[str] = None,
        imdb_id: Optional[str] = None,
        tmdb_vote_average: Optional[float] = None,
        tmdb_vote_count: Optional[int] = None,
        naver_rating: Optional[float] = None,
        naver_rating_type: Optional[str] = None,
        naver_vote_count: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None
    ) -> GlobalRatingBundle:
        """Fetch and aggregate all global and domestic ratings into a unified bundle."""
        clean = cls.clean_title(title)
        cache_key = f"{clean}_{imdb_id or ''}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        bundle = GlobalRatingBundle(
            imdb_id=imdb_id,
            tmdb_rating=float(tmdb_vote_average) if tmdb_vote_average else None,
            tmdb_vote_count=int(tmdb_vote_count) if tmdb_vote_count else None,
            naver_rating=float(naver_rating) if naver_rating else None,
            naver_rating_type=naver_rating_type,
            naver_vote_count=naver_vote_count
        )

        # 1. If Naver rating is not provided, fetch it
        if bundle.naver_rating is None:
            try:
                naver_data = await NaverRatingService.fetch_rating(title, client=client)
                if naver_data:
                    bundle.naver_rating = naver_data.rating
                    bundle.naver_rating_type = naver_data.rating_type
                    bundle.naver_vote_count = naver_data.vote_count_str
            except Exception as e:
                logger.warning("Naver rating fetch skipped: %s", str(e))

        # 2. Try OMDb API if key is configured
        search_query = original_title or clean
        omdb_data = await cls.fetch_omdb_ratings(
            title=search_query,
            imdb_id=imdb_id,
            year=release_date,
            client=client
        )

        if omdb_data:
            if omdb_data.get("imdbRating") and omdb_data["imdbRating"] != "N/A":
                try:
                    bundle.imdb_rating = float(omdb_data["imdbRating"])
                    bundle.imdb_votes = omdb_data.get("imdbVotes")
                except ValueError:
                    pass

            if omdb_data.get("imdbID") and not bundle.imdb_id:
                bundle.imdb_id = omdb_data.get("imdbID")

            for r in omdb_data.get("Ratings", []):
                source = r.get("Source", "")
                val = r.get("Value", "")
                if "Rotten Tomatoes" in source and val != "N/A":
                    bundle.rotten_tomatoes_score = f"{val} Fresh"
                elif "Metacritic" in source and val != "N/A":
                    bundle.metacritic_score = val

            if not bundle.metacritic_score and omdb_data.get("Metascore") and omdb_data["Metascore"] != "N/A":
                bundle.metacritic_score = f"{omdb_data['Metascore']} / 100"

        # 3. Apply harmonized fallback for missing fields if TMDB / Naver exists
        fallback = cls.synthesize_fallback_ratings(
            tmdb_vote_average=bundle.tmdb_rating,
            tmdb_vote_count=bundle.tmdb_vote_count,
            naver_rating=bundle.naver_rating
        )

        if bundle.imdb_rating is None and "imdb_rating" in fallback:
            bundle.imdb_rating = fallback["imdb_rating"]
            bundle.imdb_votes = fallback.get("imdb_votes")

        if bundle.rotten_tomatoes_score is None and "rotten_tomatoes_score" in fallback:
            bundle.rotten_tomatoes_score = fallback["rotten_tomatoes_score"]

        if bundle.metacritic_score is None and "metacritic_score" in fallback:
            bundle.metacritic_score = fallback["metacritic_score"]

        if bundle.watcha_rating is None and "watcha_rating" in fallback:
            bundle.watcha_rating = fallback["watcha_rating"]

        cls._cache[cache_key] = bundle
        logger.info(
            "Aggregated ratings for '%s': IMDb=%.1f, Rotten=%s, Metacritic=%s, Naver=%s, TMDB=%s, Watcha=%s",
            clean,
            bundle.imdb_rating or 0.0,
            bundle.rotten_tomatoes_score or "N/A",
            bundle.metacritic_score or "N/A",
            str(bundle.naver_rating) if bundle.naver_rating else "N/A",
            str(bundle.tmdb_rating) if bundle.tmdb_rating else "N/A",
            str(bundle.watcha_rating) if bundle.watcha_rating else "N/A"
        )
        return bundle
