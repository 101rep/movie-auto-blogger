import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import Base, Product, Content, Comment
from database.repository import Repository
from services.autopilot_service import AutopilotService
from services.scheduler_service import SchedulerService
from integrations.coupang_api import CoupangPartnersAPI
from integrations.threads_api import ThreadsOfficialAPI

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

def test_coupang_api_integration():
    api = CoupangPartnersAPI()
    results = api.search_products("텀블러", limit=3)
    assert len(results) > 0
    assert results[0].name != ""
    assert results[0].price > 0

    deeplinks = api.generate_deeplink(["https://www.coupang.com/vp/products/1001"])
    assert len(deeplinks) == 1
    assert "shorten" in deeplinks[0]

def test_threads_api_integration():
    api = ThreadsOfficialAPI()
    post_res = api.publish_post(text="테스트 본문입니다.")
    assert post_res["status"] == "SUCCESS"
    assert "post_id" in post_res

    reply_res = api.publish_reply(parent_id=post_res["post_id"], text="테스트 댓글입니다.")
    assert reply_res["status"] == "SUCCESS"

    metrics = api.get_metrics(post_res["post_id"])
    assert metrics["views"] >= 0
    assert metrics["likes"] >= 0

def test_autopilot_service_pipeline(test_db):
    service = AutopilotService(test_db)
    result = service.run_autopilot(keyword="스탠리", schedule_hours_later=3)

    assert result["status"] == "SUCCESS"
    assert result["keyword"] == "스탠리"
    assert result["product_id"] is not None
    assert result["content_id"] is not None
    assert result["title"] != ""
    assert len(result["steps"]) >= 9

    # Check that post was saved as APPROVED and SCHEDULED
    repo = Repository(test_db)
    content = repo.get_content(result["content_id"])
    assert content is not None
    assert content.status == "SCHEDULED"
    assert content.scheduled_at is not None
    assert len(content.comments) >= 2

def test_background_due_schedule_publishing(test_db):
    repo = Repository(test_db)
    prod = repo.create_product({
        "external_id": "TEST_DUE_01",
        "name": "만기 예약 테스트 상품",
        "category": "리빙",
        "price": 20000,
        "rating": 4.5,
        "review_count": 100,
        "url": "https://coupang.com/due_test",
        "description": "설명"
    })
    # Content scheduled in the past (due for publish)
    content = repo.create_content(
        product_id=prod.id,
        title="만기 발행 테스트",
        body="자동 발행되어야 하는 글입니다.",
        status="SCHEDULED",
        comments=[{"sequence": 1, "body": "공정위 문구 포함 댓글", "link": "https://coupang.com"}]
    )
    content.scheduled_at = datetime.utcnow() - timedelta(minutes=5)
    test_db.commit()

    sched_svc = SchedulerService(test_db)
    published_ids = sched_svc.process_due_schedules()

    assert content.id in published_ids
    test_db.refresh(content)
    assert content.status == "PUBLISHED"