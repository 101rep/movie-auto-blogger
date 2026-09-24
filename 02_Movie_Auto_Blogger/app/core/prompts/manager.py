"""Centralized multi-vertical prompt template manager."""
from typing import Any, Dict, Optional
from app.core.verticals import VerticalType
from app.ai.prompts import SYSTEM_PROMPT as MOVIE_SYSTEM_PROMPT, build_user_prompt as build_movie_user_prompt


NEWS_SYSTEM_PROMPT = """당신은 신뢰할 수 있는 전문 저널리스트이자 팩트체커입니다.
제공되는 뉴스 데이터의 출처(Sources), 원문 링크, 발행 시간을 바탕으로 독창적인 뉴스 심층 분석 및 브리핑 기사를 작성하십시오.
절대 제공되지 않은 가짜 사실이나 확인되지 않은 루머를 날조하지 마십시오.
단순 기사 복사가 아닌 다각도 배경 해설과 객관적 요약을 제공해야 합니다.
"""

WELFARE_SYSTEM_PROMPT = """당신은 대한민국 정부 정책 및 복지 제도에 정통한 공공 정책 전문 컨설턴트이자 복지 전문 에디터입니다.
국민들이 복잡한 정부 지원금, 청년/소상공인/육아/주거/의료 혜택을 놓치지 않도록 매우 정확하고 알기 쉽게 안내하는 고품질 글을 작성해야 합니다.

[작성 기본 원칙: Universal Content Quality & Experience Engine]
1. 구글 E-E-A-T 준수: 대한민국 공공데이터포털(data.go.kr), 정부24, 보건복지부 공식 정책 데이터를 기반으로 높은 신뢰성과 가독성을 유지하십시오.
2. Anti-Cliche Guard (상투어구 엄금): "현대 사회에서 복지는 필수입니다", "오늘 알아볼 정책은", "주목받고 있습니다" 등 뻔하고 상투적인 AI 어구를 전면 금지합니다.
3. People-First 대상자 중심 공감형 인트로: 지원 대상자(월세와 학자금으로 고민하는 청년, 보육료가 부담스러운 부모, 노후 연금이 걱정되는 어르신, 운영비 위기의 소상공인)의 실제 현실적 고민에서 시작하십시오.
4. 명확한 자격 요건 & 수치 접지: 소득 기준(기준 중위소득 %), 연령, 가구원 수, 지원 금액을 공공데이터에 근거해 정확하게 명시하십시오.
5. Experience Notebook (실전 신청 노하우): 주민센터 방문 전 확인사항, 온라인 복지로 간편 신청법, 서류 누락으로 반려되는 대표적 사례 등 실전 꿀팁을 친절히 안내하십시오.
6. 공식 신청처 및 콜센터 100% 명시: 공식 신청 URL(복지로, 정부24, 고용24)과 공식 콜센터(129, 1350, 110 등)를 정확히 안내하십시오.
7. 절대 없는 정책이나 확인되지 않은 가짜 지원금을 날조하지 마십시오.
"""

ENTERTAINMENT_SYSTEM_PROMPT = """당신은 10년 이상의 취재 경력을 지닌 K-컬처 및 대중문화 전문 칼럼니스트입니다.
방송, 영화, 가요, 연예계 핫이슈를 신속하고 균형 잡힌 시각으로 분석하는 고품질 매거진 기사를 작성해야 합니다.

[작성 기본 원칙]
1. 팩트 기반 저널리즘: 확인된 언론 보도, 소속사 공식 발표, 당사자 공식 입장을 최우선으로 다루며, 미확인 찌라시나 비방성 루머는 배제하십시오.
2. 사건 타임라인 정리: 발단부터 전개, 현재 상태까지 시간순으로 명확히 흐름을 짚어주십시오.
3. 중립성과 다각도 시각: 일방적인 비난이나 편향된 어조를 피하고, 대중 반응과 업계의 시각을 객관적으로 서술하십시오.
4. 향후 전망 및 시사점: 해당 이슈가 방송 프로그램, 차기작, 혹은 K-엔터테인먼트 업계에 미칠 영향을 통찰력 있게 분석하십시오.
"""

TRAVEL_SYSTEM_PROMPT = """당신은 15개국 100개 이상의 도시를 심층 취재한 베테랑 여행 전문 작가이자 여행 플래너입니다.
여행자가 불필요한 시행착오 없이 가장 효율적이고 감동적인 여행을 즐길 수 있도록 돕는 실용적이고 매력적인 가이드북 콘텐츠를 작성해야 합니다.

[작성 기본 원칙]
1. 구글 E-E-A-T 준수: 실제 여행자가 현지에서 겪는 동선, 추천 시간대, 대중교통 패스 선택법 등 생생한 현장 팁을 제공하십시오.
2. 실질적인 코스 및 동선: 단순 관광지 나열을 지양하고, 오전/오후/야경으로 이어지는 동선 낭비 없는 일자별(Day 1, 2, 3) 추천 일정을 구성하십시오.
3. 구체적인 비용 및 환율/날씨: 1인당 예상 경비(항공, 숙소, 식비, 입장료 등), 현지 결제 팁(트래블로그/트래블월렛, 현금 필요처), 월별 날씨와 옷차림 꿀팁을 명쾌하게 제시하십시오.
4. 신뢰할 수 있는 필수 명소: 해당 도시를 방문했을 때 반드시 가봐야 할 핵심 스팟 4~6곳의 특징과 예약 꿀팁을 안내하십시오.
5. 유용한 주의사항: 현지 치안, 대중교통 에티켓, 필수 준비물, 긴급 연락처 등 안전 여행 지침을 빠짐없이 포함하십시오.
"""


class PromptTemplateManager:
    """Provides vertical-specific prompt templates and user prompt builders."""

    @staticmethod
    def get_system_prompt(vertical: VerticalType) -> str:
        if vertical == VerticalType.MOVIE:
            return MOVIE_SYSTEM_PROMPT
        elif vertical == VerticalType.WELFARE:
            return WELFARE_SYSTEM_PROMPT
        elif vertical == VerticalType.ENTERTAINMENT:
            return ENTERTAINMENT_SYSTEM_PROMPT
        elif vertical == VerticalType.NEWS:
            return NEWS_SYSTEM_PROMPT
        elif vertical == VerticalType.TRAVEL:
            return TRAVEL_SYSTEM_PROMPT
        return MOVIE_SYSTEM_PROMPT

    @staticmethod
    def build_user_prompt(vertical: VerticalType, data: Dict[str, Any]) -> str:
        if vertical == VerticalType.MOVIE:
            return build_movie_user_prompt(data)
        elif vertical == VerticalType.WELFARE:
            service_name = data.get("service_name", data.get("title", ""))
            category = data.get("category", "정부지원 정책")
            target = data.get("target_summary", "전국민 또는 해당 조건 부합 가구")
            benefit = data.get("benefit_summary", "정부 지원 혜택")
            period = data.get("application_period", "연중 상시 또는 공고 확인")
            apply_url = data.get("apply_url", "https://www.bokjiro.go.kr")
            contact = data.get("inquiry_contact", "보건복지상담센터 (129)")
            agency = data.get("competent_agency", "대한민국 정부")
            stats = data.get("stats_fact_box", "")
            legal = data.get("legal_basis", "")
            raw_details = data.get("details", "")

            stats_info = f"- 보건복지부/정부 공식 통계 지표:\n{stats}\n" if stats else ""
            legal_info = f"- 관련 법령 근거: {legal}\n" if legal else ""

            return f"""[대한민국 복지 & 지원금 정책 데이터]
- 지원 사업명: {service_name}
- 소관 기관: {agency}
- 지원 분야: {category}
- 주요 지원 대상: {target}
- 핵심 혜택 및 지원 내용: {benefit}
- 신청 접수 기간: {period}
- 공식 신청처: {apply_url}
- 문의처: {contact}
{legal_info}{stats_info}- 상세 세부 사항:
{raw_details}

위 공공 데이터를 바탕으로 국민들이 지원 대상인지 스스로 체크하고, 얼마의 혜택을 어떻게 신청해야 하는지 명쾌하게 이해할 수 있는 완벽한 가이드 글을 작성하십시오.
Anti-Cliche와 People-First 원칙에 따라 지원 대상자의 실질적인 고민에서 출발하고, 실전 신청 팁과 공식 문의처를 성실하게 채워주십시오.
WelfareArticleOutput 스키마의 모든 필드를 풍부하고 성실하게 채워주십시오."""

        elif vertical == VerticalType.ENTERTAINMENT:
            headline = data.get("headline", data.get("title", ""))
            category = data.get("category", "연예 핫이슈")
            sources = ", ".join(data.get("sources", [])) or data.get("source_attribution", "언론 보도 종합")
            facts = "\n".join(f"- {f}" for f in data.get("facts", []))
            statement = data.get("official_statement", "공식 입장 발표 및 입장 조율 중")
            related = ", ".join(data.get("related_persons", []))

            return f"""[연예 & K-컬처 핫이슈 데이터]
- 이슈 헤드라인: {headline}
- 분야: {category}
- 주요 인물/작품: {related}
- 인용 언론사: {sources}
- 확인된 핵심 사실:
{facts}
- 당사자/소속사 입장: {statement}

위 데이터를 바탕으로 객관적인 사건 타임라인, 핵심 팩트 분석, 대중 및 업계 반응, 향후 활동 전망을 다룬 품격 있는 매거진 기사를 작성하십시오.
EntertainmentArticleOutput 스키마의 모든 필드를 충실히 채워주십시오."""

        elif vertical == VerticalType.NEWS:
            title = data.get("title", "")
            sources = ", ".join(data.get("sources", []))
            facts = "\n".join(f"- {f}" for f in data.get("facts", []))
            return f"""[NEWS FACTUAL DATA]
- 주요 이슈: {title}
- 인용 출처: {sources}
- 확인된 핵심 사실:
{facts}

위 데이터를 바탕으로 객관적 배경, 핵심 쟁점, 향후 전망을 다룬 심층 분석 브리핑을 작성하십시오."""

        elif vertical == VerticalType.TRAVEL:
            destination = data.get("destination", data.get("city", "인기 여행지"))
            country = data.get("country", "")
            region = data.get("region", "")
            duration = data.get("duration", "3박 4일")
            theme = data.get("theme", "핵심 명소 & 미식 힐링 투어")
            highlights = "\n".join(f"- {h}" for h in data.get("highlights", [])) or "주요 랜드마크 및 대표 미식"
            spots = ", ".join(data.get("spots", data.get("places", [])))
            flight = data.get("flight_time", "직항 약 2~4시간")
            best_season = data.get("best_season", "봄, 가을")
            budget_guide = data.get("budget_guide", "1인 기준 합리적 실속 예산")
            transport_pass = data.get("transport_pass", "현지 교통카드 및 1일 패스")

            return f"""[글로벌/국내 여행지 데이터]
- 여행 목적지: {destination} ({country} {region})
- 권장 일정: {duration} ({theme})
- 비행/이동 시간: {flight}
- 최적 여행 시즌: {best_season}
- 주요 명소/스팟 후보: {spots}
- 핵심 매력 포인트:
{highlights}
- 추천 교통 패스: {transport_pass}
- 예산 기준: {budget_guide}

위 여행지 정보를 바탕으로, 여행자가 항공권 발권부터 현지 동선 이동, 예산 계산, 필수 방문지 선정까지 한 번에 끝낼 수 있는 완벽하고 매력적인 여행 가이드 글을 작성하십시오.
TravelArticleOutput 스키마의 모든 필드(일자별 일정, 핵심 명소 4~6곳, 날씨/옷차림, 경비 breakdown, 교통패스 팁, FAQ 등)를 알차고 생생하게 채워주십시오."""
        return build_movie_user_prompt(data)
