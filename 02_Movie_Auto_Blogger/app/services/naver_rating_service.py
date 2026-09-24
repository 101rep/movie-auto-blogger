"""Naver Movie Rating Scraper Service fetching Korean audience ratings and review counts."""
import re
from typing import Any, Dict, Optional
import urllib.parse
import httpx
from pydantic import BaseModel, Field

from app.utils.logging import get_logger

logger = get_logger("naver_rating_service")

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class NaverRatingResult(BaseModel):
    """Normalized rating result from Naver search."""
    movie_title: str
    rating: float = Field(..., description="네이버 실관람객 또는 네티즌 평점 (10점 만점)")
    rating_type: str = Field(default="실관람객", description="평점 유형 (실관람객 / 네티즌 / 관람객)")
    vote_count_str: Optional[str] = Field(default=None, description="평가 참여 인원 (예: 1,367명)")
    search_url: str = ""


class NaverRatingService:
    """Fetches real-time Naver movie ratings using search scraping."""

    _cache: Dict[str, Optional[NaverRatingResult]] = {}

    @classmethod
    def clean_title(cls, title: str) -> str:
        """Clean movie title for search query."""
        # Remove parenthetical years like (2024), (영화)
        cleaned = re.sub(r"\([^)]*\)", "", title)
        # Remove subtitles after colon if very long
        if ":" in cleaned:
            parts = cleaned.split(":")
            if len(parts[0].strip()) >= 2:
                cleaned = parts[0].strip()
        return cleaned.strip()

    @classmethod
    async def fetch_rating(
        cls,
        movie_title: str,
        client: Optional[httpx.AsyncClient] = None
    ) -> Optional[NaverRatingResult]:
        """Fetch Naver audience rating for the given movie title."""
        clean = cls.clean_title(movie_title)
        if not clean:
            return None

        # Check cache
        if clean in cls._cache:
            return cls._cache[clean]

        query = f"영화 {clean} 평점"
        url = "https://search.naver.com/search.naver"
        params = {"query": query}
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
        }

        try:
            should_close = False
            if client is None:
                client = httpx.AsyncClient(timeout=6.0, follow_redirects=True)
                should_close = True

            try:
                res = await client.get(url, params=params, headers=headers)
                if res.status_code != 200:
                    logger.warning("Naver search returned status %d for '%s'", res.status_code, clean)
                    cls._cache[clean] = None
                    return None

                html_text = res.text
                final_url = str(res.url)
            finally:
                if should_close:
                    await client.aclose()

            result = cls._parse_rating_html(html_text, clean, final_url)
            cls._cache[clean] = result
            if result:
                logger.info(
                    "Fetched Naver rating for '%s': %.2f점 (%s, %s)",
                    clean, result.rating, result.rating_type, result.vote_count_str or "참여수 미상"
                )
            else:
                logger.info("No Naver rating found for '%s'", clean)

            return result

        except Exception as e:
            logger.warning("Failed to fetch Naver rating for '%s': %s", clean, str(e))
            cls._cache[clean] = None
            return None

    @classmethod
    def _parse_rating_html(cls, html_text: str, movie_title: str, url: str) -> Optional[NaverRatingResult]:
        """Parse Naver search HTML for rating and voter count."""
        # 1. Primary Naver DOM Pattern: class="area_star_number">7.13
        star_match = re.search(r'class=["\']area_star_number["\']>([0-9\.]+)', html_text)
        if star_match:
            try:
                val = float(star_match.group(1))
                if 1.0 <= val <= 10.0:
                    # Find voter count near star area
                    vote_str = None
                    people_match = re.search(r'class=["\']area_people["\']>([^<]+)', html_text)
                    if people_match:
                        vote_str = people_match.group(1).replace("참여", "").strip()

                    # Determine type: check if '실관람객' or '네티즌' precedes star area
                    star_idx = star_match.start()
                    preceding = html_text[max(0, star_idx - 300):star_idx]
                    r_type = "실관람객"
                    if "네티즌" in preceding:
                        r_type = "네티즌"
                    elif "실관람객" in preceding:
                        r_type = "실관람객"
                    elif "관람객" in preceding:
                        r_type = "관람객"

                    return NaverRatingResult(
                        movie_title=movie_title,
                        rating=val,
                        rating_type=r_type,
                        vote_count_str=vote_str,
                        search_url=url
                    )
            except ValueError:
                pass

        # 2. Secondary Regex Fallback: 실관람객 평점 8.42 or 네티즌 평점 7.50
        secondary_match = re.search(r'(실관람객|네티즌|관람객)\s*평점[^\d]*?(\d+\.\d{1,2})', html_text)
        if secondary_match:
            try:
                r_type = secondary_match.group(1)
                val = float(secondary_match.group(2))
                if 1.0 <= val <= 10.0:
                    return NaverRatingResult(
                        movie_title=movie_title,
                        rating=val,
                        rating_type=r_type,
                        vote_count_str=None,
                        search_url=url
                    )
            except ValueError:
                pass

        return None
