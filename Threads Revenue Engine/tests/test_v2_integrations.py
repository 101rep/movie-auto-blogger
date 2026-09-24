import pytest
from integrations.threads.mock_provider import MockThreadsProvider
from integrations.threads.meta_threads_provider import MetaThreadsProvider
from integrations.threads.exceptions import ThreadsAuthError, ThreadsPublishError
from integrations.affiliate.mock_provider import MockAffiliateProvider
from integrations.affiliate.coupang_provider import CoupangProvider
from integrations.affiliate.exceptions import AffiliateAuthError, DeeplinkError
from integrations.affiliate.schemas import ProductItem
from services.publisher_service import PublisherService
from services.product_service import ProductService
from services.contracts import LiveThreadsProvider, CoupangProvider as ContractsCoupangProvider, ProviderError
from apps.backend.tre.telegram import command

def test_threads_provider_mock():
    provider = MockThreadsProvider()
    assert provider.validate_token() is True

    pub = provider.publish_post(text="Hello Threads V2 Mock", media_urls=["https://example.com/img.jpg"])
    assert pub.post_id.startswith("mock_")
    assert pub.status == "SUCCESS"

    reply = provider.publish_reply(parent_id=pub.post_id, text="Reply content")
    assert reply.post_id.startswith("mock_")
    assert reply.status == "SUCCESS"

    status = provider.get_post_status(pub.post_id)
    assert status.status == "SUCCESS"

    insights = provider.get_insights(pub.post_id)
    assert insights.views >= 0
    assert insights.likes >= 0

def test_threads_provider_fail_closed():
    # Unconfigured provider fails closed
    live = LiveThreadsProvider()
    with pytest.raises(ProviderError):
        live.publish_text("dummy", "text")

def test_affiliate_provider_mock():
    provider = MockAffiliateProvider()
    results = provider.search_products(keyword="텀블러", limit=5)
    assert len(results) > 0
    p0 = results[0]
    assert "텀블러" in p0.name or "보온" in p0.name
    assert p0.price > 0
    assert p0.affiliate_url != ""

    deeplink = provider.create_deeplink("https://www.coupang.com/vp/products/12345")
    assert "link.coupang.com" in deeplink or "mock_affiliate" in deeplink

    report = provider.get_report("20260901", "20260923")
    assert report.orders >= 0

def test_affiliate_provider_fail_closed():
    live = ContractsCoupangProvider()
    with pytest.raises(ProviderError):
        live.generate_link("https://www.coupang.com/vp/products/123")

def test_product_scoring_engine():
    svc = ProductService(mode="mock")

    # Ideal price (15k - 50k), high rating, high reviews, rocket delivery
    ideal_prod = ProductItem(
        product_id="1001",
        name="스테인리스 대용량 보온 보냉 텀블러 900ml",
        price=28000,
        original_url="https://www.coupang.com/vp/products/1001",
        affiliate_url="https://link.coupang.com/a/1001",
        rating=4.9,
        review_count=1200,
        shipping_type="로켓배송",
        category="주방용품",
        image_url="https://example.com/img1.jpg"
    )

    score = svc.calculate_product_score(ideal_prod, account_category="주방용품")
    assert score >= 80.0, f"Expected high score >= 80, got {score}"

    # Cooldown penalty: product in recent_product_ids must get 0 score
    cooldown_score = svc.calculate_product_score(
        ideal_prod,
        account_category="주방용품",
        recent_product_ids=["1001"]
    )
    assert cooldown_score == 0.0, f"Expected 0.0 due to cooldown, got {cooldown_score}"

def test_affiliate_compliance_validation():
    svc = ProductService(mode="mock")

    valid_text = "이 텀블러 진짜 얼음이 안 녹아서 추천합니다!"
    valid_replies = [
        "제품 정보: 스텐 보온 텀블러\n이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.\nhttps://link.coupang.com/a/sample"
    ]
    res_valid = svc.validate_affiliate_compliance(
        valid_text,
        valid_replies,
        "이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다."
    )
    assert res_valid["compliant"] is True
    assert len(res_valid["errors"]) == 0

    # Missing link
    no_link_replies = ["쿠팡 파트너스 활동으로 수수료를 제공받습니다."]
    res_invalid = svc.validate_affiliate_compliance(
        valid_text,
        no_link_replies,
        "이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다."
    )
    assert res_invalid["compliant"] is False
    assert "AFFILIATE_LINK_MISSING" in res_invalid["errors"]

def test_v2_api_endpoints(env):
    client, factory = env

    # 1. Product Search
    resp_search = client.get("/api/products/search?keyword=텀블러&limit=3")
    assert resp_search.status_code == 200
    search_data = resp_search.json()
    assert len(search_data) > 0
    assert "product_id" in search_data[0]

    # 2. Select Best Product
    resp_select = client.post("/api/products/select-best", json={"keyword": "텀블러", "limit": 5})
    assert resp_select.status_code == 200
    select_data = resp_select.json()
    assert "product_id" in select_data
    assert "product_item" in select_data
    assert select_data["product_item"]["score"] > 0

    # 3. Deeplink generation
    resp_deeplink = client.post("/api/products/deeplink", json={"urls": ["https://www.coupang.com/vp/products/999"]})
    assert resp_deeplink.status_code == 200
    deeplink_data = resp_deeplink.json()
    assert "links" in deeplink_data
    assert len(deeplink_data["links"]) == 1
    assert "shorten_url" in deeplink_data["links"][0]

    # 4. Threads Health
    resp_th = client.get("/api/threads/health")
    assert resp_th.status_code == 200
    th_data = resp_th.json()
    assert th_data["status"] == "MOCK"
    assert th_data["is_mock"] is True

    # 5. Products Health
    resp_ph = client.get("/api/products/health")
    assert resp_ph.status_code == 200
    ph_data = resp_ph.json()
    assert ph_data["status"] == "MOCK"
    assert ph_data["is_mock"] is True

def test_telegram_v2_commands(env):
    from apps.backend.tre.config import settings
    client, factory = env
    with factory() as db:
        chat_id = settings().telegram_allowed_chat_id
        res_schedule = command(db, chat_id, "/schedule")
        assert isinstance(res_schedule, list)

        res_errors = command(db, chat_id, "/errors")
        assert isinstance(res_errors, list)
