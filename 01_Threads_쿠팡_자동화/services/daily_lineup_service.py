# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Account, Product, Content
from services.account_service import AccountService
from services.product_service import ProductService

class DailyLineupService:
    ACCOUNT_PERSONA_SPECS = {
        2: {
            "username": "kth.101rep",
            "name": "IT 테크 큐레이터",
            "category": "디지털/가전/테크",
            "format": "스펙 비교 & 분석형 카드뉴스",
            "seed_keywords": ["버티컬 마우스", "초고속 멀티 충전기", "모니터 스크린바", "기계식 키보드", "노트북 거치대"],
            "role": "IT 전문 스펙 분석"
        },
        12: {
            "username": "toontoooon",
            "name": "툰툰이의 귀여운 꿀템",
            "category": "캐릭터/팬시/자취/데스크",
            "format": "호들갑 바이럴 4컷 인스타툰",
            "seed_keywords": ["귀여운 데스크 소품", "자취 필수템", "모니터 메모보드", "미니 탁상 가습기", "감성 탁상시계"],
            "role": "자취생 귀여운 공감 인스타툰"
        },
        13: {
            "username": "lookatmeai",
            "name": "룩앳미 AI 뷰티&트렌드",
            "category": "뷰티/패션/스킨케어",
            "format": "감각적인 매거진 에디토리얼 카드뉴스",
            "seed_keywords": ["올리브영 1위 세럼", "시카 수분크림", "속눈썹 영양제", "톤업 선크림", "워터 틴트"],
            "role": "2030 여성 감각 뷰티 트렌드"
        },
        14: {
            "username": "taechi.tube",
            "name": "태치튜브 감성 라이프",
            "category": "여행/캠핑/감성소품/아웃도어",
            "format": "웜톤 감성 라이프스타일 카드뉴스",
            "seed_keywords": ["초경량 캠핑 체어", "감성 충전식 무드등", "휴대용 에스프레소 머신", "차박 에어매트", "트래블 파우치"],
            "role": "캠핑/여행족 감성 라이프"
        },
        15: {
            "username": "101rep80",
            "name": "호구탈출 가성비 핫딜",
            "category": "디지털/가성비비교/특가/최저가",
            "format": "고대비 경고형 팩트체크 카드뉴스",
            "seed_keywords": ["가성비 무선청소기", "가성비 노이즈캔슬링 헤드폰", "초저가 에어프라이어", "쿠팡 반값 핫딜"],
            "role": "호구 안되는 가성비 팩트체커"
        },
        16: {
            "username": "yr170425",
            "name": "살림로그 스마트 리빙",
            "category": "리빙/주방/수납정리/청소",
            "format": "클린 정보성 살림백서 카드뉴스",
            "seed_keywords": ["냉장고 밀폐 정리용기", "실리콘 조리도구 5종", "먼지 틈새 브러쉬", "무타공 주방선반", "스마트 센서 휴지통"],
            "role": "1인가구/주부 살림 꿀팁러"
        },
        17: {
            "username": "ktaehoon80",
            "name": "30대 직장인의 현실생존",
            "category": "직장인생존템/피로회복/건강",
            "format": "현실 공감 흑백툰 & 생존 브리핑",
            "seed_keywords": ["거북목 교정 경추베개", "손목 터널증후군 마우스패드", "밀크씨슬 피로회복제", "온열 마사지 안대", "등받이 쿠션"],
            "role": "3040 직장인 흑백 고충 공감"
        }
    }

    def __init__(self, db: Session):
        self.db = db
        self.acc_svc = AccountService(db)
        self.prod_svc = ProductService(db)

    def plan_daily_lineup(self, user_products: List[Product] = None) -> Dict[str, Any]:
        target_acc_ids = list(self.ACCOUNT_PERSONA_SPECS.keys())
        all_products = user_products or []
        assignments = {acc_id: [] for acc_id in target_acc_ids}

        # 1. 대표님 전달 품목 1-1 매칭
        for prod in all_products:
            acc_id = self.find_best_persona_account(prod)
            assignments[acc_id].append({
                "source_type": "USER_SUBMITTED",
                "product_id": prod.id,
                "product_name": prod.name,
                "category": prod.category,
                "price": prod.price,
                "description": "대표님 전달 상품 1-1 배정"
            })

        # 2. 비어있는 계정용 쿠팡 자동 충원
        auto_filled_items = []
        for acc_id, items in assignments.items():
            if len(items) == 0:
                spec = self.ACCOUNT_PERSONA_SPECS[acc_id]
                kw = spec["seed_keywords"][0]
                scouted = self.prod_svc.search_external_products(kw, limit=1)
                if scouted:
                    top_p = scouted[0]
                    saved_p = self.prod_svc.save_product(top_p.model_dump())
                    item_data = {
                        "source_type": "COUPANG_AUTO_FILL",
                        "product_id": saved_p.id,
                        "product_name": saved_p.name,
                        "category": saved_p.category,
                        "price": saved_p.price,
                        "description": f"{spec['name']} 전담 쿠팡 1위 자동 스카우트"
                    }
                    assignments[acc_id].append(item_data)
                    auto_filled_items.append({
                        "account_id": acc_id,
                        "account": spec["username"],
                        "persona": spec["name"],
                        "product": saved_p.name
                    })

        return {
            "total_accounts": len(target_acc_ids),
            "user_products_count": len(all_products),
            "auto_filled_count": len(auto_filled_items),
            "assignments": assignments,
            "auto_fill_items": auto_filled_items
        }

    def find_best_persona_account(self, prod: Product) -> int:
        text = f"{prod.category or ''} {prod.name or ''}".lower()
        if any(k in text for k in ["뷰티", "메이크업", "틴트", "세럼", "크림", "올리브영", "스킨", "로션", "팩트", "쿠션", "섀도우", "라이너"]):
            return 13
        if any(k in text for k in ["주방", "식기", "밀폐", "정리용", "수납", "청소", "선반", "살림", "세제", "수건"]):
            return 16
        if any(k in text for k in ["마우스", "키보드", "충전기", "케이블", "모니터", "거치대", "스마트", "기계식", "로봇"]):
            return 2
        if any(k in text for k in ["벽시계", "시계", "체어", "의자", "소파", "거울", "미러", "자취", "데스크", "귀여운", "소품"]):
            return 12
        if any(k in text for k in ["캠핑", "텐트", "버너", "차박", "랜턴", "아웃도어", "여행", "파우치"]):
            return 14
        if any(k in text for k in ["베개", "경추", "안마", "마사지", "영양제", "비타민", "밀크씨슬", "눈찜질", "스트레칭", "손목"]):
            return 17
        return 15
