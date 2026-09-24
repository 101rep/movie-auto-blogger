"""Tests for Phase 6: Content Cluster Hub & Spoke Engine."""
import pytest
from app.database.models import Movie
from app.services.cluster_service import (
    ClusterIntent,
    ClusterService,
    MovieClusterPlan,
)


def test_generate_cluster_plan_structure():
    """Verify cluster plan creates 1 primary hub and multiple spoke articles."""
    movie = Movie(
        id=55,
        title="파묘",
        director="장재현",
        release_date="2024-02-22",
        popularity=250.0
    )

    plan: MovieClusterPlan = ClusterService.generate_cluster_plan(movie)

    assert plan.movie_id == 55
    assert "파묘" in plan.movie_title
    assert plan.primary_topic.is_primary is True
    assert plan.primary_topic.intent == ClusterIntent.PILLAR_REVIEW
    assert "파묘" in plan.primary_topic.target_keyword

    assert len(plan.supporting_topics) >= 4
    intents = [s.intent for s in plan.supporting_topics]
    assert ClusterIntent.ENDING_EXPLAINED in intents
    assert ClusterIntent.POST_CREDIT in intents
    assert ClusterIntent.OTT_PLATFORM in intents
    assert ClusterIntent.CAST_ANALYSIS in intents

    assert plan.total_planned_articles == 1 + len(plan.supporting_topics)


def test_internal_link_strategy_generation():
    """Verify internal link strategy is explicitly designed."""
    movie = Movie(
        id=56,
        title="베놈: 라스트 댄스",
        director="켈리 마르셀",
        release_date="2024-10-23"
    )
    plan = ClusterService.generate_cluster_plan(movie)

    assert len(plan.internal_link_strategy) >= 2
    assert any("메인 필러" in s for s in plan.internal_link_strategy)


def test_intent_scores_are_valid():
    """Verify all intent opportunity scores are within 0 to 100."""
    movie = Movie(
        id=57,
        title="인터스텔라",
        director="크리스토퍼 놀란"
    )
    plan = ClusterService.generate_cluster_plan(movie)

    assert 0.0 <= plan.primary_topic.intent_score <= 100.0
    for spoke in plan.supporting_topics:
        assert 0.0 <= spoke.intent_score <= 100.0
