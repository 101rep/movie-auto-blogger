"""Multi-stage AI Content Pipeline: Writer -> Editor -> Fact Checker -> SEO Optimizer."""
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.ai.schemas import ArticleOutput
from app.database.models import Movie
from app.services.fact_check_service import FactCheckReport, FactCheckService
from app.utils.logging import get_logger

logger = get_logger("content_pipeline")


class PipelineTier(str, Enum):
    """Pipeline execution tiers balancing speed and depth."""
    BASIC = "BASIC"          # Fast: Writer + Fact Checker
    STANDARD = "STANDARD"    # Balanced: Research + Writer + Editor + Fact Checker
    FULL = "FULL"            # Comprehensive: Research + Writer + Editor + Fact Checker + SEO Optimizer


class PipelineResult(BaseModel):
    """Result of running the content creation pipeline."""
    tier: PipelineTier
    stages_executed: List[str] = Field(default_factory=list)
    article: ArticleOutput
    fact_report: Optional[FactCheckReport] = None
    editorial_notes: List[str] = Field(default_factory=list)
    seo_notes: List[str] = Field(default_factory=list)
    is_publish_ready: bool = True
    summary: str = ""


class ContentPipeline:
    """Orchestrates sequential content refining stages: Research -> Write -> Edit -> Fact -> SEO."""

    @staticmethod
    def edit_article(article: ArticleOutput, movie: Movie) -> Tuple[ArticleOutput, List[str]]:
        """Editor stage: Refines tone, removes robotic repetitive cliches, and enhances flow."""
        notes: List[str] = []
        # Target cliches to clean up
        cliches = [
            ("결론적으로 말하자면,", "총평하자면,"),
            ("요약하자면,", "한마디로 정리하면,"),
            ("말할 것도 없이,", "분명하게도,"),
            ("다시 말해,", "즉,"),
        ]

        # Clean introduction
        intro = article.introduction
        for old, new in cliches:
            if old in intro:
                intro = intro.replace(old, new)
                notes.append(f"도입부 진부한 어구 교체: '{old}' -> '{new}'")

        # Clean conclusion
        conclusion = article.conclusion
        for old, new in cliches:
            if old in conclusion:
                conclusion = conclusion.replace(old, new)
                notes.append(f"결론부 어구 자연스럽게 개선: '{old}' -> '{new}'")

        # Check for repetitive word density (e.g. excessive '매우', '정말')
        full_text = f"{intro} {article.spoiler_free_synopsis} {conclusion}"
        for overused in ["정말", "매우", "엄청난"]:
            count = len(re.findall(rf"\b{overused}\b", full_text))
            if count > 4:
                notes.append(f"과도하게 반복된 수식어('{overused}' {count}회) 절제 권고")

        # Create updated ArticleOutput
        updated_dict = article.model_dump()
        updated_dict["introduction"] = intro
        updated_dict["conclusion"] = conclusion
        refined_article = ArticleOutput.model_validate(updated_dict)

        return refined_article, notes

    @staticmethod
    def optimize_seo(article: ArticleOutput, movie: Movie) -> Tuple[ArticleOutput, List[str]]:
        """SEO Optimizer stage: Enhances title, meta description, and keywords without altering facts."""
        seo_notes: List[str] = []
        updated_dict = article.model_dump()

        # 1. Optimize SEO Title: ensure movie title is prominently placed and length is 30-55 chars
        seo_title = updated_dict.get("seo_title") or article.title
        clean_movie = movie.title.split("(")[0].strip()

        if clean_movie not in seo_title:
            seo_title = f"{clean_movie} 리뷰 및 결말 해석: {seo_title}"
            seo_notes.append(f"SEO 제목에 핵심 키워드('{clean_movie}') 전면 배치")

        if len(seo_title) > 55:
            seo_title = seo_title[:52] + "..."
            seo_notes.append("검색결과 잘림 방지를 위해 SEO 제목 길이 최적화 (55자 이내)")

        updated_dict["seo_title"] = seo_title

        # 2. Optimize Meta Description: ensure 100~160 chars and contains movie title
        meta_desc = updated_dict.get("meta_description") or article.excerpt
        if clean_movie not in meta_desc:
            meta_desc = f"영화 '{clean_movie}' 줄거리와 핵심 관람 포인트, {meta_desc}"
            seo_notes.append(f"메타 설명문에 영화 키워드('{clean_movie}') 포함")

        if len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + "..."
            seo_notes.append("포털 스니펫 길이에 맞춰 메타 설명문 160자 이내로 정제")

        updated_dict["meta_description"] = meta_desc

        # 3. Optimize Tags: ensure movie title and director are in tags, limit to 8 max
        tags: List[str] = updated_dict.get("tags") or []
        if clean_movie not in tags:
            tags.insert(0, clean_movie)
            seo_notes.append(f"태그 목록에 영화명('{clean_movie}') 추가")
        if movie.director and movie.director not in tags:
            tags.append(movie.director)
            seo_notes.append(f"태그 목록에 감독명('{movie.director}') 추가")

        updated_dict["tags"] = tags[:8]

        optimized_article = ArticleOutput.model_validate(updated_dict)
        return optimized_article, seo_notes

    @classmethod
    async def run_pipeline(
        cls,
        article: ArticleOutput,
        movie: Movie,
        tier: PipelineTier = PipelineTier.FULL
    ) -> PipelineResult:
        """Execute pipeline stages sequentially based on requested Tier."""
        stages: List[str] = ["WRITER"]
        current_article = article
        editorial_notes: List[str] = []
        seo_notes: List[str] = []

        # Stage: RESEARCH (Implicit in Movie metadata enrichment)
        if tier in (PipelineTier.STANDARD, PipelineTier.FULL):
            stages.insert(0, "RESEARCH")

        # Stage: EDITOR
        if tier in (PipelineTier.STANDARD, PipelineTier.FULL):
            current_article, ed_notes = cls.edit_article(current_article, movie)
            editorial_notes.extend(ed_notes)
            stages.append("EDITOR")

        # Stage: FACT_CHECKER (Critical Gate: Facts > SEO)
        fact_report = FactCheckService.extract_and_verify(current_article, movie)
        stages.append("FACT_CHECKER")

        # Stage: SEO_OPTIMIZER
        if tier == PipelineTier.FULL:
            current_article, s_notes = cls.optimize_seo(current_article, movie)
            seo_notes.extend(s_notes)
            stages.append("SEO_OPTIMIZER")

        is_ready = not fact_report.has_fatal_conflict

        summary = f"Pipeline {tier.value} 완료 (단계: {' -> '.join(stages)}), 팩트 충돌: {fact_report.conflict_count}건"
        logger.info(summary)

        return PipelineResult(
            tier=tier,
            stages_executed=stages,
            article=current_article,
            fact_report=fact_report,
            editorial_notes=editorial_notes,
            seo_notes=seo_notes,
            is_publish_ready=is_ready,
            summary=summary
        )
