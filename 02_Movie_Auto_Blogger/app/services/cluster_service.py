"""Content Cluster service implementing Hub & Spoke architecture for topical authority."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.database.models import Movie
from app.utils.logging import get_logger

logger = get_logger("cluster_service")


class ClusterIntent(str, Enum):
    """Search intent classification for cluster articles."""
    PILLAR_REVIEW = "PILLAR_REVIEW"          # Main hub article: Comprehensive review
    ENDING_EXPLAINED = "ENDING_EXPLAINED"    # Spoke: Ending explanation & interpretation
    POST_CREDIT = "POST_CREDIT"              # Spoke: Post-credits scene & sequel clues
    CAST_ANALYSIS = "CAST_ANALYSIS"          # Spoke: Cast & acting performance deep dive
    OTT_PLATFORM = "OTT_PLATFORM"            # Spoke: OTT streaming availability & watch guide
    TRIVIA = "TRIVIA"                        # Spoke: Production trivia & Easter eggs


class ClusterSubTopic(BaseModel):
    """Sub-topic planned within a cluster."""
    intent: ClusterIntent
    suggested_title: str
    target_keyword: str
    intent_score: float = Field(..., description="Intent opportunity score (0~100)")
    description: str
    is_primary: bool = False


class MovieClusterPlan(BaseModel):
    """Complete Hub & Spoke cluster plan for a movie."""
    movie_id: int
    movie_title: str
    primary_topic: ClusterSubTopic
    supporting_topics: List[ClusterSubTopic] = Field(default_factory=list)
    internal_link_strategy: List[str] = Field(default_factory=list)
    total_planned_articles: int = 1


class ClusterService:
    """Generates structured content clusters to maximize topical search coverage."""

    @staticmethod
    def generate_cluster_plan(movie: Movie) -> MovieClusterPlan:
        """Generate a complete Hub & Spoke cluster plan for a target movie."""
        title = movie.title.split("(")[0].strip()

        # 1. Primary Pillar Review
        primary = ClusterSubTopic(
            intent=ClusterIntent.PILLAR_REVIEW,
            suggested_title=f"영화 '{title}' 줄거리와 관람 포인트, 평점 및 솔직 총평 총정리",
            target_keyword=f"{title} 줄거리 결말 리뷰",
            intent_score=95.0,
            description=f"영화 '{title}'의 전반적 줄거리, 출연진, 기본정보를 망라한 핵심 필러 콘텐츠",
            is_primary=True
        )

        # 2. Supporting Spokes based on movie characteristics
        spokes: List[ClusterSubTopic] = []

        # Ending explained spoke
        spokes.append(ClusterSubTopic(
            intent=ClusterIntent.ENDING_EXPLAINED,
            suggested_title=f"영화 '{title}' 결말 해석과 숨겨진 복선 총정리 (스포주의)",
            target_keyword=f"{title} 결말 해석 복선",
            intent_score=88.0,
            description="결말부 반전과 상징적 의미를 심층 분석하여 N차 관람객 및 해석 검색자 공략"
        ))

        # Post-credit scene spoke
        spokes.append(ClusterSubTopic(
            intent=ClusterIntent.POST_CREDIT,
            suggested_title=f"영화 '{title}' 쿠키 영상 몇 개? 유무와 후속작 떡밥 완벽 정리",
            target_keyword=f"{title} 쿠키 영상",
            intent_score=84.0,
            description="극장 상영 직후 관람객들이 엔딩크레딧 전후 가장 빠르게 검색하는 쿠키 영상 정보 제공"
        ))

        # OTT streaming spoke
        spokes.append(ClusterSubTopic(
            intent=ClusterIntent.OTT_PLATFORM,
            suggested_title=f"영화 '{title}' OTT 다시보기: 넷플릭스, 티빙, 디즈니+ 스트리밍 정보",
            target_keyword=f"{title} OTT 다시보기",
            intent_score=80.0,
            description="상영 종료 후 2차 시장 검색 유입을 장기적으로 확보하는 롱테일 스트리밍 가이드"
        ))

        # Cast analysis spoke if cast is available
        director = movie.director or "감독"
        spokes.append(ClusterSubTopic(
            intent=ClusterIntent.CAST_ANALYSIS,
            suggested_title=f"영화 '{title}' 출연진 등장인물 관계도와 {director}의 연출 특징",
            target_keyword=f"{title} 출연진 등장인물",
            intent_score=75.0,
            description="주요 배우들의 캐릭터 분석과 감독의 필모그래피 연계 심층 비평"
        ))

        # Internal Link Strategy
        link_strategy = [
            f"서브 글({ClusterIntent.ENDING_EXPLAINED.value}, {ClusterIntent.POST_CREDIT.value}) 상단에 메인 필러 리뷰 링크 배치",
            f"메인 필러 글 하단 '관련 심층 가이드' 섹션에 결말 해석 및 쿠키 영상 링크 연결",
            "모든 서브 글 상호 간 앵커 텍스트로 자연스러운 횡적 연결 (Spoke-to-Spoke)"
        ]

        plan = MovieClusterPlan(
            movie_id=movie.id,
            movie_title=movie.title,
            primary_topic=primary,
            supporting_topics=spokes,
            internal_link_strategy=link_strategy,
            total_planned_articles=1 + len(spokes)
        )

        logger.info("Generated cluster plan for '%s': %d articles planned", movie.title, plan.total_planned_articles)
        return plan
