import pytest
from services.product_service import ProductService

def test_duplicate_external_id_prevention(db_session):
    svc = ProductService(db_session)
    product_data = {
        "external_id": "DUP-100",
        "name": "중복 방지 테스트 상품 A",
        "url": "https://coupang.com/dup-a",
        "category": "리빙",
        "price": 10000,
        "rating": 4.5,
        "review_count": 100
    }

    prod1 = svc.save_product(product_data)
    assert prod1.id is not None

    # Save same external_id again with updated price
    updated_data = dict(product_data)
    updated_data["price"] = 12000
    prod2 = svc.save_product(updated_data)

    assert prod1.id == prod2.id
    assert prod2.price == 12000

def test_duplicate_url_prevention(db_session):
    svc = ProductService(db_session)
    p1 = svc.save_product({
        "external_id": "DUP-URL-1",
        "name": "URL 중복 테스트 상품 1",
        "url": "https://coupang.com/same-url",
        "category": "리빙",
        "price": 20000
    })

    # Save different external_id but SAME URL
    p2 = svc.save_product({
        "external_id": "DUP-URL-2",
        "name": "URL 중복 테스트 상품 2",
        "url": "https://coupang.com/same-url",
        "category": "리빙",
        "price": 25000
    })

    assert p1.id == p2.id