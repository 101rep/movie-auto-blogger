# -*- coding: utf-8 -*-
"""
TVmaze REST API Client for Global OTT TV Series Metadata & Schedules.
Provides real-time air dates, episode countdowns, cast, and external IDs (TheTVDB/IMDb).
"""

import logging
import re
from typing import Dict, Any, List, Optional
import httpx
from core.ott_engine.config import TVMAZE_BASE_URL, TVMAZE_API_KEY

logger = logging.getLogger("tvmaze_client")


class TVmazeClient:
    """Client for interacting with TVmaze API."""

    def __init__(self, api_key: str = TVMAZE_API_KEY, timeout: float = 12.0):
        self.api_key = api_key
        self.base_url = TVMAZE_BASE_URL.rstrip("/")
        self.timeout = timeout

    def _clean_summary(self, html_text: Optional[str]) -> str:
        """Strips HTML tags from TVmaze summary."""
        if not html_text:
            return ""
        clean = re.sub(r"<[^>]+>", "", html_text)
        return clean.strip()

    def search_show(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Searches for a show by title with embedded episodes, cast, and next episode.
        Returns parsed, clean show metadata.
        """
        url = f"{self.base_url}/singlesearch/shows"
        params = {
            "q": query,
            "embed[]": ["episodes", "cast", "nextepisode"]
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    logger.warning(f"TVmaze show search failed for '{query}': {res.status_code}")
                    return None
                data = res.json()
                return self._parse_show_data(data)
        except Exception as e:
            logger.error(f"Error searching show '{query}' on TVmaze: {e}")
            return None

    def get_show_by_id(self, show_id: int) -> Optional[Dict[str, Any]]:
        """Fetches full show metadata by TVmaze Show ID with embeds."""
        url = f"{self.base_url}/shows/{show_id}"
        params = {
            "embed[]": ["episodes", "cast", "nextepisode"]
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    return None
                return self._parse_show_data(res.json())
        except Exception as e:
            logger.error(f"Error fetching show ID {show_id} on TVmaze: {e}")
            return None

    def get_daily_web_schedule(self, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches web/streaming releases for a specific date (YYYY-MM-DD).
        Filters for major global OTT platforms (Netflix, Disney+, etc.).
        """
        url = f"{self.base_url}/schedule/web"
        params = {}
        if target_date:
            params["date"] = target_date

        results = []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params)
                if res.status_code != 200:
                    logger.warning(f"TVmaze web schedule failed: {res.status_code}")
                    return []
                items = res.json()
                for item in items:
                    show = item.get("_embedded", {}).get("show")
                    if not show:
                        continue
                    web_channel = show.get("webChannel") or {}
                    results.append({
                        "episode_id": item.get("id"),
                        "episode_name": item.get("name"),
                        "season": item.get("season"),
                        "number": item.get("number"),
                        "airdate": item.get("airdate"),
                        "show_id": show.get("id"),
                        "show_name": show.get("name"),
                        "platform": web_channel.get("name", "Web Streaming"),
                        "rating": show.get("rating", {}).get("average"),
                        "image": (show.get("image") or {}).get("original"),
                    })
        except Exception as e:
            logger.error(f"Error fetching TVmaze daily web schedule: {e}")
        return results

    def _parse_show_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parses raw TVmaze JSON into structured dictionary."""
        externals = data.get("externals") or {}
        embedded = data.get("_embedded") or {}
        image = data.get("image") or {}
        rating = data.get("rating") or {}
        web_channel = data.get("webChannel") or {}
        network = data.get("network") or {}

        platform_name = web_channel.get("name") or network.get("name") or "Global OTT"

        # Next episode info
        next_ep = embedded.get("nextepisode") or {}
        next_episode_info = None
        if next_ep:
            next_episode_info = {
                "name": next_ep.get("name"),
                "season": next_ep.get("season"),
                "number": next_ep.get("number"),
                "airdate": next_ep.get("airdate"),
                "airtime": next_ep.get("airtime"),
                "summary": self._clean_summary(next_ep.get("summary")),
            }

        # Episodes list
        raw_episodes = embedded.get("episodes") or []
        episodes = []
        for ep in raw_episodes:
            episodes.append({
                "id": ep.get("id"),
                "name": ep.get("name"),
                "season": ep.get("season"),
                "number": ep.get("number"),
                "airdate": ep.get("airdate"),
                "runtime": ep.get("runtime"),
                "rating": (ep.get("rating") or {}).get("average"),
                "summary": self._clean_summary(ep.get("summary")),
                "image": (ep.get("image") or {}).get("original"),
            })

        # Cast list (top 8)
        raw_cast = embedded.get("cast") or []
        cast = []
        for c in raw_cast[:8]:
            person = c.get("person") or {}
            character = c.get("character") or {}
            cast.append({
                "person_name": person.get("name"),
                "character_name": character.get("name"),
                "person_image": (person.get("image") or {}).get("medium"),
            })

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "type": data.get("type"),
            "language": data.get("language"),
            "genres": data.get("genres", []),
            "status": data.get("status"),
            "runtime": data.get("runtime") or data.get("averageRuntime") or 60,
            "premiered": data.get("premiered"),
            "official_site": data.get("officialSite"),
            "rating": rating.get("average") or 8.0,
            "platform": platform_name,
            "summary": self._clean_summary(data.get("summary")),
            "image_original": image.get("original"),
            "image_medium": image.get("medium"),
            "tvdb_id": externals.get("thetvdb"),
            "imdb_id": externals.get("imdb"),
            "next_episode": next_episode_info,
            "episodes": episodes,
            "total_episodes": len(episodes),
            "cast": cast,
        }
