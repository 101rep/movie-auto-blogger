"""Quality Profiles managing vertical-specific and global content quality standards."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QualityProfile(BaseModel):
    """Content Quality Profile defining validation thresholds and rule toggles."""
    name: str = Field(default="default", description="프로필 명칭")
    people_first: bool = Field(default=True, description="독자 중심 우선주의 적용 여부")
    search_intent: bool = Field(default=True, description="검색 의도 분석 및 반영 여부")
    cliche_control: bool = Field(default=True, description="AI 상투어구 억제 활성화")
    fact_grounding: bool = Field(default=True, description="공식 팩트 검증 활성화")
    duplicate_control: bool = Field(default=True, description="중복 콘텐츠 억제")
    internal_links: bool = Field(default=True, description="내부링크 연결 활성화")
    semantic_headings: bool = Field(default=True, description="시맨틱 헤딩(H2/H3 계층) 준수")
    seo_metadata: bool = Field(default=True, description="SEO 메타데이터 생성")
    schema_enabled: bool = Field(default=True, description="Schema.org 구조화 데이터 활성화")
    experience_enabled: bool = Field(default=False, description="개인 경험 인터뷰 및 그라운딩 활성화 여부")
    grounding_required: bool = Field(default=True, description="경험 글의 경우 취재 수첩 근거 필수")
    min_body_length: int = Field(default=600, description="본문 최소 한국어 글자 수")
    max_title_length: int = Field(default=50, description="제목 최대 글자 수")
    min_title_length: int = Field(default=10, description="제목 최소 글자 수")
    banned_cliches: List[str] = Field(
        default_factory=lambda: [
            "요즘 ~가 인기입니다",
            "~에 대해 알아보겠습니다",
            "많은 분들이 궁금해합니다",
            "~를 찾고 계신가요?",
            "이번 글에서는 ~를 살펴보겠습니다",
            "도움이 되셨기를 바랍니다",
            "지금부터 함께 살펴보시죠",
            "궁금증을 해결해 드립니다"
        ],
        description="억제 대상 기계적 AI 클리셰 목록"
    )


class QualityProfileRegistry:
    """Registry maintaining global and vertical-specific Quality Profiles."""
    _profiles: Dict[str, QualityProfile] = {}

    @classmethod
    def register(cls, profile: QualityProfile) -> None:
        cls._profiles[profile.name.lower()] = profile

    @classmethod
    def get(cls, name: str) -> QualityProfile:
        return cls._profiles.get(name.lower(), cls._profiles.get("default", QualityProfile()))

    @classmethod
    def list_profiles(cls) -> List[str]:
        return list(cls._profiles.keys())


# Default built-in profiles
QualityProfileRegistry.register(QualityProfile(name="default"))
QualityProfileRegistry.register(QualityProfile(name="movie", experience_enabled=False, min_body_length=600))
QualityProfileRegistry.register(QualityProfile(name="travel", experience_enabled=False, min_body_length=500))
QualityProfileRegistry.register(QualityProfile(name="experience", experience_enabled=True, grounding_required=True, min_body_length=700))
QualityProfileRegistry.register(QualityProfile(name="affiliate", experience_enabled=False, min_body_length=500))
QualityProfileRegistry.register(QualityProfile(name="welfare", experience_enabled=False, min_body_length=600))
QualityProfileRegistry.register(QualityProfile(name="entertainment", experience_enabled=False, min_body_length=500))
