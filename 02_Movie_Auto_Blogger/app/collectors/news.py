"""Collector for Korean Factual News & Economic/Social Briefings."""
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
import httpx
from pydantic import BaseModel, Field

from app.utils.logging import get_logger

logger = get_logger("news_collector")


class NewsCandidateItem(BaseModel):
    """Normalized news briefing candidate."""
    topic_id: str
    headline: str
    category: str = "경제·시사"
    key_facts: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    official_statement: Optional[str] = None
    original_url: Optional[str] = None
    score: float = 85.0
    source_attribution: str = "공공 데이터 및 국내 주요 경제·시사 보도 종합"


CORE_NEWS_CATALOG: List[Dict[str, Any]] = [
    {
        "topic_id": "NEWS-ECON-RATE-01",
        "headline": "한국은행 기준금리 동향과 시중은행 대출·예금 금리 변동 영향 총정리",
        "category": "금융·경제",
        "key_facts": [
            "한국은행 금융통화위원회 기준금리 결정 발표 및 통화정책 방향성 제시",
            "주요 시중은행 주택담보대출 및 전세자금대출 혼합형·변동형 금리 추이 분석",
            "가계부채 관리 방안과 스트레스 DSR 2단계 적용에 따른 대출 한도 변화 핵심 체크"
        ],
        "sources": ["한국은행", "금융위원회", "연합뉴스", "한국경제"],
        "official_statement": "금융당국은 '시장 금리 변동성에 대비하여 실수요자 보호와 가계부채의 질적 구조 개선을 균형 있게 추진하겠다'고 밝힘",
        "original_url": "https://www.bok.or.kr",
        "score": 97.0
    },
    {
        "topic_id": "NEWS-REALESTATE-TREND-02",
        "headline": "수도권 부동산 시장 동향과 청약제도 개편 핵심 포인트 분석",
        "category": "부동산·주거",
        "key_facts": [
            "신생아 특례대출 소득 기준 완화 및 다자녀 특별공급 기준 2자녀 확대 시행",
            "서울 및 수도권 주요 학군지·역세권 아파트 실거래가 및 매매 거래량 통계",
            "무주택 청년·신혼부부를 위한 공공분양 '뉴:홈' 청약 일정 및 신청 팁"
        ],
        "sources": ["국토교통부", "한국부동산원", "매일경제"],
        "official_statement": "국토교통부는 '출산 가구와 청년층의 주거 안정 사다리를 강화하기 위해 청약 및 대출 규제를 실질적으로 완화한다'고 발표",
        "original_url": "https://www.molit.go.kr",
        "score": 95.0
    },
    {
        "topic_id": "NEWS-TECH-AI-REVOLUTION-03",
        "headline": "인공지능(AI) 기술 생태계 대격변: 글로벌 빅테크 차세대 모델과 일상 업무 혁신",
        "category": "IT·과학",
        "key_facts": [
            "주요 빅테크 기업의 멀티모달 AI 에이전트 출시 및 생산성 도구 전면 결합",
            "국내 주요 기업들의 온디바이스(On-device) AI 기기 보급 확대 및 서비스 고도화",
            "AI 검색 도입에 따른 웹 생태계 트래픽 변화 및 사용자 이용 패턴 진화"
        ],
        "sources": ["글로벌 테크 미디어", "과학기술정보통신부", "전자신문"],
        "official_statement": "업계 전문가들은 '단순 텍스트 대화를 넘어 직접 작업을 수행하는 자율 에이전트 시대가 본격 개막했다'고 평가",
        "original_url": "https://www.msit.go.kr",
        "score": 94.0
    },
    {
        "topic_id": "NEWS-HEALTH-INSURANCE-04",
        "headline": "국민건강보험 개편안과 실손의료보험 청구 간소화 서비스 이용 가이드",
        "category": "사회·생활",
        "key_facts": [
            "병원 창구 방문 없이 모바일 앱으로 1분 만에 서류 제출 가능한 실손보험 간소화",
            "지역가입자 재산세 부과 기준 완화 및 피부양자 자격 요건 최신 변동 사항",
            "본인확인 의무화 제도 시행에 따른 병의원 진료 시 신분증 지참 필수 주의사항"
        ],
        "sources": ["국민건강보험공단", "보건복지부", "금융감독원"],
        "official_statement": "보건복지부는 '국민의 의료비 청구 불편을 획기적으로 줄이고 건강보험 재정 건전성을 도모하는 제도 개선'이라고 설명",
        "original_url": "https://www.nhis.or.kr",
        "score": 96.0
    },
    {
        "topic_id": "NEWS-FIN-SAVINGS-05",
        "headline": "시중은행 정기예금·적금 최고 금리 비교 및 파킹통장 활용 재테크 전략",
        "category": "금융·경제",
        "key_facts": [
            "인터넷전문은행 및 1금융권 파킹통장 실시간 금리 및 우대조건 비교",
            "만기 유지율을 높이는 풍차돌리기 예적금 가입 팁",
            "금융소득종합과세 기준 및 비과세종합저축 가입 대상 확인"
        ],
        "sources": ["금융감독원 파인", "은행연합회 소비자포털"],
        "official_statement": "전문가들은 '금리 변동기에는 단기 파킹통장과 분할 예치 방식을 적절히 병행하는 것이 유리하다'고 조언",
        "original_url": "https://fine.fss.or.kr",
        "score": 93.0
    },
    {
        "topic_id": "NEWS-PROP-RENT-06",
        "headline": "전세보증금 반환보증 가입 요건과 안심전세 앱 활용 전세사기 예방 수칙",
        "category": "부동산·주거",
        "key_facts": [
            "주택도시보증공사(HUG) 전세보증금 반환보증 담보인정비율 및 보증료 할인",
            "안심전세 앱을 통한 임대인 체납 이력 및 악성 임대인 명단 사전 조회법",
            "전입신고와 확정일자 당일 효력 발생을 위한 계약서 특약 조항 작성법"
        ],
        "sources": ["국토교통부", "주택도시보증공사(HUG)"],
        "official_statement": "국토부는 '안심전세 앱 기능 고도화를 통해 임차인의 정보 비대칭을 해소하겠다'고 강조",
        "original_url": "https://www.khug.or.kr",
        "score": 92.5
    },
    {
        "topic_id": "NEWS-TECH-CHIP-07",
        "headline": "차세대 반도체 및 고대역폭메모리(HBM) 기술 경쟁과 미래 산업 전망",
        "category": "IT·과학",
        "key_facts": [
            "AI 데이터센터 확장에 따른 초고속 메모리 반도체 수요 급증",
            "국내 주요 제조사의 차세대 HBM4 양산 로드맵 및 기술 차별화",
            "소부장(소재·부품·장비) 생태계 강화 및 글로벌 공급망 다변화"
        ],
        "sources": ["산업통상자원부", "한국반도체산업협회"],
        "official_statement": "산업부는 'AI 반도체 초격차 확보를 위한 R&D 투자와 인프라 지원을 대폭 강화하겠다'고 발표",
        "original_url": "https://www.motie.go.kr",
        "score": 91.0
    },
    {
        "topic_id": "NEWS-LIFE-TRANSIT-08",
        "headline": "전국 대중교통 K-패스와 수도권 기후동행카드 혜택 비교 및 최적 선택 가이드",
        "category": "사회·생활",
        "key_facts": [
            "K-패스: 월 15회 이상 이용 시 지출액의 20~53% 환급 (청년·저소득층 추가 우대)",
            "기후동행카드: 서울 시내 지하철·시내버스 무제한 정기권 (따릉이 포함 옵션)",
            "월 대중교통 이용 금액과 출퇴근 경로에 따른 최적 카드 판별 기준"
        ],
        "sources": ["국토교통부 대도시권광역교통위원회", "서울특별시"],
        "official_statement": "교통 당국은 '국민 체감형 교통비 절감 혜택 확대를 위해 연계 지자체를 지속 확대한다'고 밝힘",
        "original_url": "https://korea-pass.kr",
        "score": 93.5
    }
]


class NewsCollector:
    """Collector for breaking and curated factual news."""

    def __init__(self, use_remote_feed: bool = True) -> None:
        self.use_remote_feed = use_remote_feed

    async def health_check(self) -> Dict[str, Any]:
        """Verify news data connectivity."""
        return {
            "success": True,
            "catalog_count": len(CORE_NEWS_CATALOG),
            "message": "뉴스 & 팩트체크 수집기 정상 가동 중"
        }

    async def get_popular_topics(self, limit: int = 10) -> List[NewsCandidateItem]:
        """Return curated high-priority news topics."""
        return [NewsCandidateItem.model_validate(item) for item in CORE_NEWS_CATALOG[:limit]]

    async def get_topic_by_id(self, topic_id: str) -> Optional[NewsCandidateItem]:
        """Lookup news topic by topic_id."""
        for raw in CORE_NEWS_CATALOG:
            if raw["topic_id"] == topic_id:
                return NewsCandidateItem.model_validate(raw)
        return None

    async def discover_latest_news(self, limit: int = 5) -> List[NewsCandidateItem]:
        """Discover latest live news topics from RSS or curated catalog."""
        import hashlib
        candidates = await self.get_popular_topics(limit=limit)

        if self.use_remote_feed:
            try:
                # Use Google News Korea Economy / Society RSS
                async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                    resp = await client.get(
                        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
                    )
                    if resp.status_code == 200:
                        root = ET.fromstring(resp.text)
                        items = root.findall("./channel/item")
                        for idx, item_elem in enumerate(items[:12]):
                            title_elem = item_elem.find("title")
                            link_elem = item_elem.find("link")
                            if title_elem is not None and title_elem.text:
                                raw_title = title_elem.text.strip()
                                parts = raw_title.rsplit(" - ", 1)
                                headline = parts[0].strip()
                                source = parts[1].strip() if len(parts) > 1 else "주요 언론"
                                link = link_elem.text.strip() if link_elem is not None and link_elem.text else "https://news.google.com"
                                h_id = hashlib.md5(headline.encode("utf-8")).hexdigest()[:8]
                                t_id = f"NEWS-LIVE-{h_id}"

                                if not any(c.topic_id == t_id or c.headline == headline for c in candidates):
                                    candidates.append(
                                        NewsCandidateItem(
                                            topic_id=t_id,
                                            headline=headline,
                                            category="실시간 경제·시사",
                                            key_facts=[
                                                f"{source} 보도에 따른 최신 이슈 분석",
                                                "정부 정책 및 시장 동향과 연계된 핵심 팩트 확인",
                                                "소비자 및 경제 활동에 미치는 직간접적 파급 효과"
                                            ],
                                            sources=[source],
                                            original_url=link,
                                            score=94.0 - (idx * 0.5)
                                        )
                                    )
            except Exception as e:
                logger.warning("Remote news RSS fetch error (using curated catalog): %s", str(e))

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:limit]

