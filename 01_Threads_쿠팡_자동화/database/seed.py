import json
from database.connection import SessionLocal, Base, engine
from database.models import (
    Project, Account, Product, ProductScore, ProductDNA,
    ContentIdea, Content, Comment, PromptVersion
)

def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Project
        project = db.query(Project).first()
        if not project:
            project = Project(
                name='쿠팡 x Threads 자동화 1호',
                description='Threads를 통한 쿠팡 파트너스 고수익 큐레이션 프로젝트',
                status='ACTIVE'
            )
            db.add(project)
            db.commit()
            db.refresh(project)

        # 2. Account
        account = db.query(Account).first()
        if not account:
            account = Account(
                project_id=project.id,
                platform='THREADS',
                username='kth.101rep',
                display_name='kth.101rep',
                category='IT/테크/전자기기',
                cluster_type='VERTICAL',
                target_audience='IT 기기 및 테크 얼리어답터',
                tone='팩트 중심 전문 분석 어조',
                status='ACTIVE'
            )
            db.add(account)
            db.commit()

        # 3. Products (5 items)
        if db.query(Product).count() == 0:
            sample_products = [
                {
                    'external_id': 'CP-1001',
                    'name': '스탠리 퀜처 H2.0 플로우스테이트 텀블러 887ml',
                    'url': 'https://www.coupang.com/vp/products/1001',
                    'image_url': 'https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=500&auto=format&fit=crop&q=60',
                    'category': '주방용품',
                    'price': 49000,
                    'original_price': 59000,
                    'rating': 4.9,
                    'review_count': 1420,
                    'shipping_type': '로켓배송',
                    'description': '진공 단열 기술로 48시간 얼음 유지. 인체공학적 손잡이와 빨대 뚜껑 일체형 설계.',
                    'source': 'coupang'
                },
                {
                    'external_id': 'CP-1002',
                    'name': '다이슨 에어랩 멀티 스타일러 앤 드라이어 컴플리트 롱',
                    'url': 'https://www.coupang.com/vp/products/1002',
                    'image_url': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&auto=format&fit=crop&q=60',
                    'category': '뷰티/가전',
                    'price': 699000,
                    'original_price': 749000,
                    'rating': 4.8,
                    'review_count': 3240,
                    'shipping_type': '로켓배송',
                    'description': '코안다 효과로 열 손상 없이 자연스러운 컬과 볼륨 연출. 다양한 툴 기본 탑재.',
                    'source': 'coupang'
                },
                {
                    'external_id': 'CP-1003',
                    'name': '샤오미 미지아 스마트 로봇청소기 B101CN 올인원 물걸레',
                    'url': 'https://www.coupang.com/vp/products/1003',
                    'image_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&auto=format&fit=crop&q=60',
                    'category': '생활가전',
                    'price': 389000,
                    'original_price': 450000,
                    'rating': 4.7,
                    'review_count': 890,
                    'shipping_type': '로켓직구',
                    'description': '자동 걸레 세척 및 열풍 건조 스테이션 탑재. LDS 라이다 센서로 스마트 매핑.',
                    'source': 'coupang'
                },
                {
                    'external_id': 'CP-1004',
                    'name': '닥터지 레드 블레미쉬 클리어 수딩 크림 70ml 2개 세트',
                    'url': 'https://www.coupang.com/vp/products/1004',
                    'image_url': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&auto=format&fit=crop&q=60',
                    'category': '뷰티',
                    'price': 28900,
                    'original_price': 36000,
                    'rating': 4.9,
                    'review_count': 12500,
                    'shipping_type': '로켓배송',
                    'description': '10-시카 콤플렉스로 민감해진 피부를 촉촉하게 진정시키는 수분 진정 크림.',
                    'source': 'coupang'
                },
                {
                    'external_id': 'CP-1005',
                    'name': '코멧 홈 고중량 호텔식 페이스타월 200g 10수 10장 세트',
                    'url': 'https://www.coupang.com/vp/products/1005',
                    'image_url': 'https://images.unsplash.com/photo-1616627547584-bf28cee262db?w=500&auto=format&fit=crop&q=60',
                    'category': '리빙/생활',
                    'price': 19900,
                    'original_price': 25000,
                    'rating': 4.6,
                    'review_count': 4580,
                    'shipping_type': '로켓배송',
                    'description': '도톰한 200g 중량감의 최고급 코마사 면 100% 호텔식 수건 세트.',
                    'source': 'coupang'
                }
            ]

            created_prods = []
            for p in sample_products:
                prod = Product(
                    external_id=p['external_id'],
                    name=p['name'],
                    url=p['url'],
                    image_url=p['image_url'],
                    category=p['category'],
                    price=p['price'],
                    original_price=p['original_price'],
                    rating=p['rating'],
                    review_count=p['review_count'],
                    shipping_type=p['shipping_type'],
                    description=p['description'],
                    source=p['source']
                )
                db.add(prod)
                created_prods.append(prod)
            db.commit()
            for prod in created_prods:
                db.refresh(prod)

            # 4. Product Score for Product 1 & 5
            score1 = ProductScore(
                product_id=created_prods[0].id,
                price_score=17,
                review_score=19,
                rating_score=20,
                shipping_score=19,
                conversion_score=18,
                content_score=15,
                seasonality_score=8,
                total_score=88,
                reason='4.9점 압도적 평점과 텀블러 대란 트렌드 덕분에 구매 전환 및 콘텐츠 확장성이 매우 높음.'
            )
            db.add(score1)

            # 5. Product DNA for Product 1
            dna1 = ProductDNA(
                product_id=created_prods[0].id,
                target_person='사무실에 오래 앉아있는 직장인, 운동 좋아하는 2030, 수분 섭취 습관 들이려는 사람',
                problem='얼음이 금방 녹아 미지근해지고 하루에 물 뜨러 정수기 5번씩 왔다갔다 하는 귀찮음',
                use_case='아침 출근길 차 안 컵홀더에 꽂고 퇴근할 때까지 시원한 얼음물 마시기',
                purchase_reason='887ml 대용량 + 차 컵홀더 호환 + 밤새 녹지 않는 극강의 보냉력',
                purchase_barrier='텀블러치고 4만원 후반대의 다소 부담스러운 가격과 무게감',
                benefit='하루 2번만 물 채우면 일일 권장 수분 섭취 완료, 감성적인 책상 인테리어 효과',
                keywords=json.dumps(['스탠리텀블러', '보냉력끝판왕', '사무실꿀템', '차량용텀블러', '직장인필수템'], ensure_ascii=False),
                content_angles=json.dumps(['직장인 물뜨러 가는 귀찮음 종결', '차량 컵홀더에 들어가는 887ml 괴물 용량', '얼음 넣고 24시간 뒤에도 남아있는지 실측'], ensure_ascii=False),
                evidence='평점 4.9점 / 리뷰 1420건 / 실사용자 48시간 얼음 유지 인증 다수',
                ai_summary='보냉력과 887ml 대용량 컵홀더 호환성이 핵심 셀링 포인트인 트렌디 리빙 아이템.'
            )
            db.add(dna1)

            # 6. Content Ideas for Product 1 (3 items)
            ideas1 = [
                ContentIdea(
                    project_id=project.id,
                    product_id=created_prods[0].id,
                    title='[경험담] 사무실 정수기 셔틀 그만두게 된 결정적 이유',
                    angle='경험담',
                    hook='회사에서 물 뜨러 하루 5번 일어나던 거, 이거 사고 1번으로 줄었어요.',
                    target='사무실 집중 근무하는 2030 직장인',
                    problem='자리에서 일어날 때마다 집중 깨지고 얼음은 1시간 만에 녹아버림',
                    desire='오후까지 얼음 동동 띄운 아이스 커피를 계속 마시고 싶음',
                    evidence='887ml 용량이라 2잔이면 하루 수분 섭취 끝, 퇴근 때까지 얼음 살아있음',
                    purpose='신뢰',
                    status='선택'
                ),
                ContentIdea(
                    project_id=project.id,
                    product_id=created_prods[0].id,
                    title='[비교] 저가형 텀블러 3개 버리고 결국 스탠리로 정착한 이유',
                    angle='비교',
                    hook='만원짜리 텀블러 매년 사서 버리지 말고, 그냥 이거 하나로 끝내세요.',
                    target='가성비 찾다가 이중 지출한 경험이 있는 사람',
                    problem='뚜껑 틈새 곰팡이, 컵홀더 안 들어감, 보냉력 2시간 컷',
                    desire='한 번 사서 몇 년간 고장 없이 쓸 튼튼한 텀블러',
                    evidence='스테인리스 18/8 소재, 식기세척기 지원, 컵홀더 하단 슬림형 설계',
                    purpose='판매',
                    status='대기'
                )
            ]
            for idea in ideas1:
                db.add(idea)

        # 7. Prompt Versions default seeds
        default_prompts = [
            ('product_analysis', 'v1', '상품의 메타데이터(가격, 리뷰, 배송, 설명)를 바탕으로 구매 전환 관점의 구조적 특성을 파악한다.', '상품 구조 분석 기본 프롬프트'),
            ('product_scoring', 'v1', '가격(20), 리뷰(20), 구매가능성(20), 콘텐츠소재(15), 문제해결(15), 시즌성(10) 기준으로 100점 만점 평가 및 명확한 근거 산출.', '상품 7개 항목 점수화 엔진'),
            ('product_dna', 'v1', '상품을 콘텐츠 제작 관점에서 타겟, 문제, 사용상황, 장벽, 혜택, 키워드, 각도로 심층 해체.', '상품 DNA 추출 기본 프롬프트'),
            ('content_idea', 'v1', '10가지 콘텐츠 각도(경험담, 문제해결, 비교, 가격/절약, 실수, 반전, 사용상황, 팁, 체크포인트, 예상 밖 활용)를 기반으로 고효율 후킹 아이디어 10개 생성.', '10대 각도 아이디어 생성 엔진'),
            ('threads_writer', 'v1', 'Threads 특화 문체 규칙(한 문장 한 줄, 짧은 문단, 모바일 가독성, 사실 기반, AI 냄새 및 해시태그 배제)을 적용하여 바이럴 본문 작성.', 'Threads 전용 바이럴 작성기 v1'),
            ('comment_writer', 'v1', '본문과 결합할 파트너스 고지 및 구매 유도 댓글 1~3개 생성.', '댓글 및 광고 고지 작성기 v1')
        ]
        for name, ver, pr, desc in default_prompts:
            exist_pv = db.query(PromptVersion).filter(PromptVersion.name == name, PromptVersion.version == ver).first()
            if not exist_pv:
                pv = PromptVersion(name=name, version=ver, prompt=pr, description=desc, active=True)
                db.add(pv)

        db.commit()
        print('Seed executed successfully!')
    finally:
        db.close()

if __name__ == '__main__':
    run_seed()
