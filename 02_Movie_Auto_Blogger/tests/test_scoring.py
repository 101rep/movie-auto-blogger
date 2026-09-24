"""Unit tests for the explainable candidate movie scoring engine."""
from datetime import date
from app.collectors.base import NormalizedMovie
from app.services.scoring_service import CandidateScoringService


def test_candidate_scoring_components():
    """Verify that score components are correctly computed and sum up."""
    ref_date = date(2024, 6, 15)

    movie = NormalizedMovie(
        external_id="101",
        title="인사이드 아웃 2",
        overview="13살이 된 라일리의 감정 컨트롤 본부에 불안, 당황 등 새로운 감정들이 찾아오면서 벌어지는 이야기.",
        release_date="2024-06-12",
        popularity=500.0,
        vote_average=8.0,
        vote_count=2000,
        director="켈시 만",
        major_cast=["에이미 포일러", "마야 호크", "필리스 스미스", "루이스 블랙"],
        poster_reference="https://image.tmdb.org/t/p/w780/poster.jpg"
    )

    total_score, breakdown = CandidateScoringService.calculate_score(movie, reference_date=ref_date)

    # Popularity: log10(501) * 11.6 ~= 31.32
    assert 25.0 <= breakdown["popularity_score"] <= 35.0
    # Recency: release is 3 days before reference date -> 30.0 pts
    assert breakdown["recency_score"] == 30.0
    # Rating: vote_average 8.0 * 2.0 = 16.0 pts
    assert breakdown["rating_score"] == 16.0
    # Completeness: overview(4) + poster(4) + director(3) + cast(4) = 15.0 pts
    assert breakdown["completeness_score"] == 15.0

    # Total should be close to 90+
    assert total_score >= 85.0
    assert total_score == round(
        breakdown["popularity_score"] +
        breakdown["recency_score"] +
        breakdown["rating_score"] +
        breakdown["completeness_score"],
        2
    )


def test_scoring_relative_ranking():
    """Verify that a popular recent release ranks higher than an obscure old release."""
    ref_date = date(2024, 6, 15)

    recent_hit = NormalizedMovie(
        external_id="1",
        title="최신 대작 영화",
        overview="충분히 긴 줄거리 정보가 담겨있는 최신 개봉 대작 영화입니다.",
        release_date="2024-06-10",
        popularity=800.0,
        vote_average=8.2,
        vote_count=500,
        director="유명 감독",
        major_cast=["배우A", "배우B", "배우C"],
        poster_reference="https://image.tmdb.org/poster.jpg"
    )

    obscure_old = NormalizedMovie(
        external_id="2",
        title="오래된 독립 단편 영화",
        overview=None,
        release_date="1995-01-01",
        popularity=1.5,
        vote_average=5.0,
        vote_count=5,
        director=None,
        major_cast=[],
        poster_reference=None
    )

    score_hit, _ = CandidateScoringService.calculate_score(recent_hit, reference_date=ref_date)
    score_old, _ = CandidateScoringService.calculate_score(obscure_old, reference_date=ref_date)

    assert score_hit > score_old
    assert score_hit > 75.0
    assert score_old < 25.0
