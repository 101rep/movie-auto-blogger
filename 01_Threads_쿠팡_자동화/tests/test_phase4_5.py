import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import (
    Base, Product, ContentIdea, Content, Comment,
    PerformanceMetric, LearningInsight, Account
)
from database.repository import Repository
from services.product_service import ProductService
from services.review_service import ReviewService
from services.scheduler_service import SchedulerService
from services.analytics_service import AnalyticsService
from services.learning_service import LearningService
from services.account_service import AccountService


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
def seeded_content(test_db):
    repo = Repository(test_db)
    prod = repo.create_product({
        "external_id": "TEST_PROD_001",
        "name": "에르고노믹 초경량 버티컬 마우스",
        "category": "디지털/가전",
        "price": 45000,
        "rating": 4.8,
        "review_count": 850,
        "url": "https://coupang.com/test",
        "description": "손목 통증 완화, 무소음 클릭 마우스"
    })
    idea = ContentIdea(
        product_id=prod.id,
        title="[경험담] 하루 8시간 마우스 쥐는 분들...",
        angle="경험담",
        hook="하루 8시간 마우스 쥐는 분들, 손목 안 아프신가요?",
        target="사무직 직장인",
        problem="손목 터널 증후군",
        desire="통증 없는 편안한 업무",
        evidence="버티컬 마우스 사용 후 통증 완화",
        purpose="손목 보호 마우스 추천",
        status="대기"
    )
    test_db.add(idea)
    test_db.commit()
    test_db.refresh(idea)

    content = repo.create_content(
        product_id=prod.id,
        idea_id=idea.id,
        title="손목 구출 버티컬 마우스",
        body="하루 8시간 마우스 쥐는 분들, 손목 안 아프신가요?\n버티컬 마우스로 바꾼 뒤 손목 시림이 사라졌습니다.\n댓글에서 자세한 모델명 확인해보세요.",
        status="APPROVED",
        comments=[
            {
                "sequence": 1,
                "body": "이 포스팅은 쿠팡 파트너스 활동의 일환으로 이에 따른 일정액의 수수료를 제공받습니다.\n추천 모델: https://link.coupang.com/test",
                "link": "https://link.coupang.com/test"
            }
        ]
    )
    return prod, idea, content


def test_review_service_pass(test_db, seeded_content):
    prod, idea, content = seeded_content
    review_svc = ReviewService(test_db)

    result = review_svc.audit_content(content.id)
    assert result.policy_passed is True
    assert result.quality_score >= 80
    assert result.duplicate_score >= 0.0
    assert result.readability_level in ["우수", "보통"]


def test_review_service_policy_missing(test_db, seeded_content):
    prod, idea, content = seeded_content
    repo = Repository(test_db)
    bad_content = repo.create_content(
        product_id=prod.id,
        idea_id=idea.id,
        title="공정위 미표기 테스트 글",
        body="정말 좋은 마우스입니다. 구매 링크는 댓글에 있어요.",
        status="DRAFT",
        comments=[
            {
                "sequence": 1,
                "body": "구매처는 여기입니다: https://link.coupang.com/test",
                "link": "https://link.coupang.com/test"
            }
        ]
    )

    review_svc = ReviewService(test_db)
    result = review_svc.audit_content(bad_content.id)
    assert result.policy_passed is False
    assert "공정위" in result.feedback


def test_scheduler_service_lifecycle(test_db, seeded_content):
    prod, idea, content = seeded_content
    sched_svc = SchedulerService(test_db)

    # 1. 예약 등록
    scheduled_time = datetime.now() + timedelta(hours=2)
    updated_content = sched_svc.schedule_content(content.id, scheduled_time)
    assert updated_content.status == "SCHEDULED"
    assert updated_content.scheduled_at is not None

    # 2. 캘린더 이벤트 조회
    events = sched_svc.get_calendar_events()
    assert len(events) >= 1
    found = any(e["id"] == content.id for e in events)
    assert found is True

    # 3. 예약 취소
    canceled = sched_svc.cancel_schedule(content.id)
    assert canceled.status == "APPROVED"
    assert canceled.scheduled_at is None

    # 4. 즉시 발행
    publish_res = sched_svc.publish_now(content.id)
    assert publish_res["status"] == "SUCCESS"
    assert publish_res["post_id"].startswith("th_") or publish_res["post_id"].startswith("mock_th_")


def test_analytics_and_learning_lifecycle(test_db, seeded_content):
    prod, idea, content = seeded_content
    sched_svc = SchedulerService(test_db)
    analytics_svc = AnalyticsService(test_db)
    learning_svc = LearningService(test_db)

    # 1. 발행
    sched_svc.publish_now(content.id)

    # 2. 메트릭 동기화
    metric = analytics_svc.sync_metrics_from_provider(content.id)
    assert metric is not None
    assert metric.views > 0
    assert metric.clicks > 0

    # 3. 종합 리포트
    report = analytics_svc.get_summary_report()
    assert report["total_views"] > 0
    assert "angle_stats" in report

    # 4. 자가 학습 인사이트 도출
    insight = learning_svc.analyze_and_learn()
    assert insight is not None
    assert insight.best_angle is not None
    assert "price" in insight.suggested_weight_adjustments


def test_account_service_crud(test_db):
    acc_svc = AccountService(test_db)

    # 1. 계정 등록
    new_acc = acc_svc.create_account({
        "username": "tester_curator",
        "display_name": "스마트 살림 큐레이터",
        "platform": "THREADS",
        "category": "생활용품",
        "tone": "친근한 일상체"
    })
    assert new_acc.id is not None
    assert new_acc.username == "tester_curator"

    # 2. 계정 목록
    accounts = acc_svc.list_accounts()
    assert len(accounts) == 1

    # 3. 단일 조회
    found = acc_svc.get_account(new_acc.id)
    assert found is not None
    assert found.display_name == "스마트 살림 큐레이터"