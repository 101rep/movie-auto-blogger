"""Trailer and video clip discovery service with TMDB and YouTube Data API integration."""
from typing import Any, Dict, List, Optional
import httpx

from app.collectors.tmdb import TMDBMovieProvider
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("trailer_service")


class TrailerService:
    """Discovers official YouTube trailers and multi-type video clips for movies.

    Upgrade v2: integrates with YouTubeService for richer video discovery,
    including trailers, teasers, making-of films, OST clips, and interviews.
    """

    def __init__(
        self,
        tmdb_provider: Optional[TMDBMovieProvider] = None,
        youtube_api_key: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.tmdb = tmdb_provider or TMDBMovieProvider()
        self.youtube_api_key = youtube_api_key or settings.YOUTUBE_API_KEY

    async def get_trailer_info(
        self,
        movie_title: str,
        external_id: Optional[str] = None,
    ) -> Optional[Dict[str, str]]:
        """Find the primary official trailer for a movie (backward-compatible API).

        Prioritises TMDB official distributor trailers for exact accuracy,
        with optional YouTube Data API fallback.

        Returns a plain dict for direct use in Jinja2 templates::

            {
                "video_id": "abc123",
                "title": "공식 예고편",
                "embed_url": "https://www.youtube-nocookie.com/embed/abc123",
                "watch_url": "https://www.youtube.com/watch?v=abc123",
                "source": "tmdb" | "youtube_api",
            }
        """
        # 1. Try TMDB videos if external_id is provided
        if external_id:
            try:
                videos = await self.tmdb.get_movie_videos(str(external_id))
                if videos:
                    # Filter for YouTube trailers
                    trailers = [
                        v for v in videos
                        if v.get("site") == "YouTube" and v.get("type") == "Trailer" and v.get("key")
                    ]
                    # Fallback to Teaser or Clip if no Trailer
                    if not trailers:
                        trailers = [
                            v for v in videos
                            if v.get("site") == "YouTube" and v.get("type") in ("Teaser", "Clip") and v.get("key")
                        ]

                    if trailers:
                        selected = trailers[0]
                        v_key = selected["key"]
                        logger.info("Found official TMDB trailer for '%s': key=%s", movie_title, v_key)
                        return {
                            "video_id": v_key,
                            "title": selected.get("name") or f"{movie_title} 공식 예고편",
                            "embed_url": f"https://www.youtube-nocookie.com/embed/{v_key}",
                            "watch_url": f"https://www.youtube.com/watch?v={v_key}",
                            "source": "tmdb",
                        }
            except Exception as e:
                logger.warning("Error fetching TMDB trailer for %s (%s): %s", movie_title, external_id, str(e))

        # 2. Try YouTube Data API v3 if API key configured
        if self.youtube_api_key and self.youtube_api_key.strip():
            try:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": f"{movie_title} 공식 예고편",
                    "type": "video",
                    "maxResults": 1,
                    "key": self.youtube_api_key.strip(),
                    "relevanceLanguage": "ko",
                }
                async with httpx.AsyncClient(timeout=8.0) as client:
                    res = await client.get(url, params=params)
                    if res.status_code == 200:
                        items = res.json().get("items", [])
                        if items and "videoId" in items[0].get("id", {}):
                            v_key = items[0]["id"]["videoId"]
                            v_title = items[0]["snippet"].get("title") or f"{movie_title} 예고편"
                            logger.info("Found YouTube API trailer for '%s': id=%s", movie_title, v_key)
                            return {
                                "video_id": v_key,
                                "title": v_title,
                                "embed_url": f"https://www.youtube-nocookie.com/embed/{v_key}",
                                "watch_url": f"https://www.youtube.com/watch?v={v_key}",
                                "source": "youtube_api",
                            }
            except Exception as e:
                logger.warning("Error querying YouTube Data API for %s: %s", movie_title, str(e))

        return None

    async def get_all_movie_videos(
        self,
        movie_title: str,
        external_id: Optional[str] = None,
        max_additional: int = 3,
    ) -> List[Dict[str, Any]]:
        """Discover multiple video types for a movie (trailers, teasers, making-of, OST, interviews).

        Returns a list of video dicts compatible with the article template.
        Each dict contains:
            video_id, title, video_type, type_label, embed_url, watch_url,
            source, view_count, like_count, comment_count, channel_name

        Integrates with YouTubeService for stats enrichment.
        """
        from app.services.youtube_service import YouTubeService

        yt_service = YouTubeService(youtube_api_key=self.youtube_api_key)

        # Gather TMDB video keys first
        tmdb_video_keys: List[Dict[str, str]] = []
        if external_id:
            try:
                raw_videos = await self.tmdb.get_movie_videos(str(external_id))
                if raw_videos:
                    tmdb_video_keys = [
                        v for v in raw_videos
                        if v.get("site") == "YouTube" and v.get("key")
                    ]
            except Exception as e:
                logger.warning("Error fetching TMDB video list for %s: %s", movie_title, e)

        # Delegate full discovery to YouTubeService
        video_infos = await yt_service.get_movie_videos(
            movie_title=movie_title,
            external_id=external_id,
            tmdb_video_keys=tmdb_video_keys,
            max_additional_videos=max_additional,
        )

        return [v.to_dict() for v in video_infos]

    async def get_audience_reaction_for_trailer(
        self,
        trailer_video_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Fetch audience reaction data (top comments + sentiment) for the main trailer.

        Returns dict for Jinja2 rendering or None if unavailable.
        """
        if not trailer_video_id:
            return None
        from app.services.youtube_service import YouTubeService

        yt_service = YouTubeService(youtube_api_key=self.youtube_api_key)
        reaction = await yt_service.get_audience_reaction(trailer_video_id)
        if reaction:
            return reaction.to_dict()
        return None
