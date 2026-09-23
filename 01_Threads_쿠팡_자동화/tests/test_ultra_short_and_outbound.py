# -*- coding: utf-8 -*-
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Account, Product, OutboundInteraction
from prompts.hook_vault import HOOK_VAULT, get_hook, get_all_hooks_count
from services.threads_writer_service import ThreadsWriterService
from services.outbound_service import OutboundInteractionService
from services.shortform_service import ShortformScriptService
from services.warmup_evaluator import WarmupEvaluationService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_hook_vault_coverage():
    """도파민 훅 뱅크 100선 및 7개 카테고리 정상 작동 테스트"""
    total_count = get_all_hooks_count()
    assert total_count >= 100, f"Expected >= 100 hooks, got {total_count}"
    
    categories = [
        "REVERSAL_DOPAMINE", "LOSS_AVERSION", "TOSS_COOP_DEAL",
        "ULTRA_SHORT", "INSIDER_WHISTLEBLOWER", "DAILY_REALITY", "SECRET_HACK"
    ]
    for cat in categories:
        hook = get_hook(cat, "테스트 상품")
        assert hook is not None
        assert len(hook) > 10


def test_ultra_short_post_generation(db_session):
    """ultra_short 3줄 초압축 텍스트 모드 생성 테스트"""
    account = Account(
        username="tech_it_pro",
        category="IT_TECH",
        target_audience="2030 직장인"
    )
    product = Product(
        external_id="BELKIN_TEST_01",
        name="벨킨 3in1 고속 충전기",
        url="https://coupang.com/vp/products/12345",
        price=89000,
        rating=4.9,
        review_count=3500,
        category="IT_TECH"
    )
    db_session.add_all([account, product])
    db_session.commit()

    service = ThreadsWriterService(db_session)
    post = service.generate_post(
        product_id=product.id,
        rewrite_mode="ultra_short"
    )

    assert post is not None
    assert post.body is not None
    lines = [l.strip() for l in post.body.strip().split("\n") if l.strip()]
    assert len(lines) >= 3
    # 3rd line must include profile search guidance
    assert any("프로필" in l and "검색" in l for l in lines)


def test_outbound_interaction_service(db_session):
    """선소통(스하리) 웜업 서비스 및 일일 상한선(10건) 테스트"""
    account = Account(
        username="living_master",
        category="LIVING",
        target_audience="주부 및 1인가구"
    )
    db_session.add(account)
    db_session.commit()

    # 1. First interaction
    record = OutboundInteractionService.perform_outbound_interaction(db_session, account.id)
    assert record is not None
    assert record.account_id == account.id
    assert record.target_author.startswith("@")
    assert len(record.comment_body) > 5
    assert 180 <= record.jitter_delay_sec <= 900

    # 2. Daily limit enforcement (reach 10)
    for _ in range(9):
        OutboundInteractionService.perform_outbound_interaction(db_session, account.id)

    stats = OutboundInteractionService.get_outbound_stats(db_session, account.id)
    assert stats["total_outbound_count"] == 10

    # 11th interaction should be blocked by safety limit
    blocked = OutboundInteractionService.perform_outbound_interaction(db_session, account.id)
    assert blocked is None


def test_shortform_script_service():
    """15초 바이럴 숏폼 대본 생성기 테스트"""
    product = {
        "title": "아누아 어성초 토너",
        "price": 18900,
        "rating": 4.8,
        "review_count": 2100,
        "category": "BEAUTY",
        "item_number": 202
    }
    script = ShortformScriptService.generate_15s_script(
        product=product,
        account_username="beauty_pick",
        item_number=202
    )

    assert script["target_duration"] == "15초 초압축"
    assert script["item_number"] == 202
    assert len(script["scenes"]) == 3
    assert script["scenes"][0]["timestamp"] == "00:00 - 00:03"
    assert script["scenes"][1]["timestamp"] == "00:03 - 00:10"
    assert script["scenes"][2]["timestamp"] == "00:10 - 00:15"
    assert "202" in script["scenes"][2]["caption"]
    assert "#릴스" in script["hashtags"]
    assert len(script["full_narration"]) > 50


def test_trust_score_with_outbound_interactions(db_session):
    """스하리 소통이 WarmupEvaluationService 신뢰도 점수 및 졸업에 기여하는지 테스트"""
    account = Account(
        username="deal_hunter",
        category="HOT_DEAL",
        trust_score=40.0
    )
    db_session.add(account)
    db_session.commit()

    warmup_svc = WarmupEvaluationService(db_session)

    # Before outbound interactions
    eval_before = warmup_svc.evaluate_account(account.id)
    score_before = eval_before["trust_score"]

    # Add 5 outbound interactions
    for i in range(5):
        interaction = OutboundInteraction(
            account_id=account.id,
            target_author=f"@user_{i}",
            target_post_snippet="핫딜 정보 감사합니다",
            comment_body="정말 유용한 정보네요!",
            niche_category="HOT_DEAL",
            jitter_delay_sec=200,
            status="SUCCESS"
        )
        db_session.add(interaction)
    db_session.commit()

    eval_after = warmup_svc.evaluate_account(account.id)
    score_after = eval_after["trust_score"]

    # Outbound comments simulate authentic replies and boost trust score
    assert score_after > score_before


def test_browser_launcher_service(db_session):
    """PC 브라우저 격리 런처 및 프로필 분리 테스트"""
    from services.browser_launcher_service import BrowserLauncherService

    account = Account(
        username="test_launcher",
        category="LIVING",
        login_password="q1w2e3r4!!"
    )
    db_session.add(account)
    db_session.commit()

    profile_dir = BrowserLauncherService.get_profile_dir(account.username)
    assert "threads_test_launcher" in profile_dir

    exe = BrowserLauncherService.get_browser_executable()
    assert exe is not None

    shortcuts = BrowserLauncherService.create_desktop_shortcuts([account])
    assert shortcuts["status"] == "SUCCESS"
    assert shortcuts["count"] >= 1
