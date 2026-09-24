"""Pydantic schemas for Experience Interview, Context Notebook, Outline, and Grounding."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContextEpisode(BaseModel):
    """Structured individual experience episode extracted from interview."""
    id: str = Field(..., description="에피소드 식별자 (예: E01, E02)")
    situation: str = Field(..., description="실제 발생한 구체적 상황")
    problem_or_conflict: str = Field(default="", description="고민, 갈등 또는 예상 밖 문제")
    action: str = Field(default="", description="사용자가 취한 구체적 행동 및 선택")
    result: str = Field(default="", description="실제 행동의 결과 (성공, 실패, 반전)")
    emotion: str = Field(default="", description="당시 느낀 감정 또는 생각 변화")
    specific_numbers: List[str] = Field(default_factory=list, description="비용, 소요시간, 대기시간, 날짜 등 구체적 수치")
    unique_observation: str = Field(default="", description="직접 경험하며 발견한 고유 관찰 또는 꿀팁")
    source_type: str = Field(default="user_interview", description="출처 유형")
    confidence: str = Field(default="user_reported", description="신뢰도 등급")


class ContextNotebook(BaseModel):
    """Context Memory notebook accumulating user's verified first-hand experiences."""
    topic: str = Field(default="", description="취재 대주제")
    main_keyword: str = Field(default="", description="메인 검색 키워드")
    interview_round: int = Field(default=0, description="진행된 인터뷰 문답 횟수")
    episodes: List[ContextEpisode] = Field(default_factory=list, description="확보된 고유 경험 에피소드 목록")
    facts: List[str] = Field(default_factory=list, description="사용자가 직접 언급한 사실들")
    numbers: List[str] = Field(default_factory=list, description="언급된 구체적 비용/시간/기간 수치")
    comparisons: List[str] = Field(default_factory=list, description="비교한 대안 및 선택 이유")
    mistakes: List[str] = Field(default_factory=list, description="시행착오, 아쉬웠던 점, 후회")
    discoveries: List[str] = Field(default_factory=list, description="직접 발견한 유용한 팁 및 조언")
    photo_opportunities: List[str] = Field(default_factory=list, description="사용자가 직접 보유한 사진")
    unknown_or_unverified: List[str] = Field(default_factory=list, description="기억나지 않거나 확인되지 않은 사항")


class InterviewTurn(BaseModel):
    """Single question-and-answer exchange during deep interview."""
    round: int
    question: str
    original_answer: str
    extracted_episodes: List[ContextEpisode] = Field(default_factory=list)
    extracted_facts: List[str] = Field(default_factory=list)
    is_drilldown: bool = False


class InterviewSessionState(BaseModel):
    """Persistent state of an active or completed interview session."""
    session_id: str
    topic: str
    main_keyword: str = ""
    suggested_subtopics: List[str] = Field(default_factory=list)
    turns: List[InterviewTurn] = Field(default_factory=list)
    context_notebook: ContextNotebook = Field(default_factory=ContextNotebook)
    status: str = "IN_PROGRESS"  # IN_PROGRESS, COMPLETED, OUTLINED, DRAFTED, APPROVED
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class H2SectionOutline(BaseModel):
    """Outline structure for each H2 sub-section."""
    heading: str = Field(..., description="소제목 명칭")
    episode_ids: List[str] = Field(default_factory=list, description="매핑된 에피소드 ID (예: ['E01'])")
    key_facts: List[str] = Field(default_factory=list, description="해당 부분에 배치할 수치/사실")
    user_decision: str = Field(default="", description="사용자의 고민과 선택 과정")
    expected_vs_actual: str = Field(default="", description="예상과 실제 결과의 차이")
    photo_placement: Optional[str] = Field(default=None, description="사진 추천 배치 위치 (보유 시)")


class ExperienceOutline(BaseModel):
    """Structured Experience-driven blog outline."""
    titles: List[str] = Field(..., min_length=3, max_length=3, description="제목 후보 정확히 3개")
    intro_direction: str = Field(..., description="실제 고민/장면으로 시작하는 서론 작성 가이드")
    sections: List[H2SectionOutline] = Field(..., min_length=3, max_length=4, description="소제목 3~4개")
    conclusion_direction: str = Field(..., description="별도 결론 H2 없이 마지막 2~3문장 마무리 가이드")
    photo_suggestions: List[str] = Field(default_factory=list, description="직접 촬영 사진 배치 제안")


class ExperienceDraft(BaseModel):
    """Generated full draft grounded in Context Notebook."""
    title: str = Field(..., description="최종 글 제목")
    seo_title: str = Field(..., description="SEO 최적화 제목")
    meta_description: str = Field(..., description="검색엔진 메타 설명문")
    slug: str = Field(..., description="URL 슬러그")
    html_content: str = Field(..., description="워드프레스 호환 HTML 본문")
    excerpt: str = Field(..., description="요약 발췌문")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    episodes_used: List[str] = Field(default_factory=list, description="활용된 에피소드 ID 목록")
    generator_version: str = "1.0"
    quality_profile: str = "experience"
    prompt_version: str = "v3.0-experience-engine"


class GroundingClaim(BaseModel):
    """Individual assertion checked against Context Notebook."""
    claim_text: str
    is_grounded: bool
    matched_episode_id: Optional[str] = None
    source_type: str = "user_interview"
    detail: str = ""


class ExperienceGroundingReport(BaseModel):
    """Audit report of experiential grounding in draft."""
    total_claims: int = 0
    grounded_count: int = 0
    ungrounded_count: int = 0
    grounded_claims_count: int = 0      # alias for grounded_count (UI convenience)
    grounding_ratio: float = 1.0        # grounded_count / total_claims (1.0 if no claims)
    is_passed: bool = True
    status: str = "PASS"  # PASS, REVIEW, FAIL
    claims: List[GroundingClaim] = Field(default_factory=list)
    ungrounded_claims: List[GroundingClaim] = Field(default_factory=list)  # filtered convenience list
    summary: str = ""
