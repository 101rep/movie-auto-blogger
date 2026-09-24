"""Tests for Phase 9 (Internal Link Optimization) and Phase 10 (Learning Engine)."""
import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base, Movie, Post, PostStatusEnum, utc_now
from app.services.internal_link_service import InternalLinkService
from app.services.learning_service import (
    LearningDataStatus,
    LearningEngineService,
    StrategyRecommendation,
)


@pytest.fixture
def db_session():
    """In-memory SQLite session for linking and learning tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_anchor_recommendation_director_match():
    """Verify natural anchor text when director matches."""
    m1 = Movie(id=1, external_id="m1", title="인셉션", director="크리스토퍼 놀란")
    m2 = Movie(id=2, external_id="m2", title="인터스텔라", director="크리스토퍼 놀란")
    p2 = Post(id=2, movie_id=2, title="인터스텔라 리뷰", slug="interstellar-review")

    anchor = InternalLinkService.generate_anchor_recommendation(m1, m2, p2)
    assert "크리스토퍼 놀란" in anchor
    assert "인터스텔라" in anchor


def test_anchor_recommendation_cast_match():
    """Verify natural anchor text when cast overlaps."""
    m1 = Movie(id=1, external_id="m1", title="인셉션", director="놀란", cast_json='["레오나르도 디카프리오"]')
    m2 = Movie(id=3, external_id="m3", title="셔터 아일랜드", director="스콜세지", cast_json='["레오나르도 디카프리오"]')
    p3 = Post(id=3, movie_id=3, title="셔터 아일랜드 리뷰", slug="shutter-island-review")

    anchor = InternalLinkService.generate_anchor_recommendation(m1, m2, p3)
    assert "레오나르도 디카프리오" in anchor
    assert "셔터 아일랜드" in anchor


def test_orphan_page_detection(db_session):
    """Verify detect_orphan_pages finds published articles without inbound links."""
    m1 = Movie(id=1, external_id="m1", title="Movie 1")
    m2 = Movie(id=2, external_id="m2", title="Movie 2")
    m3 = Movie(id=3, external_id="m3", title="Movie 3")
    db_session.add_all([m1, m2, m3])
    db_session.commit()

    # Post 1 links to Post 2
    p1 = Post(
        id=1, movie_id=1, title="Post 1", slug="post-1",
        status=PostStatusEnum.PUBLISHED.value,
        wordpress_url="https://site.com/post-1",
        rendered_content="<p>Check out <a href='https://site.com/post-2'>Movie 2</a></p>"
    )
    # Post 2 has inbound link from Post 1
    p2 = Post(
        id=2, movie_id=2, title="Post 2", slug="post-2",
        status=PostStatusEnum.PUBLISHED.value,
        wordpress_url="https://site.com/post-2",
        rendered_content="<p>Review of Movie 2</p>"
    )
    # Post 3 is an orphan (no inbound link from anywhere)
    p3 = Post(
        id=3, movie_id=3, title="Post 3 (Orphan)", slug="post-3",
        status=PostStatusEnum.PUBLISHED.value,
        wordpress_url="https://site.com/post-3",
        rendered_content="<p>Isolated review</p>"
    )
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    orphans = InternalLinkService.detect_orphan_pages(db_session)
    orphan_slugs = [o["slug"] for o in orphans]

    assert "post-3" in orphan_slugs
    assert "post-2" not in orphan_slugs


def test_learning_engine_insufficient_data(db_session):
    """Verify learning engine returns INSUFFICIENT_DATA when sample size < 5."""
    # Add only 2 posts
    m = Movie(id=1, external_id="m1", title="M1")
    p = Post(id=1, movie_id=1, title="P1", slug="p1", status=PostStatusEnum.PUBLISHED.value)
    db_session.add_all([m, p])
    db_session.commit()

    strategy: StrategyRecommendation = LearningEngineService.analyze_strategy(db_session)
    assert strategy.status == LearningDataStatus.INSUFFICIENT_DATA
    assert strategy.sample_size == 1
    assert len(strategy.top_performing_genres) > 0


def test_learning_engine_sufficient_data_insights(db_session):
    """Verify learning engine derives top genres and insights when sample size >= 5."""
    movies = []
    posts = []
    for i in range(1, 7):
        genre = "SF" if i % 2 == 0 else "Action"
        m = Movie(
            id=i, external_id=f"tmdb-{i}", title=f"Film {i}",
            genres_json=json.dumps([genre]),
            candidate_score=85.0
        )
        p = Post(
            id=i, movie_id=i, title=f"Review {i}", slug=f"review-{i}",
            status=PostStatusEnum.PUBLISHED.value
        )
        movies.append(m)
        posts.append(p)

    db_session.add_all(movies)
    db_session.add_all(posts)
    db_session.commit()

    strategy: StrategyRecommendation = LearningEngineService.analyze_strategy(db_session)
    assert strategy.status == LearningDataStatus.SUFFICIENT_DATA
    assert strategy.sample_size >= 6
    assert len(strategy.genre_statistics) >= 2
    assert any(g in strategy.top_performing_genres for g in ["SF", "Action"])
    assert len(strategy.actionable_insights) >= 3
