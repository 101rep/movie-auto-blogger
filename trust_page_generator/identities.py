"""Brand Identity Specifications for 8 WordPress Blogs per PRD.
Strictly differentiated profiles ensuring zero duplicate branding.
"""
from typing import Dict, Any, List
from trust_page_generator.config import BLOG_REGISTRY
from trust_page_generator.database.models import BlogIdentity


MASTER_IDENTITIES: Dict[int, Dict[str, Any]] = {
    1: {
        "blog_id": 1,
        "brand_name": "트래블픽24",
        "domain": "https://travelpick24.com",
        "category": "국내외 실전 여행 가이드 & 일정 큐레이션",
        "mission": "실패 없는 여행을 위해 과장된 광고를 배제하고, 실제 여행자의 동선에 맞춘 최적의 일정과 현장 팁을 제공합니다.",
        "target_user": "주말 나들이를 계획하는 가족, 2040 자유 여행자, 효율적인 동선을 원하는 뚜벅이/드라이브 여행객",
        "tone": "친근하고 꼼꼼한 여행 플래너 톤 (시간대별 추천 동선, 솔직한 주차 및 대기 팁 안내)",
        "content_policy": "한국관광공사 TourAPI 공공데이터 및 지자체 공식 관광 자료를 기반으로 운영시간, 요금, 주차 공간, 대중교통 경로를 교차 검증합니다.",
        "trust_message": "본 사이트는 특정 업체의 상업적 후원이나 협찬에 왜곡되지 않으며, 공식 발표 자료와 실제 방문자 후기 데이터를 토대로 객관적인 여행 정보를 정리합니다.",
        "email": "contact@travelpick24.com"
    },
    2: {
        "blog_id": 2,
        "brand_name": "트렌드스팟24",
        "domain": "https://trendspot24.com",
        "category": "글로벌 트렌드, 테크 & 라이프스타일 인사이트",
        "mission": "급변하는 디지털 사회와 현대인의 라이프스타일 변화 속에서 단순 유행을 넘어선 핵심 맥락과 실용적인 인사이트를 전달합니다.",
        "target_user": "트렌드에 민감한 2030 직장인, 테크 얼리어답터, 디지털 크리에이터 및 마케터",
        "tone": "감각적이면서도 균형 잡힌 분석 톤 (표면적 현상보다는 원인과 향후 파급효과 중심 서술)",
        "content_policy": "글로벌 테크 발표, 공식 미디어 보도자료, 신뢰도 높은 산업 보고서를 바탕으로 팩트를 점검하며 과장된 찌라시나 루머를 원천 차단합니다.",
        "trust_message": "단순한 클릭베이트를 지양하고, 공식 통계와 검증된 공개 정보를 기반으로 시대의 흐름을 통찰할 수 있는 정제된 콘텐츠만을 제공합니다.",
        "email": "contact@trendspot24.com"
    },
    3: {
        "blog_id": 3,
        "brand_name": "아이템픽24",
        "domain": "https://item.travelpick24.com",
        "category": "테크 기기, 데스크테리어 & 생산성 장비 스펙 분석",
        "mission": "복잡한 기술 스펙을 알기 쉽게 풀고, 구매 후 후회 없는 합리적인 소비를 돕기 위해 장단점을 투명하게 비교 분석합니다.",
        "target_user": "재택근무 직장인, 데스크테리어 애호가, 가성비와 성능을 꼼꼼히 따지는 스마트 컨슈머",
        "tone": "명확하고 실용적인 테크 큐레이터 톤 (체크리스트, 스펙 비교표, 실사용 관점의 솔직한 평가)",
        "content_policy": "제조사 공식 제품 카탈로그 및 기술 사양서(Spec Sheet)를 1차 출처로 삼으며, 복수의 실구매자 피드백을 수집하여 교차 검증합니다.",
        "trust_message": "화려한 수식어나 일방적인 찬양을 배제하고, 공식 스펙 데이터와 실제 사용 환경에서의 한계점까지 가감 없이 공개하여 신뢰할 수 있는 가이드를 제시합니다.",
        "email": "item@travelpick24.com"
    },
    4: {
        "blog_id": 4,
        "brand_name": "엔터픽24",
        "domain": "https://enter.trendspot24.com",
        "category": "영화, OTT 시리즈 & 대중문화 심층 큐레이션",
        "mission": "영화와 드라마의 숨은 연출 의도와 미학적 가치를 조명하여, 관객이 작품을 더욱 풍성하고 깊이 있게 즐길 수 있도록 돕습니다.",
        "target_user": "주말 영화를 고르는 OTT 구독자, 스토리텔링과 연출에 관심이 많은 영화 애호가",
        "tone": "영화 매거진 에디터 스타일의 깊이 있는 비평 톤 (스포일러 방지 가이드라인 준수, 관람 포인트 중심 해설)",
        "content_policy": "글로벌 공식 영화 데이터베이스(TMDB, IMDb) 및 배급사 공식 보도자료를 준용하며, 자극적인 스포일러 없이 작품의 본질을 전달합니다.",
        "trust_message": "작품에 대한 존중을 바탕으로, 공인된 영화 정보와 글로벌 평점 데이터를 객관적으로 분석하여 취향에 맞는 최고의 콘텐츠를 선별합니다.",
        "email": "enter@trendspot24.com"
    },
    5: {
        "blog_id": 5,
        "brand_name": "복지픽23",
        "domain": "https://welfare23.travelpick24.com",
        "category": "청년 주거, 자산형성, 취업·일자리 복지 정책 포털",
        "mission": "2030 청년들이 복잡한 행정 용어 때문에 정당한 권리와 지원금을 놓치지 않도록, 실생활에 직결되는 청년 정책의 문턱을 낮춥니다.",
        "target_user": "만 19~39세 청년, 취업준비생, 사회초년생, 독립을 준비하는 청년 1인가구",
        "tone": "실생활 맞춤형 청년 정책 전문가 톤 (월세, 전세보증금, 자산형성 통장 등 실전 신청 요령 중심)",
        "content_policy": "국토교통부, 고용노동부, 행정안전부 및 각 지자체의 공식 공고문과 사업 지침을 직접 대조하여 자격 요건과 소득 기준을 검증합니다.",
        "trust_message": "정부 정책의 시행령과 공식 공고 원문을 기반으로 정리하며, 불확실하거나 자극적인 표현 없이 실제 신청 시 필요한 실질적 요건만을 명확히 안내합니다.",
        "email": "welfare23@travelpick24.com"
    },
    6: {
        "blog_id": 6,
        "brand_name": "복지픽24",
        "domain": "https://welfare24.travelpick24.com",
        "category": "시니어 연금, 노후 케어, 소상공인 경영·재기 정책 지원",
        "mission": "어르신의 안정적인 노후 복지와 소상공인·자영업자 대표님들의 든든한 사업 경영을 위해 필수 정부 지원제도를 명쾌하게 안내합니다.",
        "target_user": "5060 신중년 및 만 65세 이상 어르신 가구, 소상공인, 자영업자, 폐업·재기를 고민하는 대표",
        "tone": "정중하고 신뢰감 있는 실무 컨설턴트 톤 (가독성 높은 문장, 신청 단계별 준비서류 체크리스트 안내)",
        "content_policy": "보건복지부, 중소벤처기업부, 소상공인시장진흥공단, 국민연금공단의 공식 사업 지침 및 공공데이터를 기준으로 사실관계를 검증합니다.",
        "trust_message": "어르신과 자영업자분들의 현실적인 필요에 맞춰 공공기관의 공식 발표자료만을 엄선하여 정리하며, 어려운 법적 용어를 쉬운 일상 언어로 정제하여 전달합니다.",
        "email": "welfare24@travelpick24.com"
    },
    7: {
        "blog_id": 7,
        "brand_name": "복지픽25",
        "domain": "https://welfare25.travelpick24.com",
        "category": "전 국민 정부지원금, 보육·영유아, 생활바우처 & 건강보험",
        "mission": "대한민국 국민이라면 누구나 누려야 할 보편적 복지 혜택과 긴급 지원제도를 한곳에서 쉽고 투명하게 확인할 수 있도록 돕습니다.",
        "target_user": "영유아 및 아동을 양육하는 부모, 생활안정이 필요한 일반 가구, 복지 제도를 처음 접하는 전 국민",
        "tone": "친절하고 따뜻한 복지 상담사 톤 (차근차근 하나씩 짚어주는 다정한 설명과 자가진단표 제공)",
        "content_policy": "대한민국 공공데이터포털(data.go.kr)과 정부24의 10,937개 공식 복지 데이터를 실시간 연계하여 지원 금액과 신청 기한을 정확히 반영합니다.",
        "trust_message": "공식 정부24 데이터와 보건복지부 고시 기준을 100% 준용하며, 누구에게나 열려 있는 지원금 정보를 투명하고 공정하게 정리하여 안내합니다.",
        "email": "welfare25@travelpick24.com"
    },
    8: {
        "blog_id": 8,
        "brand_name": "뉴스픽24",
        "domain": "https://news.trendspot24.com",
        "category": "실시간 시사 뉴스, 경제 정책 & 데이터 팩트 브리핑",
        "mission": "편향된 정쟁과 자극적인 루머를 걷어내고, 독자의 실생활과 경제에 직결되는 주요 시사 이슈를 데이터와 팩트 중심으로 요약 브리핑합니다.",
        "target_user": "바쁜 일상 속에서 빠르고 정확하게 핵심 시사·경제 이슈를 파악하고자 하는 현대 직장인",
        "tone": "객관적이고 균형 잡힌 저널리즘 톤 (데이터 기반 사실 서술, 양측 관점의 공정한 제시)",
        "content_policy": "대한민국 정부 부처 공식 합동 브리핑, 국가통계포털(KOSIS), 공공기관 보도자료를 1차 근거로 채택하며 미확인 루머는 일체 다루지 않습니다.",
        "trust_message": "속보 경쟁을 위한 추측성 기사를 배제하고, 공식 발표와 공인 통계를 바탕으로 검증된 팩트만을 정직하게 브리핑합니다.",
        "email": "news@trendspot24.com"
    }
}


def sync_identities_to_db() -> List[BlogIdentity]:
    """Populate or update blog_identity records in the database."""
    from trust_page_generator.database.session import SessionLocal

    db = SessionLocal()
    records = []
    try:
        for blog_id, data in MASTER_IDENTITIES.items():
            existing = db.query(BlogIdentity).filter(BlogIdentity.blog_id == blog_id).first()
            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
                records.append(existing)
            else:
                new_identity = BlogIdentity(**data)
                db.add(new_identity)
                records.append(new_identity)
        db.commit()
    finally:
        db.close()
    return records
