"""YouTube Data API v3 enhanced service.

Provides:
  - Multi-video discovery (trailers, teasers, making-of, OST clips, interviews)
  - Video statistics fetching (views, likes, comment count → candidate scoring)
  - Audience reaction analysis from top comments
  - Related video curation for article sidebars
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("youtube_service")

# ─── Constants ────────────────────────────────────────────────────────────────
YT_API_BASE = "https://www.googleapis.com/youtube/v3"
_TIMEOUT = 10.0

# Video type labels shown in article templates
_VIDEO_TYPE_LABELS: Dict[str, str] = {
    "trailer": "공식 예고편",
    "teaser": "티저 예고편",
    "making": "메이킹 필름",
    "ost": "OST / 사운드트랙",
    "interview": "감독·배우 인터뷰",
    "clip": "영화 클립",
    "other": "관련 영상",
}


class YouTubeVideoInfo:
    """Structured info for a single YouTube video."""

    def __init__(
        self,
        video_id: str,
        title: str,
        video_type: str,
        embed_url: str,
        watch_url: str,
        source: str = "youtube_api",
        view_count: Optional[int] = None,
        like_count: Optional[int] = None,
        comment_count: Optional[int] = None,
        channel_name: Optional[str] = None,
    ) -> None:
        self.video_id = video_id
        self.title = title
        self.video_type = video_type
        self.type_label = _VIDEO_TYPE_LABELS.get(video_type, _VIDEO_TYPE_LABELS["other"])
        self.embed_url = embed_url
        self.watch_url = watch_url
        self.source = source
        self.view_count = view_count
        self.like_count = like_count
        self.comment_count = comment_count
        self.channel_name = channel_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_id": self.video_id,
            "title": self.title,
            "video_type": self.video_type,
            "type_label": self.type_label,
            "embed_url": self.embed_url,
            "watch_url": self.watch_url,
            "source": self.source,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "channel_name": self.channel_name,
        }


class AudienceReaction:
    """Aggregated audience reaction data extracted from YouTube comments."""

    def __init__(
        self,
        total_comment_count: int,
        top_comments: List[str],
        sentiment_summary: str,
        hype_score: int,  # 0~10 excitement level
    ) -> None:
        self.total_comment_count = total_comment_count
        self.top_comments = top_comments
        self.sentiment_summary = sentiment_summary
        self.hype_score = hype_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_comment_count": self.total_comment_count,
            "top_comments": self.top_comments,
            "sentiment_summary": self.sentiment_summary,
            "hype_score": self.hype_score,
        }


class YouTubeService:
    """Full-featured YouTube Data API v3 integration service.

    Call patterns:
        svc = YouTubeService()
        # Get multi-type videos for article
        videos = await svc.get_movie_videos(movie_title="범죄도시4", external_id="12345")
        # Get audience reaction for scoring / article section
        reaction = await svc.get_audience_reaction(video_id="abc123")
        # Get trailer stats for candidate scoring
        stats = await svc.get_video_stats(video_id="abc123")
    """

    def __init__(self, youtube_api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = youtube_api_key or settings.YOUTUBE_API_KEY
        self._enabled = bool(self.api_key and self.api_key.strip())

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    async def get_movie_videos(
        self,
        movie_title: str,
        external_id: Optional[str] = None,
        tmdb_video_keys: Optional[List[Dict[str, str]]] = None,
        max_additional_videos: int = 3,
    ) -> List[YouTubeVideoInfo]:
        """Discover multiple YouTube videos related to a movie.

        Returns a deduplicated list ordered by relevance:
          1. Official trailers (from TMDB keys or YouTube search)
          2. Teasers / making-of / OST clips (via YouTube search)
          3. Interview clips (director/cast)

        Args:
            movie_title: Korean or original title.
            external_id: TMDB movie ID (used to log context).
            tmdb_video_keys: Pre-fetched TMDB video entries (passed from TrailerService).
            max_additional_videos: Number of extra videos beyond main trailer.
        """
        if not self._enabled:
            logger.debug("YouTube API key not configured, skipping multi-video discovery.")
            return []

        results: List[YouTubeVideoInfo] = []
        seen_ids: set[str] = set()

        # 1. Enrich TMDB-provided video keys with stats
        if tmdb_video_keys:
            for entry in tmdb_video_keys:
                vid_key = entry.get("key")
                if not vid_key or vid_key in seen_ids:
                    continue
                v_type = self._classify_tmdb_type(entry.get("type", ""))
                vid_info = YouTubeVideoInfo(
                    video_id=vid_key,
                    title=entry.get("name") or f"{movie_title} {_VIDEO_TYPE_LABELS.get(v_type, '예고편')}",
                    video_type=v_type,
                    embed_url=f"https://www.youtube-nocookie.com/embed/{vid_key}",
                    watch_url=f"https://www.youtube.com/watch?v={vid_key}",
                    source="tmdb",
                )
                results.append(vid_info)
                seen_ids.add(vid_key)

        # 2. Fetch additional videos via YouTube Search API
        if max_additional_videos > 0:
            search_queries = self._build_search_queries(movie_title, len(results))
            for query, video_type in search_queries[:max_additional_videos]:
                try:
                    found = await self._search_video(query, video_type, seen_ids)
                    if found:
                        results.append(found)
                        seen_ids.add(found.video_id)
                except Exception as e:
                    logger.warning("YouTube search failed for query '%s': %s", query, e)

        # 3. Batch-fetch statistics for all discovered videos
        if results:
            all_ids = [v.video_id for v in results]
            stats_map = await self._fetch_stats_batch(all_ids)
            for vid in results:
                s = stats_map.get(vid.video_id)
                if s:
                    vid.view_count = s.get("view_count")
                    vid.like_count = s.get("like_count")
                    vid.comment_count = s.get("comment_count")
                    vid.channel_name = s.get("channel_name")

        logger.info(
            "Discovered %d YouTube videos for '%s' (external_id=%s).",
            len(results), movie_title, external_id
        )
        return results

    async def search_travel_video(
        self,
        destination: str,
        country: Optional[str] = None
    ) -> Optional[YouTubeVideoInfo]:
        """Search for top-rated, high-retention travel guide video on YouTube.
        
        Picks the most relevant embeddable video with highest view count/engagement.
        """
        if not self._enabled:
            return None

        clean_dest = destination.split('(')[0].strip()
        query = f"{clean_dest} 여행 코스 꿀팁 가이드"
        url = f"{YT_API_BASE}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 5,
            "key": self.api_key.strip(),
            "relevanceLanguage": "ko",
            "videoEmbeddable": "true",
            "order": "relevance"
        }
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                res = await client.get(url, params=params)
                if res.status_code != 200:
                    return None
                items = res.json().get("items", [])
                if not items:
                    return None

                video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]
                if not video_ids:
                    return None

                # Fetch statistics to pick the best video
                stats_map = await self._fetch_stats_batch(video_ids)

                # Pick video with highest view count
                best_item = None
                best_views = -1
                for it in items:
                    vid_id = it.get("id", {}).get("videoId")
                    s = stats_map.get(vid_id, {})
                    v_cnt = s.get("view_count", 0) or 0
                    if v_cnt > best_views:
                        best_views = v_cnt
                        best_item = it

                if not best_item:
                    best_item = items[0]

                target_id = best_item["id"]["videoId"]
                target_snippet = best_item.get("snippet", {})
                target_stats = stats_map.get(target_id, {})

                logger.info("Found best travel video for '%s': [%s] (Views: %s)", clean_dest, target_id, target_stats.get("view_count"))

                return YouTubeVideoInfo(
                    video_id=target_id,
                    title=target_snippet.get("title", f"{clean_dest} 여행 가이드"),
                    video_type="travel_guide",
                    embed_url=f"https://www.youtube-nocookie.com/embed/{target_id}",
                    watch_url=f"https://www.youtube.com/watch?v={target_id}",
                    source="youtube_api",
                    view_count=target_stats.get("view_count"),
                    like_count=target_stats.get("like_count"),
                    comment_count=target_stats.get("comment_count"),
                    channel_name=target_snippet.get("channelTitle")
                )
        except Exception as e:
            logger.warning("Failed to search travel YouTube video for '%s': %s", destination, e)
            return None

    async def get_video_stats(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fetch statistics for a single video (view_count, like_count, comment_count)."""
        if not self._enabled or not video_id:
            return None
        stats_map = await self._fetch_stats_batch([video_id])
        return stats_map.get(video_id)

    async def get_audience_reaction(
        self,
        video_id: str,
        max_comments: int = 20,
    ) -> Optional[AudienceReaction]:
        """Fetch top comments and analyse audience sentiment for a trailer.

        Returns AudienceReaction with:
        - Top 5 highest-liked comment excerpts (truncated to 80 chars)
        - Overall sentiment summary (excited / mixed / negative)
        - Hype score 0~10 derived from view / like ratio and comment tone
        """
        if not self._enabled or not video_id:
            return None

        # Fetch stats first for total comment count and view/like
        stats = await self._fetch_stats_batch([video_id])
        vid_stats = stats.get(video_id, {})
        total_comments = vid_stats.get("comment_count", 0) or 0
        view_count = vid_stats.get("view_count", 0) or 0
        like_count = vid_stats.get("like_count", 0) or 0

        # Fetch top comments
        top_comments: List[str] = []
        try:
            url = f"{YT_API_BASE}/commentThreads"
            params = {
                "part": "snippet",
                "videoId": video_id,
                "order": "relevance",
                "maxResults": max_comments,
                "key": self.api_key.strip(),
                "textFormat": "plainText",
            }
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    items = res.json().get("items", [])
                    for item in items:
                        snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                        text = snippet.get("textDisplay", "").strip()
                        if text and len(text) > 5:
                            # Truncate long comments for display
                            top_comments.append(text[:100] + ("..." if len(text) > 100 else ""))
                        if len(top_comments) >= 5:
                            break
        except Exception as e:
            logger.warning("Failed to fetch comments for video %s: %s", video_id, e)

        # Compute hype score (0–10)
        hype_score = self._compute_hype_score(
            view_count=view_count,
            like_count=like_count,
            comment_count=total_comments,
        )

        # Derive simple sentiment summary
        sentiment_summary = self._derive_sentiment_summary(hype_score, total_comments)

        logger.info(
            "Audience reaction for video %s: %d comments, hype_score=%d, sentiment='%s'",
            video_id, total_comments, hype_score, sentiment_summary
        )

        return AudienceReaction(
            total_comment_count=total_comments,
            top_comments=top_comments,
            sentiment_summary=sentiment_summary,
            hype_score=hype_score,
        )

    async def compute_youtube_opportunity_score(self, video_id: str) -> float:
        """Return a 0.0–10.0 YouTube opportunity bonus for candidate scoring.

        Higher score = more viral trailer → push movie up in candidate ranking.
        Formula factors: view_count, like/view ratio, comment_count.
        """
        if not self._enabled or not video_id:
            return 0.0
        stats_map = await self._fetch_stats_batch([video_id])
        s = stats_map.get(video_id, {})
        view_count = s.get("view_count") or 0
        like_count = s.get("like_count") or 0
        comment_count = s.get("comment_count") or 0
        hype = self._compute_hype_score(view_count, like_count, comment_count)
        # Normalise hype 0~10 to bonus 0.0~10.0 (used directly in scoring)
        return float(hype)

    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    async def _search_video(
        self,
        query: str,
        video_type: str,
        seen_ids: set[str],
    ) -> Optional[YouTubeVideoInfo]:
        """Search YouTube for a single video matching query, skipping already-found IDs."""
        url = f"{YT_API_BASE}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 5,
            "key": self.api_key.strip(),
            "relevanceLanguage": "ko",
            "videoCategoryId": "1",  # Film & Animation
        }
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            res = await client.get(url, params=params)
            if res.status_code != 200:
                return None
            items = res.json().get("items", [])
            for item in items:
                vid_id = item.get("id", {}).get("videoId")
                if not vid_id or vid_id in seen_ids:
                    continue
                snippet = item.get("snippet", {})
                return YouTubeVideoInfo(
                    video_id=vid_id,
                    title=snippet.get("title", query),
                    video_type=video_type,
                    embed_url=f"https://www.youtube-nocookie.com/embed/{vid_id}",
                    watch_url=f"https://www.youtube.com/watch?v={vid_id}",
                    source="youtube_api",
                    channel_name=snippet.get("channelTitle"),
                )
        return None

    async def _fetch_stats_batch(
        self, video_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Fetch statistics for a batch of video IDs via videos.list API.

        Returns mapping of video_id → {view_count, like_count, comment_count, channel_name}.
        """
        if not video_ids or not self._enabled:
            return {}
        url = f"{YT_API_BASE}/videos"
        params = {
            "part": "statistics,snippet",
            "id": ",".join(video_ids[:50]),  # API limit
            "key": self.api_key.strip(),
        }
        result: Dict[str, Dict[str, Any]] = {}
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    for item in res.json().get("items", []):
                        vid_id = item.get("id")
                        stats = item.get("statistics", {})
                        snippet = item.get("snippet", {})
                        result[vid_id] = {
                            "view_count": int(stats.get("viewCount") or 0),
                            "like_count": int(stats.get("likeCount") or 0),
                            "comment_count": int(stats.get("commentCount") or 0),
                            "channel_name": snippet.get("channelTitle"),
                        }
        except Exception as e:
            logger.warning("Failed to fetch YouTube batch stats: %s", e)
        return result

    @staticmethod
    def _classify_tmdb_type(tmdb_type: str) -> str:
        """Map TMDB video type string to internal video_type key."""
        mapping = {
            "Trailer": "trailer",
            "Teaser": "teaser",
            "Featurette": "making",
            "Behind the Scenes": "making",
            "Clip": "clip",
        }
        return mapping.get(tmdb_type, "other")

    @staticmethod
    def _build_search_queries(movie_title: str, already_found: int) -> List[tuple[str, str]]:
        """Return ordered list of (search_query, video_type) to fetch beyond main trailer."""
        queries = [
            (f"{movie_title} 메이킹 필름 비하인드", "making"),
            (f"{movie_title} OST 사운드트랙", "ost"),
            (f"{movie_title} 감독 인터뷰", "interview"),
            (f"{movie_title} 티저 예고편", "teaser"),
        ]
        # If we already have a trailer, skip teaser to avoid duplication
        if already_found > 0:
            queries = [q for q in queries if q[1] != "teaser"]
        return queries

    @staticmethod
    def _compute_hype_score(
        view_count: int,
        like_count: int,
        comment_count: int,
    ) -> int:
        """Compute 0–10 hype score from YouTube engagement metrics.

        Thresholds (cumulative points up to 10):
          - View milestones (0–4 pts): <100K=0, <1M=1, <5M=2, <20M=3, ≥20M=4
          - Like ratio 0–3 pts: like/view ≥5%=3, ≥2%=2, ≥0.5%=1
          - Comments 0–3 pts: ≥100K=3, ≥10K=2, ≥1K=1
        """
        score = 0
        # Views
        if view_count >= 20_000_000:
            score += 4
        elif view_count >= 5_000_000:
            score += 3
        elif view_count >= 1_000_000:
            score += 2
        elif view_count >= 100_000:
            score += 1

        # Like ratio
        if view_count > 0:
            ratio = like_count / view_count
            if ratio >= 0.05:
                score += 3
            elif ratio >= 0.02:
                score += 2
            elif ratio >= 0.005:
                score += 1

        # Comments
        if comment_count >= 100_000:
            score += 3
        elif comment_count >= 10_000:
            score += 2
        elif comment_count >= 1_000:
            score += 1

        return min(score, 10)

    @staticmethod
    def _derive_sentiment_summary(hype_score: int, total_comments: int) -> str:
        """Translate hype score into a human-readable Korean sentiment label."""
        if hype_score >= 8:
            return "폭발적인 기대감 (초화제작)"
        elif hype_score >= 6:
            return "높은 기대감 (화제작)"
        elif hype_score >= 4:
            return "긍정적 반응 (기대작)"
        elif hype_score >= 2:
            return "관심 증가 중"
        else:
            return "반응 집계 중"
