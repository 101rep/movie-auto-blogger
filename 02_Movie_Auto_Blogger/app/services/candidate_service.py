"""Candidate collection, deduplication, and database persistence service."""
import json
from typing import List, Optional, Set
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector, NormalizedMovie
from app.collectors.tmdb import TMDBMovieProvider
from app.config import get_settings
from app.database.models import Movie, Post, PostStatusEnum
from app.services.scoring_service import CandidateScoringService
from app.utils.logging import get_logger

logger = get_logger("candidate_service")


class CandidateService:
    """Discovers, deduplicates, scores, and persists movie candidates."""

    def __init__(self, collector: Optional[BaseCollector] = None) -> None:
        self.collector = collector or TMDBMovieProvider()
        self.settings = get_settings()

    async def discover_candidates(self) -> List[NormalizedMovie]:
        """Gather diverse candidates from popular, now-playing, upcoming, Korean acclaimed, and OTT endpoints."""
        logger.info("Starting candidate movie discovery across multi-channel endpoints (Theatrical + Korean + OTT)...")
        popular = await self.collector.get_popular_movies(page=1)
        now_playing = await self.collector.get_now_playing_movies(page=1)
        upcoming = await self.collector.get_upcoming_movies(page=1)
        korean = await self.collector.get_korean_movies(years_back=3, page=1)
        ott = await self.collector.get_ott_movies(page=1)

        # Merge and deduplicate candidates within the pool by (source, external_id)
        merged: dict[tuple[str, str], NormalizedMovie] = {}
        for movie in popular + now_playing + upcoming + korean + ott:
            key = (movie.source, movie.external_id)
            if key not in merged:
                merged[key] = movie

        logger.info(
            "Discovered %d unique movie candidates from provider endpoints (Popular: %d, NowPlaying: %d, Upcoming: %d, Korean: %d, OTT: %d).",
            len(merged), len(popular), len(now_playing), len(upcoming), len(korean), len(ott)
        )
        return list(merged.values())

    async def get_by_external_id(self, db: Session, external_id: str, source: str = "tmdb") -> Optional[Movie]:
        """Query movie from DB by external ID."""
        stmt = select(Movie).where(Movie.external_id == str(external_id))
        return db.execute(stmt).scalar_one_or_none()

    def get_ineligible_external_ids(self, db: Session, source: str = "tmdb") -> Set[str]:
        """Find external IDs of movies that must NOT be re-published.

        Criteria:
        - Already published (PUBLISHED, COMPLETED)
        - Already scheduled for future publication (SCHEDULED)
        - Already drafted or generated in admin/test (APPROVED, GENERATED, REVIEW)
        - Currently being generated (GENERATING)
        - Failed generation repeatedly (>= 3 failures)
        """
        # 1. Movies with active / published / scheduled / drafted posts
        active_statuses = [
            PostStatusEnum.PUBLISHED.value,
            PostStatusEnum.COMPLETED.value,
            PostStatusEnum.SCHEDULED.value,
            PostStatusEnum.GENERATED.value,
            PostStatusEnum.APPROVED.value,
            PostStatusEnum.REVIEW.value,
            PostStatusEnum.GENERATING.value,
        ]

        active_query = (
            select(Movie.external_id)
            .join(Post, Post.movie_id == Movie.id)
            .where(Movie.source == source, Post.status.in_(active_statuses))
        )
        active_ids = {str(x) for x in db.execute(active_query).scalars().all() if x}

        # 1-1. Direct Post.external_id (multisite pipeline stores external_id directly on Post)
        active_ext_query = (
            select(Post.external_id)
            .where(Post.external_id.isnot(None), Post.status.in_(active_statuses))
        )
        direct_ext_ids = {str(x) for x in db.execute(active_ext_query).scalars().all() if x}

        # 1-2. Active Post movie_id lookup without source restriction
        active_mids_query = select(Post.movie_id).where(Post.movie_id.isnot(None), Post.status.in_(active_statuses))
        active_mids = set(db.execute(active_mids_query).scalars().all())
        if active_mids:
            ext_from_mids = db.execute(select(Movie.external_id).where(Movie.id.in_(active_mids))).scalars().all()
            direct_ext_ids.update({str(x) for x in ext_from_mids if x})

        # 1-3. Title cross-check: prevent re-selection of movies already mentioned in published titles
        active_titles = [t for t in db.execute(select(Post.title).where(Post.status.in_(active_statuses))).scalars().all() if t]
        if active_titles:
            all_known_movies = db.execute(select(Movie.title, Movie.external_id)).all()
            for m_title, m_ext_id in all_known_movies:
                if m_title and len(m_title.strip()) >= 2:
                    if any(m_title.strip() in pt for pt in active_titles):
                        direct_ext_ids.add(str(m_ext_id))

        # 2. Movies that have failed repeatedly (>= 3 times)
        failed_query = (
            select(Movie.external_id)
            .join(Post, Post.movie_id == Movie.id)
            .where(Movie.source == source, Post.status == PostStatusEnum.FAILED.value)
            .group_by(Movie.external_id)
            .having(func.count(Post.id) >= 3)
        )
        repeatedly_failed_ids = {str(x) for x in db.execute(failed_query).scalars().all() if x}

        ineligible = active_ids | direct_ext_ids | repeatedly_failed_ids
        logger.debug("Identified %d ineligible movies for duplicate prevention.", len(ineligible))
        return ineligible

    async def collect_score_and_persist(
        self,
        db: Session,
        pool_size: Optional[int] = None
    ) -> List[Movie]:
        """Execute complete candidate collection pipeline:

        1. Discover candidates from provider.
        2. Filter out already published/scheduled/ineligible movies.
        3. Score candidates using CandidateScoringService.
        4. Sort descending by score and trim to pool_size.
        5. Persist or update movies in database.
        """
        target_pool_size = pool_size or self.settings.CANDIDATE_POOL_SIZE
        raw_candidates = await self.discover_candidates()
        ineligible_ids = self.get_ineligible_external_ids(db)

        eligible_candidates: List[NormalizedMovie] = []
        for cand in raw_candidates:
            if cand.external_id in ineligible_ids:
                continue
            # Calculate explainable score
            score, breakdown = CandidateScoringService.calculate_score(cand)
            cand.candidate_score = score
            cand.score_breakdown = breakdown
            eligible_candidates.append(cand)

        # Rank candidates by score descending
        eligible_candidates.sort(key=lambda x: (x.candidate_score or 0.0), reverse=True)
        top_candidates = eligible_candidates[:target_pool_size]

        logger.info(
            "Selected and ranked top %d candidates (out of %d eligible).",
            len(top_candidates),
            len(eligible_candidates)
        )

        persisted_movies: List[Movie] = []
        for cand in top_candidates:
            # Check if movie record already exists in DB
            stmt = select(Movie).where(Movie.source == cand.source, Movie.external_id == cand.external_id)
            existing_movie = db.execute(stmt).scalar_one_or_none()

            genres_json = json.dumps(cand.genres, ensure_ascii=False) if cand.genres else None
            cast_json = json.dumps(cand.major_cast, ensure_ascii=False) if cand.major_cast else None
            raw_json_str = json.dumps(cand.raw_json, ensure_ascii=False) if cand.raw_json else None

            if existing_movie:
                # Update scores and latest metadata
                existing_movie.title = cand.title
                existing_movie.original_title = cand.original_title
                existing_movie.overview = cand.overview
                existing_movie.release_date = cand.release_date
                existing_movie.popularity = cand.popularity
                existing_movie.vote_average = cand.vote_average
                existing_movie.vote_count = cand.vote_count
                existing_movie.candidate_score = cand.candidate_score
                if cand.poster_reference:
                    existing_movie.poster_reference = cand.poster_reference
                if cand.backdrop_reference:
                    existing_movie.backdrop_reference = cand.backdrop_reference
                persisted_movies.append(existing_movie)
            else:
                new_movie = Movie(
                    source=cand.source,
                    external_id=cand.external_id,
                    title=cand.title,
                    original_title=cand.original_title,
                    overview=cand.overview,
                    release_date=cand.release_date,
                    runtime=cand.runtime,
                    genres_json=genres_json,
                    original_language=cand.original_language,
                    popularity=cand.popularity,
                    vote_average=cand.vote_average,
                    vote_count=cand.vote_count,
                    director=cand.director,
                    cast_json=cast_json,
                    poster_reference=cand.poster_reference,
                    backdrop_reference=cand.backdrop_reference,
                    raw_json=raw_json_str,
                    candidate_score=cand.candidate_score
                )
                db.add(new_movie)
                persisted_movies.append(new_movie)

        db.commit()
        for m in persisted_movies:
            db.refresh(m)

        return persisted_movies
