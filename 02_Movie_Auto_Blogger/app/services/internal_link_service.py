"""Deterministic internal linking service with anchor recommendation, orphan detection, and concentration control."""
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database.models import Movie, Post, PostStatusEnum
from app.utils.logging import get_logger

logger = get_logger("internal_link_service")


class InternalLinkService:
    """Discovers confirmed published posts for deterministic internal linking with anchor optimization."""

    @staticmethod
    def generate_anchor_recommendation(source_movie: Movie, target_movie: Movie, target_post: Post) -> str:
        """Generate diverse natural anchor text based on relationship context."""
        # 1. Same Director
        if source_movie.director and target_movie.director and source_movie.director == target_movie.director:
            return f"{source_movie.director} 감독의 또 다른 대표작 《{target_movie.title}》 줄거리 및 해석"

        # 2. Shared Cast
        if source_movie.cast_json and target_movie.cast_json:
            try:
                s_cast = set(json.loads(source_movie.cast_json))
                t_cast = set(json.loads(target_movie.cast_json))
                shared = list(s_cast & t_cast)
                if shared:
                    return f"배우 {shared[0]} 출연 영화 《{target_movie.title}》 관람 가이드"
            except Exception:
                pass

        # 3. Default high-CTR anchor
        return f"함께 보면 좋은 영화 《{target_movie.title}》 리뷰"

    @classmethod
    def get_related_links(
        cls,
        db: Session,
        current_movie: Movie,
        limit: int = 3
    ) -> List[Dict[str, str]]:
        """Find related published WordPress posts with contextual anchor recommendations."""
        # Find published posts with confirmed remote URLs
        query = (
            select(Post)
            .join(Movie, Movie.id == Post.movie_id)
            .where(
                Post.status == PostStatusEnum.PUBLISHED.value,
                Post.wordpress_url.isnot(None),
                Movie.id != current_movie.id
            )
        )

        candidates = db.execute(query).scalars().all()
        if not candidates:
            return []

        # Count existing inbound occurrences across published articles to penalize over-concentrated links
        inbound_counts: Dict[int, int] = {}
        all_published = db.query(Post).filter(
            Post.status == PostStatusEnum.PUBLISHED.value,
            Post.rendered_content.isnot(None)
        ).all()
        for cand in candidates:
            inbound_counts[cand.id] = 0
            if cand.wordpress_url:
                for pub in all_published:
                    if pub.rendered_content and cand.wordpress_url in pub.rendered_content:
                        inbound_counts[cand.id] += 1

        scored_links = []
        current_genres = set(json.loads(current_movie.genres_json)) if current_movie.genres_json else set()
        current_cast = set(json.loads(current_movie.cast_json)) if current_movie.cast_json else set()
        current_director = current_movie.director

        for p in candidates:
            rel_score = 0
            other_m = p.movie
            if not other_m:
                continue

            # Same director bonus
            if current_director and other_m.director and current_director == other_m.director:
                rel_score += 10

            # Overlapping cast
            if other_m.cast_json and current_cast:
                other_cast = set(json.loads(other_m.cast_json))
                rel_score += len(current_cast & other_cast) * 4

            # Overlapping genre
            if other_m.genres_json and current_genres:
                other_genres = set(json.loads(other_m.genres_json))
                rel_score += len(current_genres & other_genres) * 2

            # Concentration penalty: If post already has >= 3 inbound links, dampen its score
            existing_inbound = inbound_counts.get(p.id, 0)
            if existing_inbound >= 3:
                rel_score = max(1, rel_score - (existing_inbound * 2))

            if rel_score > 0:
                anchor = cls.generate_anchor_recommendation(current_movie, other_m, p)
                scored_links.append((rel_score, p, anchor))

        # Sort descending by relevance score
        scored_links.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, p, anchor in scored_links[:limit]:
            results.append({
                "title": p.title,
                "url": p.wordpress_url,
                "anchor_text": anchor,
                "relevance_score": score
            })

        logger.info("Found %d internal links for '%s'", len(results), current_movie.title)
        return results

    @staticmethod
    def detect_orphan_pages(db: Session) -> List[Dict[str, Any]]:
        """Identify published posts that have zero inbound internal links from other articles."""
        published_posts = db.query(Post).filter(
            Post.status == PostStatusEnum.PUBLISHED.value,
            Post.wordpress_url.isnot(None)
        ).all()

        if not published_posts:
            return []

        orphan_list: List[Dict[str, Any]] = []
        for target in published_posts:
            target_url = target.wordpress_url
            if not target_url:
                continue

            inbound_count = 0
            for source in published_posts:
                if source.id != target.id and source.rendered_content and target_url in source.rendered_content:
                    inbound_count += 1

            if inbound_count == 0:
                orphan_list.append({
                    "post_id": target.id,
                    "title": target.title,
                    "slug": target.slug,
                    "url": target.wordpress_url,
                    "movie_title": target.movie.title if target.movie else "-",
                    "inbound_links": 0,
                    "recommendation": "다른 관련 영화 글의 본문 또는 하단에 내부 링크 연결 필요"
                })

        logger.info("Detected %d orphan page(s) among %d published posts", len(orphan_list), len(published_posts))
        return orphan_list

    @classmethod
    def get_related_travel_links(
        cls,
        db: Session,
        current_destination: str,
        current_post_id: Optional[int] = None,
        limit: int = 3
    ) -> List[Dict[str, str]]:
        """Find related published/scheduled travel posts with contextual anchor text."""
        query = (
            select(Post)
            .where(
                Post.vertical == "TRAVEL",
                Post.status.in_([PostStatusEnum.PUBLISHED.value, PostStatusEnum.SCHEDULED.value]),
                Post.wordpress_url.isnot(None)
            )
        )
        if current_post_id:
            query = query.where(Post.id != current_post_id)

        candidates = db.execute(query).scalars().all()
        if not candidates:
            return []

        # Simple country / destination relevance scoring
        clean_curr = re.sub(r'\(.*?\)', '', current_destination).strip()
        scored = []
        for p in candidates:
            if clean_curr in p.title:
                continue  # Skip identical destination
            score = 5
            # Generate anchor recommendation
            anchor = f"함께 떠나기 좋은 추천 여행지 《{p.title}》"
            scored.append((score, p, anchor))

        results = []
        for score, p, anchor in scored[:limit]:
            results.append({
                "title": p.title,
                "url": p.wordpress_url,
                "anchor_text": anchor,
                "relevance_score": score
            })

        logger.info("Found %d travel internal links for '%s'", len(results), current_destination)
        return results

