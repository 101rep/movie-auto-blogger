import pytest
from services.product_service import ProductService
from services.scoring_service import ProductScoringService
from services.dna_service import ProductDNAService
from services.idea_service import ContentIdeaService
from services.threads_writer_service import ThreadsWriterService
from services.comment_service import CommentService
from domain_types.schemas import ProductScoreWeights

def test_product_service_search_and_save(db_session):
    svc = ProductService(db_session)
    results = svc.search_external_products(query="스탠리")
    assert len(results) > 0
    item = results[0]

    saved = svc.save_product(item.model_dump())
    assert saved.id is not None
    assert saved.external_id == item.external_id

    fetched = svc.get_product(saved.id)
    assert fetched is not None
    assert fetched.name == item.name

def test_scoring_service(db_session):
    prod_svc = ProductService(db_session)
    prod = prod_svc.save_product({
        "external_id": "TEST-SCORE-01",
        "name": "테스트 고품질 텀블러",
        "url": "https://coupang.com/test-score",
        "category": "주방용품",
        "price": 35000,
        "rating": 4.9,
        "review_count": 2500,
        "shipping_type": "로켓배송",
        "description": "보냉력 우수"
    })

    score_svc = ProductScoringService(db_session)
    score = score_svc.score_product(prod.id)

    assert score is not None
    assert score.total_score >= 80
    assert "평점" in score.reason or "리뷰" in score.reason
    assert score.product_id == prod.id

def test_dna_service(db_session):
    prod_svc = ProductService(db_session)
    prod = prod_svc.save_product({
        "external_id": "TEST-DNA-01",
        "name": "테스트 로봇청소기",
        "url": "https://coupang.com/test-dna",
        "category": "생활가전",
        "price": 350000,
        "rating": 4.8,
        "review_count": 1200,
        "shipping_type": "로켓배송"
    })

    dna_svc = ProductDNAService(db_session)
    dna = dna_svc.generate_dna(prod.id)

    assert dna is not None
    assert dna.target_person != ""
    assert dna.problem != ""
    assert dna.benefit != ""
    assert dna.ai_summary != ""

def test_idea_service(db_session):
    prod_svc = ProductService(db_session)
    prod = prod_svc.save_product({
        "external_id": "TEST-IDEA-01",
        "name": "테스트 캡슐커피머신",
        "url": "https://coupang.com/test-idea",
        "category": "주방용품",
        "price": 120000,
        "rating": 4.8,
        "review_count": 900
    })

    idea_svc = ContentIdeaService(db_session)
    ideas = idea_svc.generate_ideas_for_product(prod.id)

    assert len(ideas) == 10
    angles = [i.angle for i in ideas]
    assert "경험담" in angles
    assert "문제 해결" in angles
    assert "비교" in angles
    assert "가격/절약" in angles
    assert "실수" in angles

def test_threads_writer_and_comments(db_session):
    prod_svc = ProductService(db_session)
    prod = prod_svc.save_product({
        "external_id": "TEST-WRITE-01",
        "name": "테스트 호텔 수건",
        "url": "https://coupang.com/test-write",
        "category": "리빙/생활",
        "price": 20000,
        "rating": 4.7,
        "review_count": 3000
    })

    writer_svc = ThreadsWriterService(db_session)
    post = writer_svc.generate_post(prod.id, rewrite_mode="short")

    assert post.body != ""
    assert "#" not in post.body # No hashtags rule
    assert "여러분" not in post.body # No AI cliches rule

    comment_svc = CommentService(db_session)
    comments = comment_svc.generate_comments(prod.id)

    assert len(comments) >= 1
    assert "수수료" in comments[0].body # Disclosure included