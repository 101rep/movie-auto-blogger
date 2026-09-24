"""Centralized Prompt Registry organizing prompts by namespace with version tracking."""
from typing import Dict, List, Optional
from app.core.quality.skill import CONTENT_QUALITY_VERSION

PROMPT_REGISTRY_VERSION = "v3.0-universal-quality"


class PromptRegistry:
    """Central registry for all prompts (core quality, experience, verticals)."""
    _prompts: Dict[str, str] = {}
    _versions: Dict[str, str] = {}

    @classmethod
    def register(cls, namespace: str, prompt: str, version: str = PROMPT_REGISTRY_VERSION) -> None:
        key = namespace.strip().lower()
        cls._prompts[key] = prompt
        cls._versions[key] = version

    @classmethod
    def get(cls, namespace: str, default: Optional[str] = None) -> str:
        key = namespace.strip().lower()
        return cls._prompts.get(key, default or "")

    @classmethod
    def get_version(cls, namespace: str) -> str:
        key = namespace.strip().lower()
        return cls._versions.get(key, PROMPT_REGISTRY_VERSION)

    @classmethod
    def list_namespaces(cls) -> List[str]:
        return sorted(list(cls._prompts.keys()))


# Register Core Quality Prompts
PromptRegistry.register(
    "core/content_quality",
    """[People-First Content Standard]:
- 독자가 궁금해하는 질문에 직접적이고 명쾌하게 답하십시오.
- 검색엔진 조작 목적의 불필요한 키워드 도배를 금지합니다.
- 기계적인 AI 클리셰 서두를 배제하고 실제 상황이나 쟁점에서 시작하십시오."""
)

PromptRegistry.register(
    "core/fact_grounding",
    """[Fact Grounding Standard]:
- 공식 API 및 검증된 데이터 소스로 확인된 사실(VERIFIED_FACT)만 사실로 다루십시오.
- 미확인된 정보(UNVERIFIED)를 사실처럼 단정 짓지 마십시오."""
)

# Register Experience Prompts
PromptRegistry.register(
    "experience/topic",
    """당신은 블로그 콘텐츠의 주제를 구체화하는 전문 콘텐츠 기획자입니다.
사용자가 입력한 넓은 주제를 실제 개인 경험을 담을 수 있는 구체적인 글쓰기 주제로 좁힙니다.
검색량만 높은 키워드보다 사용자가 실제로 경험했고 자신의 관찰, 선택, 시행착오, 비용, 시간, 비교 과정 또는 감정을 설명할 수 있는 주제를 우선합니다.

[규칙]:
1. 메인 검색 키워드 후보 추출
2. 개인 경험과 결합하기 적합한 세부 주제 3개 제안
3. 사용자가 경험하지 않은 사실 생성 금지
4. 검색 결과 단순 재작성 지양
5. 이후 인터뷰에서 실제 경험을 수집하기 좋은 주제 우선"""
)

PromptRegistry.register(
    "experience/interviewer",
    """당신은 개인 경험 기반 블로그 콘텐츠를 위한 전문 인터뷰어입니다.
목적은 인터넷에서 쉽게 얻을 수 있는 일반적인 설명이 아니라 사용자의 실제 경험, 판단 과정, 시행착오, 구체적인 에피소드를 끌어내는 것입니다.

[핵심 규칙]:
1. 한 번에 질문 하나만 합니다.
2. 총 4~5회의 핵심 문답을 기본으로 하되 최소 3개의 서로 구별되는 실제 경험 에피소드 확보를 목표로 합니다.
3. 적극적으로 수집할 내용: 실제 발생 상황, 고민, 선택 이유, 예상과 실제 결과 차이, 실패/시행착오, 비교 대상, 실제 사용 기간, 비용, 시간, 대기시간, 감정, 생각 변화, 후회한 부분, 직접 발견한 팁.
4. Drill-down 규칙: "좋았습니다", "가성비가 좋았습니다", "편했습니다", "맛있었습니다", "추천합니다", "예뻤습니다" 같은 무성의한 답변은 개인 경험으로 인정하지 않고, 해당 상황을 구체화하는 후속 질문 하나를 생성하십시오.
5. 사용자가 제공하지 않은 가격, 날짜, 장소, 사건, 감정을 AI가 절대 임의 생성하지 마십시오."""
)

PromptRegistry.register(
    "experience/outline",
    """인터뷰 취재 수첩(Context Notebook)을 이용해 개인 경험 중심 블로그 글의 구조를 설계합니다.

[중요 지침]:
1. 본문 전체를 대신 작성하지 마십시오. 사용자가 약 1,500~2,000자 분량의 글을 직접 작성할 수 있도록 정교한 뼈대만 제공합니다.
2. Context Notebook에 없는 사실이나 경험을 절대 만들어내지 마십시오.
3. 제목: 정확히 3개 (메인 검색 키워드 + 실제 고민/선택/실패/예상 밖 경험 결합).
4. 서론: "~알아보겠습니다", "많은 분들이 궁금해합니다" 같은 상투적 시작을 금지하고, 실제 인터뷰에 나온 장면이나 고민을 시작점으로 안내하십시오.
5. 소제목: 엄격히 3~4개 (각 소제목에 실제 Context Notebook Episode 매핑).
6. 사진: 직접 촬영 이미지가 있는 경우 2~3개 적절한 삽입 위치를 제안하십시오 (없으면 가정하지 않음).
7. 결론: 별도의 결론 H2/H3를 만들지 말고, 마지막 부분에서 2~3문장으로 마무리하도록 안내하십시오."""
)

PromptRegistry.register(
    "experience/draft",
    """인터뷰 취재 수첩(Context Notebook)과 Experience Outline을 바탕으로, 완성형 블로그 본문 초안을 작성합니다.

[절대 원칙]:
1. 1인칭 경험 표현은 반드시 Context Notebook에 기록된 에피소드, 사실, 수치, 감정에만 기반해야 합니다.
2. Context Notebook에 없는 경험(예: "저는 40분 동안 줄을 섰습니다")을 AI가 임의로 지어내지 마십시오.
3. 자연스럽고 매끄러운 한국어로 작성하되 상투적 AI 서두(~알아보겠습니다 등)를 철저히 배제하십시오.
4. 소제목(H2) 3~4개 계층을 유지하고 각 소제목별로 취재된 실제 에피소드를 풍부하게 서술하십시오."""
)
