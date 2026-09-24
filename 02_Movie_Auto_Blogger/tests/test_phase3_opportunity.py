"""Tests for Phase 3: Content Opportunity Engine."""
from datetime import date, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base, Movie, Post, PostStatusEnum, utc_now
from app.services.opportunity_service import (
    DefaultTrendProvider,
    OpportunityService,
    TrendSignal,
)


@pytest.fixture
def db_session():
    """In-memory SQLite session for opportunity service testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_trend_provider_not_configured():
    """Verify fallback behavior when external trend API is not configured."""
    provider = DefaultTrendProvider(is_configured=False)
    signal = await provider.get_trend_signal("베놈: 라스트 댄스")

    assert signal.status == "NOT_CONFIGURED"
    assert signal.trend_score == 50.0
    assert signal.provider_name == "DefaultTrendFallback"


@pytest.mark.asyncio
async def test_calculate_opportunity_score_breakdown():
    """Verify explainable score breakdown and bounds."""
    service = OpportunityService()
    movie = Movie(
        id=1,
        external_id="tmdb-101",
        title="Dune: Part Two",
        release_date=date.today().strftime("%Y-%m-%d"),
        popularity=150.5,
        vote_average=8.5,
        vote_count=500,
        overview="A boy becomes the Messiah of nomads on a desert planet.",
        poster_reference="https://image.tmdb.org/t/p/w500/test.jpg",
        director="Denis Villeneuve",
        cast_json='["Timothee Chalamet", "Zendaya", "Rebecca Ferguson"]'
    )

    signal = TrendSignal(
        provider_name="TestProvider",
        status="CONFIGURED",
        trend_score=85.0,
        search_volume_index=85.0,
        relative_momentum=20.0
    )

    score, breakdown = service.calculate_opportunity_score(movie, trend_signal=signal)

    assert 0.0 <= score <= 100.0
    assert breakdown.total_score == score
    assert breakdown.trend_factor > 0
    assert breakdown.recency_factor >= 20.0  # Just released D-Day bonus
    assert breakdown.rating_quality_factor > 10.0
    assert breakdown.completeness_factor > 10.0
    assert breakdown.competition_factor > 0
    assert len(breakdown.highlights) > 0


@pytest.mark.asyncio
async def test_duplicate_penalty_excludes_published_movie(db_session):
    """Verify that an already published movie receives duplicate penalty and 0 score."""
    service = OpportunityService()
    movie = Movie(
        id=2,
        external_id="tmdb-102",
        title="Already Published Movie",
        release_date="2026-01-01",
        popularity=200.0,
        vote_average=9.0,
        vote_count=1000
    )
    db_session.add(movie)
    db_session.commit()

    # Add post with valid non-null slug
    post = Post(
        movie_id=2,
        title="Already Published Post",
        slug="already-published-post",
        status=PostStatusEnum.PUBLISHED.value,
        published_at=utc_now()
    )
    db_session.add(post)
    db_session.commit()

    score, breakdown = service.calculate_opportunity_score(movie, db=db_session)

    assert score == 0.0
    assert breakdown.duplicate_penalty == -100.0
    assert any("발행 제외" in h for h in breakdown.highlights)


@pytest.mark.asyncio
async def test_get_top_opportunities_ranking(db_session):
    """Verify top opportunities are retrieved and ordered descending by score."""
    service = OpportunityService()
    today_str = date.today().strftime("%Y-%m-%d")
    old_date = (date.today() - timedelta(days=500)).strftime("%Y-%m-%d")

    m1 = Movie(
        id=10, external_id="m1", title="Hit Movie 1", release_date=today_str,
        popularity=300.0, vote_average=8.8, vote_count=800,
        overview="Full overview with plenty of text describing the storyline.",
        poster_reference="poster1.jpg", director="Director A", cast_json='["Actor 1", "Actor 2"]'
    )
    m2 = Movie(
        id=20, external_id="m2", title="Old Movie 2", release_date=old_date,
        popularity=10.0, vote_average=5.0, vote_count=20,
        overview="Brief", poster_reference=None
    )
    m3 = Movie(
        id=30, external_id="m3", title="Medium Movie 3", release_date=today_str,
        popularity=80.0, vote_average=7.2, vote_count=200,
        overview="Good plot details for this nice medium film.",
        poster_reference="poster3.jpg", director="Director C", cast_json='["Actor 5"]'
    )
    db_session.add_all([m1, m2, m3])
    db_session.commit()

    top_opps = await service.get_top_opportunities(db_session, pool_size=10, top_n=2)

    assert len(top_opps) == 2
    assert top_opps[0].title == "Hit Movie 1"
    assert top_opps[0].opportunity_score >= top_opps[1].opportunity_score
    assert top_opps[0].status == "HIGH_OPPORTUNITY"
