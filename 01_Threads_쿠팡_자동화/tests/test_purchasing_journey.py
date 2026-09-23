# -*- coding: utf-8 -*-
"""
6단계 구매여정 설득 프레임워크 & 롱테일 호기심 키워드 & 공정위 가드레일 유닛 테스트
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from services.purchasing_journey_service import (
    PurchasingJourneyService,
    DISCLOSURE_NAVER,
    DISCLOSURE_COUPANG,
    FORBIDDEN_CLICHES
)
from database.connection import SessionLocal
from database.models import Product

@pytest.fixture
def test_product():
    db = SessionLocal()
    prod = db.query(Product).first()
    if not prod:
        prod = Product(
            external_id="TEST_PJ_001",
            name="바이탈플랜트 회전 자동 롤팬 26cm 인덕션겸용",
            url="https://www.coupang.com/vp/products/123456",
            category="주방용품",
            price=39900,
            original_price=59900,
            rating=4.8,
            review_count=1820,
            shipping_type="로켓배송",
            description="고기 굽기 편리한 회전 롤팬"
        )
        db.add(prod)
        db.commit()
        db.refresh(prod)
    db.close()
    return prod

def test_curiosity_keywords_generation(test_product):
    service = PurchasingJourneyService()
    product_dict = {
        "id": test_product.id,
        "name": test_product.name,
        "category": test_product.category,
        "price": test_product.price,
        "rating": test_product.rating,
        "review_count": test_product.review_count
    }
    keywords = service.generate_curiosity_keywords(product_dict)
    
    assert len(keywords) == 5
    type_codes = [k["type_code"] for k in keywords]
    assert "BROADCAST_ISSUE" in type_codes
    assert "MICRO_PERSONA" in type_codes
    assert "FAILURE_OVERCOME" in type_codes
    assert "PRICE_EFFICIENCY" in type_codes
    assert "FLAW_ANALYSIS" in type_codes

    for item in keywords:
        assert len(item["keyword"]) > 10
        assert "headline" in item
        assert "target_intent" in item

def test_6step_content_structure_and_naver_compliance(test_product):
    service = PurchasingJourneyService()
    product_dict = {
        "id": test_product.id,
        "name": test_product.name,
        "category": test_product.category,
        "price": test_product.price,
        "rating": test_product.rating,
        "review_count": test_product.review_count
    }
    res = service.generate_6step_content(
        product=product_dict,
        platform="NAVER_SHOPPING",
        tone="EMPATHY_STORY"
    )

    # 1. 6단계 키 확인
    steps = res["steps"]
    assert "step1_persona" in steps
    assert "step2_hook" in steps
    assert "step3_problem" in steps
    assert "step4_point" in steps
    assert "step5_pros_cons" in steps
    assert "step6_cta" in steps

    # 2. 본문 최상단 필수 공정위 문구 확인
    body = res["body"]
    first_line = body.strip().split("\n")[0]
    assert first_line == DISCLOSURE_NAVER

    # 3. 내돈내산 금지 확인 (쇼핑커넥트 2회 적발 영구정지 방지)
    assert "내돈내산" not in body

    # 4. Anti-Cliche 검증
    for cliche in FORBIDDEN_CLICHES:
        assert cliche not in body

    # 5. Suno AI BGM 프롬프트 확인
    suno = res["suno_bgm"]
    assert "BPM" in suno["bpm"]
    assert len(suno["suno_prompt"]) > 20
    assert "Instrumental" in suno["suno_prompt"]

    # 6. 30초 숏폼 대본 확인
    shortform = res["shortform_script"]
    assert shortform["duration"] == "30초"
    assert len(shortform["scenes"]) == 4

def test_purchasing_journey_api_endpoints(test_product):
    client = TestClient(app)

    # 1. Keywords API
    res_kw = client.post(f"/api/workflow/purchasing-journey/keywords/{test_product.id}")
    assert res_kw.status_code == 200
    data_kw = res_kw.json()
    assert data_kw["status"] == "SUCCESS"
    assert data_kw["count"] == 5

    # 2. Content Generation API
    res_gen = client.post(
        "/api/workflow/purchasing-journey/generate",
        json={
            "product_id": test_product.id,
            "platform": "NAVER_SHOPPING"
        }
    )
    assert res_gen.status_code == 200
    data_gen = res_gen.json()
    assert data_gen["status"] == "SUCCESS"
    assert "result" in data_gen
    assert DISCLOSURE_NAVER in data_gen["result"]["body"]

    # 3. Compliance Guardrail Check API
    dirty_body = "결론부터 말하면 여러분 이거 진짜 내돈내산 꿀템입니다."
    res_comp = client.post(
        "/api/workflow/purchasing-journey/compliance-check",
        json={
            "body": dirty_body,
            "platform": "NAVER_SHOPPING"
        }
    )
    assert res_comp.status_code == 200
    data_comp = res_comp.json()
    assert data_comp["original_had_naedon_conflict"] is True
    assert data_comp["original_had_ai_cliches"] is True
    assert DISCLOSURE_NAVER in data_comp["sanitized_body"]
    assert "내돈내산" not in data_comp["sanitized_body"]
