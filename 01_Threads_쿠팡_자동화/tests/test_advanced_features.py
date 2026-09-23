import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import Base, Product, Content, Comment
from database.repository import Repository
from services.ab_test_service import ABTestService
from services.notification_service import NotificationService
from services.bulk_import_service import BulkImportService

@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_product(test_db):
    repo = Repository(test_db)
    return repo.create_product({
        "external_id": "TEST_PROD_AB",
        "name": "프리미엄 텀블러",
        "category": "주방",
        "price": 35000,
        "rating": 4.8,
        "review_count": 500,
        "url": "https://coupang.com/ab_test",
        "description": "보냉 48시간 유지 텀블러"
    })

def test_ab_test_generation_and_evaluation(test_db, test_product):
    ab_svc = ABTestService(test_db)

    # 1. Generate A/B test variants
    ab_res = ab_svc.create_ab_test_variants(
        product_id=test_product.id,
        variant_a_mode="직장인 공감형",
        variant_b_mode="짧은 호흡형",
        hours_apart=6
    )

    assert ab_res["status"] == "SUCCESS"
    assert "variant_a" in ab_res
    assert "variant_b" in ab_res
    assert ab_res["variant_a"]["content_id"] != ab_res["variant_b"]["content_id"]

    # 2. Add metrics for A and B
    repo = Repository(test_db)
    id_a = ab_res["variant_a"]["content_id"]
    id_b = ab_res["variant_b"]["content_id"]

    repo.record_performance_metric(content_id=id_a, views=1000, likes=50, replies=5, reposts=2, clicks=80, conversions=5, revenue=5000)
    repo.record_performance_metric(content_id=id_b, views=1000, likes=20, replies=2, reposts=1, clicks=30, conversions=1, revenue=1000)

    # 3. Evaluate winner
    winner_res = ab_svc.evaluate_ab_winner(id_a, id_b)
    assert winner_res["winner"] == "A"
    assert winner_res["winner_content_id"] == id_a

def test_notification_service_simulated():
    notif = NotificationService()
    # Simulated dispatch without webhook URL
    ok1 = notif.send_post_published_alert(title="테스트 글", post_id="th_12345")
    assert ok1 is True

    ok2 = notif.send_daily_learning_report(best_angle="경험담", total_views=15000, total_clicks=600, revenue=18000)
    assert ok2 is True

def test_bulk_import_service(test_db):
    bulk_svc = BulkImportService(test_db)
    keywords = ["텀블러", "버티컬 마우스"]

    result = bulk_svc.process_bulk_keywords(keywords=keywords, base_interval_hours=4)
    assert result["status"] == "SUCCESS"
    assert result["total_processed"] == 2
    assert result["success_count"] == 2
    assert len(result["results"]) == 2