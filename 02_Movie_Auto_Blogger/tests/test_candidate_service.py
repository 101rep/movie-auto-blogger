"""Unit tests for candidate discovery, deduplication, and persistence service."""
import pytest
from unittest.mock import AsyncMock
from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector, NormalizedMovie
from app.database.models import Movie, Post, PostStatusEnum
from app.services.candidate_service import CandidateService


class MockCollector(BaseCollector):
    """Mock collector returning controlled test movies."""

    def __init__(self):
        self.popular_list = [
            NormalizedMovie(external_id="101", title="영화 101 (인기)", popularity=100.0, release_date="2024-06-01"),
            NormalizedMovie(external_id="102", title="영화 102 (인기/상영중 중복)", popularity=90.0, release_date="2024-06-05"),
        ]
        self.now_playing_list = [
            NormalizedMovie(external_id="102", title="영화 102 (인기/상영중 중복)", popularity=90.0, release_date="2024-06-05"),
            NormalizedMovie(external_id="103", title="영화 103 (상영중)", popularity=80.0, release_date="2024-06-10"),
        ]
        self.upcoming_list = [
            NormalizedMovie(external_id="104", title="영화 104 (개봉예정)", popularity=70.0, release_date="2024-07-01"),
        ]

    async def health_check(self):
        return {"success": True, "message": "Mock OK"}

    async def get_popular_movies(self, page: int = 1):
        return self.popular_list

    async def get_now_playing_movies(self, page: int = 1):
        return self.now_playing_list

    async def get_upcoming_movies(self, page: int = 1):
        return self.upcoming_list

    async def get_movie_details(self, movie_id: str):
        return None

    async def get_movie_credits(self, movie_id: str):
        return {}

    async def get_image_metadata(self, movie_id: str):
        return {}


@pytest.mark.asyncio
async def test_candidate_intra_pool_deduplication():
    """Verify movies appearing in multiple provider lists (e.g. popular & now playing) are merged."""
    collector = MockCollector()
    service = CandidateService(collector=collector)

    candidates = await service.discover_candidates()
    # 101, 102, 103, 104 -> total 4 unique movies
    assert len(candidates) == 4
    ext_ids = [c.external_id for c in candidates]
    assert ext_ids.count("102") == 1


@pytest.mark.asyncio
async def test_candidate_db_deduplication_published_and_scheduled(db_session: Session):
    """Verify that published or scheduled movies are excluded from candidates."""
    collector = MockCollector()
    service = CandidateService(collector=collector)

    # Pre-seed movie 101 as PUBLISHED
    movie101 = Movie(source="tmdb", external_id="101", title="영화 101")
    db_session.add(movie101)
    db_session.commit()

    post101 = Post(
        movie_id=movie101.id,
        title="영화 101 리뷰",
        slug="movie-101-review",
        status=PostStatusEnum.PUBLISHED.value
    )
    db_session.add(post101)
    db_session.commit()

    ineligible = service.get_ineligible_external_ids(db_session)
    assert "101" in ineligible
    assert "102" not in ineligible


@pytest.mark.asyncio
async def test_candidate_db_deduplication_repeated_failures(db_session: Session):
    """Verify movies that failed generation >= 3 times are excluded."""
    collector = MockCollector()
    service = CandidateService(collector=collector)

    # Pre-seed movie 103 with 3 failed posts
    movie103 = Movie(source="tmdb", external_id="103", title="영화 103")
    db_session.add(movie103)
    db_session.commit()

    for i in range(3):
        post = Post(
            movie_id=movie103.id,
            title=f"영화 103 실패 시도 {i+1}",
            slug=f"movie-103-attempt-{i+1}",
            status=PostStatusEnum.FAILED.value
        )
        db_session.add(post)
    db_session.commit()

    ineligible = service.get_ineligible_external_ids(db_session)
    assert "103" in ineligible


@pytest.mark.asyncio
async def test_collect_score_and_persist_pipeline(db_session: Session):
    """Verify candidates are scored, ranked, and stored in the database without duplicates."""
    collector = MockCollector()
    service = CandidateService(collector=collector)

    # Collect top 2 candidates
    persisted = await service.collect_score_and_persist(db_session, pool_size=2)
    assert len(persisted) == 2
    assert persisted[0].candidate_score >= persisted[1].candidate_score

    # Rerun the pipeline: existing movies must be updated, not fail unique constraint
    persisted_rerun = await service.collect_score_and_persist(db_session, pool_size=2)
    assert len(persisted_rerun) == 2

    # Verify count in DB is still 2
    total_db_movies = db_session.query(Movie).count()
    assert total_db_movies == 2
