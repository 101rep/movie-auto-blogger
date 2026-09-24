# -*- coding: utf-8 -*-
"""
Fanart.tv REST API Client for Designer-grade Transparent ClearArt & HD Logos.
Provides transparent PNG logos (hdtvlogo), character cutouts (hdclearart),
and 4K/HD backdrops (showbackground) without subtitles.
"""

import logging
from typing import Dict, Any, List, Optional
import httpx
from core.ott_engine.config import FANART_BASE_URL, FANART_API_KEY

logger = logging.getLogger("fanart_client")


class FanartClient:
    """Client for interacting with Fanart.tv API."""

    def __init__(self, api_key: str = FANART_API_KEY, timeout: float = 12.0):
        self.api_key = api_key
        self.base_url = FANART_BASE_URL.rstrip("/")
        self.timeout = timeout

    def get_tv_assets(self, tvdb_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves all official visual assets for a TV show by TheTVDB ID.
        Returns parsed categories: hdtvlogo, hdclearart, showbackground, etc.
        """
        if not tvdb_id:
            logger.warning("FanartClient: tvdb_id is required")
            return None

        url = f"{self.base_url}/tv/{tvdb_id}"
        headers = {"api-key": self.api_key}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"Fanart.tv fetch failed for tvdb_id {tvdb_id}: {res.status_code}")
                    return None
                return res.json()
        except Exception as e:
            logger.error(f"Error fetching Fanart.tv assets for tvdb_id {tvdb_id}: {e}")
            return None

    def select_best_assets(self, fanart_data: Optional[Dict[str, Any]]) -> Dict[str, Optional[str]]:
        """
        Selects the best quality/highest-voted assets from Fanart data.
        Returns a dictionary with:
        - hd_logo: Transparent PNG logo (prefers ko, then en, sorted by likes)
        - backdrop: 4K or HD background wallpaper without text
        - clearart: Transparent character cut-out art
        - banner: Wide graphic banner
        - poster: Season/Show poster
        """
        if not fanart_data:
            return {
                "hd_logo": None,
                "backdrop": None,
                "clearart": None,
                "banner": None,
                "poster": None,
            }

        def _sort_by_likes(items: List[Dict[str, Any]], lang_pref: List[str] = None) -> Optional[str]:
            if not items:
                return None
            if lang_pref:
                for lang in lang_pref:
                    matched = [it for it in items if it.get("lang") == lang]
                    if matched:
                        sorted_matched = sorted(matched, key=lambda x: int(x.get("likes", 0)), reverse=True)
                        return sorted_matched[0].get("url")
            sorted_items = sorted(items, key=lambda x: int(x.get("likes", 0)), reverse=True)
            return sorted_items[0].get("url")

        # 1. Transparent HD Logo (hdtvlogo > clearlogo)
        logos = fanart_data.get("hdtvlogo") or fanart_data.get("clearlogo") or []
        best_logo = _sort_by_likes(logos, lang_pref=["ko", "en", ""])

        # 2. Backdrop (show4kbackground > showbackground)
        backdrops_4k = fanart_data.get("show4kbackground") or []
        backdrops_hd = fanart_data.get("showbackground") or []
        best_backdrop = _sort_by_likes(backdrops_4k) or _sort_by_likes(backdrops_hd)

        # 3. ClearArt / CharacterArt
        cleararts = fanart_data.get("hdclearart") or fanart_data.get("clearart") or fanart_data.get("characterart") or []
        best_clearart = _sort_by_likes(cleararts, lang_pref=["ko", "en", ""])

        # 4. Banner & Poster
        banners = fanart_data.get("tvbanner") or []
        best_banner = _sort_by_likes(banners)

        posters = fanart_data.get("seasonposter") or fanart_data.get("tvposter") or []
        best_poster = _sort_by_likes(posters)

        return {
            "hd_logo": best_logo,
            "backdrop": best_backdrop,
            "clearart": best_clearart,
            "banner": best_banner,
            "poster": best_poster,
        }
