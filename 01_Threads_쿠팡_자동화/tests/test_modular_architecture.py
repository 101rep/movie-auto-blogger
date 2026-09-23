import pytest
import time
from database.repository import Repository
from database.models import Account, Content, Product
from utils.cache import SimpleTTLCache
from services.account_service import AccountService
from services.scheduler_service import SchedulerService

def test_ttl_cache_basic_and_expiry():
    cache = SimpleTTLCache(default_ttl=1)
    cache.set("key1", "value1", ttl=1)
    assert cache.get("key1") == "value1"
    
    # Wait for TTL to pass
    time.sleep(1.1)
    assert cache.get("key1") is None

def test_ttl_cache_prefix_invalidation():
    cache = SimpleTTLCache(default_ttl=60)
    cache.set("accounts:1", {"id": 1})
    cache.set("accounts:2", {"id": 2})
    cache.set("products:1", {"id": 10})

    deleted = cache.clear_prefix("accounts:")
    assert deleted == 2
    assert cache.get("accounts:1") is None
    assert cache.get("accounts:2") is None
    assert cache.get("products:1") is not None

def test_account_smart_routing(db_session):
    service = AccountService(db_session)
    
    # Create accounts across clusters
    v_acc = service.create_account({
        "username": "home_stylist",
        "display_name": "홈스타일리스트",
        "category": "리빙/생활용품",
        "cluster_type": "VERTICAL",
        "tone": "차분한 톤"
    })
    
    p_acc = service.create_account({
        "username": "solo_life_pro",
        "display_name": "자취프로",
        "category": "자취/1인가구",
        "cluster_type": "PERSONA",
        "tone": "자취생 공감 톤"
    })

    # 1. Matching by category
    matched = service.find_best_account_for_product(product_category="리빙/생활용품", product_name="원목 선반")
    assert matched is not None
    assert matched.username == "home_stylist"

    # 2. Matching by keyword in product name when vertical category doesn't match
    matched2 = service.find_best_account_for_product(product_category="소형가전", product_name="자취 필수템 미니 건조기")
    assert matched2 is not None
    assert matched2.username == "solo_life_pro"

def test_content_account_assignment_and_calendar(db_session):
    repo = Repository(db_session)
    acc = repo.create_account({
        "username": "tech_curator",
        "display_name": "테크 큐레이터",
        "category": "디지털/가전",
        "cluster_type": "VERTICAL"
    })

    prod = repo.create_product({
        "external_id": "test_tech_001",
        "name": "무소음 블루투스 마우스",
        "url": "https://coupang.com/vp/products/tech001",
        "category": "디지털/가전",
        "price": 25000
    })

    content = repo.create_content(
        product_id=prod.id,
        title="손목 통증 해방 무소음 마우스",
        body="사무실 필수템 마우스 추천",
        account_id=acc.id,
        status="APPROVED"
    )
    assert content.account_id == acc.id

    # Test update content account
    acc2 = repo.create_account({
        "username": "office_hero",
        "display_name": "직장인 오피스템",
        "category": "오피스/사무",
        "cluster_type": "PERSONA"
    })
    updated = repo.update_content_account(content.id, acc2.id)
    assert updated.account_id == acc2.id

    # Test scheduler calendar event includes account
    sched_svc = SchedulerService(db_session)
    now = time.time()
    from datetime import datetime, timedelta
    sched_svc.schedule_content(content.id, datetime.utcnow() + timedelta(hours=2))
    
    events = sched_svc.get_calendar_events()
    assert len(events) >= 1
    ev = next(e for e in events if e["id"] == content.id)
    assert ev["account_username"] == "office_hero"
    assert ev["account_cluster"] == "PERSONA"

def test_threads_v2_algorithm_safety_and_warmup(db_session):
    from services.autopilot_service import AutopilotService
    from services.comment_service import CommentService
    from database.repository import Repository
    
    repo = Repository(db_session)
    
    # 1. Create a warm-up account
    warm_acc = repo.create_account({
        "username": "newbie_curator",
        "display_name": "신규 큐레이터",
        "category": "뷰티/스킨케어",
        "cluster_type": "VERTICAL",
        "warmup_status": "WARMING_UP",
        "post_ratio_mode": "MIX_4_TO_1",
        "organic_streak": 2
    })
    assert warm_acc.warmup_status == "WARMING_UP"
    
    # Toggle warmup status
    updated_acc = repo.update_account_warmup(warm_acc.id, "ACTIVE")
    assert updated_acc.warmup_status == "ACTIVE"
    
    # 2. Test Comment Service Strategies
    comm_svc = CommentService(db_session)
    prod = repo.create_product({
        "external_id": "test_beauty_01",
        "name": "수분 진정 크림",
        "url": "https://coupang.com/vp/products/beauty01",
        "category": "뷰티",
        "price": 18000
    })
    
    # Test TIMED_COMMENT strategy
    timed_comments = comm_svc.generate_comments(
        product_id=prod.id,
        strategy="TIMED_COMMENT",
        affiliate_platform="COUPANG"
    )
    assert len(timed_comments) >= 1
    assert timed_comments[0].delay_seconds == 120
    assert "쿠팡 파트너스" in timed_comments[0].body
    
    # Test BIO_LINK strategy
    bio_comments = comm_svc.generate_comments(
        product_id=prod.id,
        strategy="BIO_LINK",
        affiliate_platform="OLIVE_YOUNG"
    )
    assert len(bio_comments) >= 1
    assert "프로필 링크" in bio_comments[0].body or "바이오" in bio_comments[0].body
    assert bio_comments[0].link_type == "BIO_BRIDGE"
    
    # Test ORGANIC warmup strategy (no links, no FTC)
    org_comments = comm_svc.generate_comments(
        product_id=prod.id,
        strategy="ORGANIC"
    )
    assert len(org_comments) == 0

