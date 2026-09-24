"""Tests for Phase 5: AI Writer -> Editor -> SEO Pipeline."""
import pytest
from app.ai.schemas import ArticleOutput, FAQItem
from app.database.models import Movie
from app.services.pipeline_service import (
    ContentPipeline,
    PipelineTier,
)
from tests.test_phase4_fact_checker import create_sample_article


@pytest.fixture
def sample_movie():
    return Movie(
        id=10,
        title="인셉션",
        director="크리스토퍼 놀란",
        release_date="2010-07-21",
        runtime=148,
        cast_json='["레오나르도 디카프리오", "조셉 고든 레빗"]'
    )


@pytest.mark.asyncio
async def test_pipeline_basic_tier(sample_movie):
    """Verify BASIC tier executes Writer and Fact Checker only."""
    article = create_sample_article()
    result = await ContentPipeline.run_pipeline(article, sample_movie, tier=PipelineTier.BASIC)

    assert result.tier == PipelineTier.BASIC
    assert result.stages_executed == ["WRITER", "FACT_CHECKER"]
    assert result.fact_report is not None
    assert result.is_publish_ready is True
    assert len(result.editorial_notes) == 0
    assert len(result.seo_notes) == 0


@pytest.mark.asyncio
async def test_pipeline_standard_tier_with_editor(sample_movie):
    """Verify STANDARD tier executes Editor and refines robotic expressions."""
    raw_article = create_sample_article()
    # Inject cliches
    updated_dict = raw_article.model_dump()
    updated_dict["introduction"] = "요약하자면, 영화 인셉션은 정말 매우 훌륭한 작품입니다. " + updated_dict["introduction"]
    updated_dict["conclusion"] = "결론적으로 말하자면, " + updated_dict["conclusion"]
    article = ArticleOutput.model_validate(updated_dict)

    result = await ContentPipeline.run_pipeline(article, sample_movie, tier=PipelineTier.STANDARD)

    assert result.tier == PipelineTier.STANDARD
    assert result.stages_executed == ["RESEARCH", "WRITER", "EDITOR", "FACT_CHECKER"]
    assert len(result.editorial_notes) > 0
    assert "요약하자면," not in result.article.introduction
    assert "한마디로 정리하면," in result.article.introduction
    assert "결론적으로 말하자면," not in result.article.conclusion


@pytest.mark.asyncio
async def test_pipeline_full_tier_with_seo_optimization(sample_movie):
    """Verify FULL tier optimizes SEO title, meta description, and tags."""
    article = create_sample_article()
    # Remove movie title from seo fields to test auto-enrichment
    updated_dict = article.model_dump()
    updated_dict["seo_title"] = "SF 걸작 영화 심층 리뷰 및 결말 해석 가이드"
    updated_dict["meta_description"] = "꿈과 무의식의 세계를 다룬 걸작 영화를 리뷰합니다."
    updated_dict["tags"] = ["SF", "명작"]
    unoptimized = ArticleOutput.model_validate(updated_dict)

    result = await ContentPipeline.run_pipeline(unoptimized, sample_movie, tier=PipelineTier.FULL)

    assert result.tier == PipelineTier.FULL
    assert result.stages_executed == ["RESEARCH", "WRITER", "EDITOR", "FACT_CHECKER", "SEO_OPTIMIZER"]
    assert len(result.seo_notes) > 0
    assert "인셉션" in result.article.seo_title
    assert "인셉션" in result.article.meta_description
    assert "인셉션" in result.article.tags
    assert sample_movie.director in result.article.tags
    assert len(result.article.tags) <= 8


@pytest.mark.asyncio
async def test_facts_over_seo_priority(sample_movie):
    """Verify that fact conflict prevents publication even if SEO is optimal."""
    # Bad article with conflicting director
    bad_article = create_sample_article(
        title="영화 인셉션 완벽 분석: 봉준호 감독의 작품",
        director_text="봉준호 감독이 연출한 블록버스터로",
        director_faq_name="봉준호"
    )

    result = await ContentPipeline.run_pipeline(bad_article, sample_movie, tier=PipelineTier.FULL)

    assert result.fact_report.has_fatal_conflict is True
    assert result.is_publish_ready is False
