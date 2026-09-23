from typing import List, Optional
from domain_types.schemas import ProductDTO
from integrations.interfaces import ProductProvider

class MockProductProvider(ProductProvider):
    def __init__(self):
        self._products = [
            ProductDTO(
                external_id='CP-1001',
                name='스탠리 퀜처 H2.0 플로우스테이트 텀블러 887ml',
                url='https://www.coupang.com/vp/products/1001',
                image_url='https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=500&auto=format&fit=crop&q=60',
                category='주방용품',
                price=49000,
                original_price=59000,
                rating=4.9,
                review_count=1420,
                shipping_type='로켓배송',
                description='진공 단열 기술로 48시간 얼음 유지. 인체공학적 손잡이와 3단 회전 빨대 뚜껑 일체형 설계.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1002',
                name='다이슨 에어랩 멀티 스타일러 앤 드라이어 컴플리트 롱',
                url='https://www.coupang.com/vp/products/1002',
                image_url='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&auto=format&fit=crop&q=60',
                category='뷰티/가전',
                price=699000,
                original_price=749000,
                rating=4.8,
                review_count=3240,
                shipping_type='로켓배송',
                description='코안다 효과로 과도한 열 손상 없이 바람으로 자연스러운 컬과 볼륨 연출.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1003',
                name='샤오미 미지아 스마트 로봇청소기 B101CN 올인원 물걸레',
                url='https://www.coupang.com/vp/products/1003',
                image_url='https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&auto=format&fit=crop&q=60',
                category='생활가전',
                price=389000,
                original_price=450000,
                rating=4.7,
                review_count=890,
                shipping_type='로켓직구',
                description='자동 걸레 세척 및 열풍 건조 스테이션 탑재. LDS 라이다 센서로 스마트 매핑 및 금지구역 설정.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1004',
                name='닥터지 레드 블레미쉬 클리어 수딩 크림 70ml 2개 세트',
                url='https://www.coupang.com/vp/products/1004',
                image_url='https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&auto=format&fit=crop&q=60',
                category='뷰티',
                price=28900,
                original_price=36000,
                rating=4.9,
                review_count=12500,
                shipping_type='로켓배송',
                description='10-시카 콤플렉스로 붉어지고 민감해진 피부를 시원하고 촉촉하게 진정시키는 젤 타입 크림.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1005',
                name='코멧 홈 고중량 호텔식 페이스타월 200g 10수 10장 세트',
                url='https://www.coupang.com/vp/products/1005',
                image_url='https://images.unsplash.com/photo-1616627547584-bf28cee262db?w=500&auto=format&fit=crop&q=60',
                category='리빙/생활',
                price=19900,
                original_price=25000,
                rating=4.6,
                review_count=4580,
                shipping_type='로켓배송',
                description='도톰한 200g 중량감의 최고급 코마사 면 100% 호텔식 수건. 흡수력과 내구성이 우수함.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1006',
                name='로지텍 MX Master 3S 무선 무소음 마우스 페일그레이',
                url='https://www.coupang.com/vp/products/1006',
                image_url='https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&auto=format&fit=crop&q=60',
                category='디지털/가전',
                price=129000,
                original_price=139000,
                rating=4.9,
                review_count=5320,
                shipping_type='로켓배송',
                description='8,000 DPI 다크필드 센서로 유리 위에서도 정밀 작동. MagSpeed 초고속 전자석 스크롤 휠 탑재.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1007',
                name='일리 Y3.3 캡슐 커피머신 화이트',
                url='https://www.coupang.com/vp/products/1007',
                image_url='https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500&auto=format&fit=crop&q=60',
                category='주방용품',
                price=109000,
                original_price=139000,
                rating=4.8,
                review_count=9820,
                shipping_type='로켓배송',
                description='미니멀하고 컴팩트한 디자인. 에스프레소 및 아메리카노 2가지 모드 지원, 19바 고압 추출.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1008',
                name='바디럽 퓨어썸 주방용 싱크대 필터 핸디형 본체 + 필터 1개',
                url='https://www.coupang.com/vp/products/1008',
                image_url='https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500&auto=format&fit=crop&q=60',
                category='리빙/생활',
                price=24900,
                original_price=32000,
                rating=4.7,
                review_count=3640,
                shipping_type='로켓배송',
                description='녹물과 미세 이물질을 완벽 차단하는 정밀 마이크로 세디먼트 필터 및 3단계 수압 조절 살수판.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1009',
                name='브리타 마레라 메모 정수기 2.4L 화이트 (필터 1개 포함)',
                url='https://www.coupang.com/vp/products/1009',
                image_url='https://images.unsplash.com/photo-1548839140-29a749e1bc4e?w=500&auto=format&fit=crop&q=60',
                category='주방용품',
                price=34900,
                original_price=42000,
                rating=4.9,
                review_count=21400,
                shipping_type='로켓배송',
                description='생수 페트병 분리수거 지옥 탈출. 막스트라 프로 필터로 미세플라스틱 및 염소 완벽 제거.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1010',
                name='크레마 모티프 전자책 e-book 리더기 6인치 화이트',
                url='https://www.coupang.com/vp/products/1010',
                image_url='https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=60',
                category='디지털/가전',
                price=224000,
                original_price=240000,
                rating=4.8,
                review_count=1150,
                shipping_type='로켓배송',
                description='300 PPI Carta 1200 최신 전자잉크 디스플레이. 안드로이드 11 탑재로 밀리의서재/리디북스 자유자재 설치.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1011',
                name='모슈 테이블팟 레트로 보온보냉 주전자 1.0L 아이보리',
                url='https://www.coupang.com/vp/products/1011',
                image_url='https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=500&auto=format&fit=crop&q=60',
                category='주방용품',
                price=38500,
                original_price=48000,
                rating=4.7,
                review_count=2390,
                shipping_type='로켓배송',
                description='우드 감성 손잡이와 앤틱한 레트로 실루엣. 10시간 보온 62도 이상, 10시간 보냉 10도 이하 유지.',
                source='coupang'
            ),
            ProductDTO(
                external_id='CP-1012',
                name='자주(JAJU) 층간소음 방지 고밀도 메모리폼 거실 실내화',
                url='https://www.coupang.com/vp/products/1012',
                image_url='https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&auto=format&fit=crop&q=60',
                category='리빙/생활',
                price=14900,
                original_price=19900,
                rating=4.6,
                review_count=3890,
                shipping_type='로켓배송',
                description='발뒤꿈치 충격을 흡수하는 3cm 고밀도 EVA 쿠션폼. 미끄럼 방지 논슬립 바닥 패턴.',
                source='coupang'
            )
        ]

    def search_products(self, query: Optional[str] = None, category: Optional[str] = None, page: int = 1, limit: int = 20) -> List[ProductDTO]:
        results = list(self._products)
        if query:
            q_words = [w.lower() for w in query.split() if w.strip()]
            matched = []
            for p in results:
                text = f"{p.name} {p.description or ''}".lower()
                if any(w in text for w in q_words):
                    matched.append(p)
            results = matched if matched else list(self._products[:limit])

        if category and category != '전체':
            results = [p for p in results if p.category == category]

        start = (page - 1) * limit
        return results[start:start + limit]

    def get_product_detail(self, external_id: str) -> Optional[ProductDTO]:
        for p in self._products:
            if p.external_id == external_id:
                return p
        return None
