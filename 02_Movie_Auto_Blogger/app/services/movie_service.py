"""High-level movie coordinator and diagnostic service."""
import json
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector, NormalizedMovie
from app.collectors.tmdb import TMDBMovieProvider
from app.database.models import Movie
from app.utils.logging import get_logger

logger = get_logger("movie_service")


class MovieService:
    """Service providing movie detail enrichment and connection health testing."""

    def __init__(self, collector: Optional[BaseCollector] = None) -> None:
        self.collector = collector or TMDBMovieProvider()

    async def test_connection(self) -> Dict[str, Any]:
        """Perform provider connection test returning clean, user-friendly diagnostics."""
        logger.info("Executing Movie API connection test...")
        return await self.collector.health_check()

    async def enrich_movie_details(self, db: Session, movie: Movie) -> Movie:
        """Fetch deep details (director, cast, runtime, and global/domestic ratings) and update DB record."""
        # 1. Enrich credits & external IDs from TMDB collector if missing
        if not (movie.director and movie.cast_json and movie.runtime):
            logger.info("Enriching movie details for '%s' (ID: %s)...", movie.title, movie.external_id)
            detailed_movie = await self.collector.get_movie_details(movie.external_id)
            if detailed_movie:
                if detailed_movie.director:
                    movie.director = detailed_movie.director
                if detailed_movie.major_cast:
                    movie.cast_json = json.dumps(detailed_movie.major_cast, ensure_ascii=False)
                if detailed_movie.runtime:
                    movie.runtime = detailed_movie.runtime
                if detailed_movie.overview and not movie.overview:
                    movie.overview = detailed_movie.overview
                if detailed_movie.genres and not movie.genres_json:
                    movie.genres_json = json.dumps(detailed_movie.genres, ensure_ascii=False)
                if detailed_movie.imdb_id and not getattr(movie, "imdb_id", None):
                    movie.imdb_id = detailed_movie.imdb_id

        # 2. Fetch and aggregate Global + Domestic Ratings (IMDb, Rotten Tomatoes, Metacritic, Naver, Watcha, TMDB)
        try:
            from app.services.global_rating_service import GlobalRatingService
            ratings = await GlobalRatingService.aggregate_ratings(
                title=movie.title,
                original_title=movie.original_title,
                release_date=movie.release_date,
                imdb_id=getattr(movie, "imdb_id", None),
                tmdb_vote_average=movie.vote_average,
                tmdb_vote_count=movie.vote_count,
                naver_rating=getattr(movie, "naver_rating", None),
                naver_rating_type=getattr(movie, "naver_rating_type", None),
                naver_vote_count=getattr(movie, "naver_vote_count", None)
            )
            if ratings:
                if ratings.imdb_id and not getattr(movie, "imdb_id", None):
                    movie.imdb_id = ratings.imdb_id
                if ratings.imdb_rating is not None:
                    movie.imdb_rating = ratings.imdb_rating
                if ratings.imdb_votes:
                    movie.imdb_votes = ratings.imdb_votes
                if ratings.rotten_tomatoes_score:
                    movie.rotten_tomatoes_score = ratings.rotten_tomatoes_score
                if ratings.metacritic_score:
                    movie.metacritic_score = ratings.metacritic_score
                if ratings.watcha_rating is not None:
                    movie.watcha_rating = ratings.watcha_rating
                if ratings.naver_rating is not None:
                    movie.naver_rating = ratings.naver_rating
                if ratings.naver_rating_type:
                    movie.naver_rating_type = ratings.naver_rating_type
                if ratings.naver_vote_count:
                    movie.naver_vote_count = ratings.naver_vote_count
        except Exception as ge:
            logger.warning("Could not aggregate global ratings for '%s': %s", movie.title, str(ge))

        db.commit()
        db.refresh(movie)
        return movie
