import pytest
from sqlalchemy import select
from integrations.instagram.mock_provider import MockInstagramProvider
from integrations.instagram.meta_instagram_provider import MetaInstagramProvider
from integrations.instagram.exceptions import InstagramAuthError
from services.instagram_service import InstagramService
from services.cardnews_service import CardnewsService
from services.content_repurpose_service import ContentRepurposeService
from services.ag_gateway import (
    AGGateway,
    ResearchAgent,
    ContentStrategyAgent,
    WriterAgent,
    CardnewsAgent,
    ProductAgent,
    ReviewAgent,
    AnalyticsAgent
)
from apps.backend.tre.models import Account, Persona, InstagramAccount, InstagramPost, InstagramAnalytics, AIUsageLog, ContentItem, Post
from apps.backend.tre.config import settings
from apps.backend.tre.telegram import command

def test_instagram_mock_publish():
    provider = MockInstagramProvider()
    assert provider.validate_token() is True

    # 1. Single Image
    res_img = provider.publish_image("https://example.com/slide1.jpg", "Test single image caption")
    assert res_img.status == "SUCCESS"
    assert res_img.media_id.startswith("mock_ig_img_")
    assert "instagram.com" in res_img.permalink

    # 2. Carousel
    res_car = provider.publish_carousel(["https://example.com/s1.jpg", "https://example.com/s2.jpg"], "Test carousel")
    assert res_car.status == "SUCCESS"
    assert res_car.media_id.startswith("mock_ig_car_")
    assert res_car.media_type == "CAROUSEL"

    # 3. Insights
    insights = provider.get_insights(res_car.media_id)
    assert insights.reach > 0
    assert insights.likes >= 0
    assert insights.saves >= 0

def test_instagram_live_fail_closed():
    # Unconfigured provider must fail closed
    live = MetaInstagramProvider()
    with pytest.raises(InstagramAuthError):
        live.publish_image("https://example.com/test.jpg", "Live attempt")

def test_carousel_cardnews_creation():
    svc = CardnewsService(default_template="minimal")
    source_title = "가족 여행 짐 싸기 꿀팁"
    source_text = "출발 전 짐의 크기와 이동 동선을 미리 파악하면 누락과 불필요한 무게를 줄일 수 있습니다. 파우치를 카테고리별로 분리하고 필수 상비약을 챙기세요."

    cardnews = svc.generate_cardnews(
        title=source_title,
        source_text=source_text,
        category="여행",
        content_type="CHECKLIST"
    )

    assert cardnews.title == source_title
    assert cardnews.template == "minimal"
    assert len(cardnews.slides) >= 3

    # Check Slide Structure
    for slide in cardnews.slides:
        assert slide.page >= 1
        assert len(slide.headline) > 0
        assert len(slide.body) > 0
        assert len(slide.image_prompt) > 0
        assert "Instagram" in slide.image_prompt or "illustration" in slide.image_prompt or "graphic" in slide.image_prompt or "aesthetic" in slide.image_prompt

    assert "#여행" in cardnews.hashtags[0]
    assert len(cardnews.caption) > 20

def test_content_repurpose_engine():
    svc = ContentRepurposeService()
    repurposed = svc.repurpose(
        title="봄맞이 거실 인테리어 정리법",
        source_text="수납 공간과 동선을 단순화하면 집이 훨씬 넓어 보입니다. 불필요한 물건을 비우고 모듈 가구를 활용해 보세요.",
        category="생활"
    )

    # 1. Threads Output
    t = repurposed.threads_post
    assert t["platform"] == "threads"
    assert "거실 인테리어" in t["body"]
    assert len(t["replies"]) >= 1

    # 2. Instagram Carousel Output
    ig = repurposed.instagram_carousel
    assert "slides" in ig
    assert len(ig["slides"]) >= 3
    assert ig["slides"][0]["page"] == 1

    # 3. Blog Output
    b = repurposed.blog_post
    assert b["platform"] == "blog"
    assert "# 봄맞이 거실 인테리어" in b["markdown"]
    assert "자주 묻는 질문 (FAQ)" in b["markdown"]

def test_ag_gateway_routing_and_persona_strategy(env):
    client, factory = env
    gw = AGGateway(mode="mock")

    with factory() as db:
        travel_acc = db.scalar(select(Account).where(Account.username.in_(["ktaehoon80", "travel"])))
        persona = db.scalar(select(Persona).where(Persona.account_id == travel_acc.id))

        # Travel: Research -> Gemini, Writing -> Claude
        resp_research = gw.route_and_generate("research", "제주도 가족 여행 코스", account_id=travel_acc.id, persona=persona, db=db)
        assert resp_research.provider == "gemini"
        assert resp_research.model == "gemini-2.5-flash"
        assert resp_research.prompt_tokens > 0
        assert resp_research.cost_usd >= 0.0

        resp_writing = gw.route_and_generate("writing", "스레드 본문 작성", account_id=travel_acc.id, persona=persona, db=db)
        assert resp_writing.provider == "claude"
        assert resp_writing.model == "claude-3-5-sonnet"

        # Check AI Usage Log in DB
        logs = list(db.scalars(select(AIUsageLog).where(AIUsageLog.account_id == travel_acc.id)))
        assert len(logs) == 2

def test_ag_gateway_fallback_routing():
    gw = AGGateway(mode="mock")
    # Simulate primary failure -> automatic fallback
    resp = gw.route_and_generate(
        task_type="writing",
        prompt="글 작성 테스트",
        force_provider="claude",
        simulate_failure_on_primary=True
    )
    assert resp.fallback_used is True
    assert resp.provider in ["gemini", "gpt", "mock"]
    assert len(resp.content) > 0

def test_brand_account_mapping_7_accounts(env):
    client, factory = env
    # Verify via API
    res = client.get("/api/instagram/accounts")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7

    for item in data:
        assert "brand_name" in item
        assert "category" in item
        ig = item["instagram"]
        assert ig["status"] == "ONLINE"
        assert ig["instagram_id"].startswith("ig_")
        assert ig["threads_ratio"] == 0.5
        assert ig["instagram_ratio"] == 0.3
        assert ig["blog_ratio"] == 0.2

def test_instagram_posts_crud_and_publish_api(env):
    client, factory = env
    # 1. Create Instagram Post
    post_payload = {
        "account_id": 1,
        "media_type": "CAROUSEL",
        "title": "주말 가족 여행 추천지 5선",
        "caption": "주말에 가기 좋은 여행지를 카드뉴스로 정리했습니다. #여행",
        "carousel_data": {"title": "주말 가족 여행", "slides": [{"page": 1, "headline": "커버", "body": "본문", "image_prompt": "prompt"}]},
        "media_urls": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
    }
    create_res = client.post("/api/instagram/posts", json=post_payload)
    assert create_res.status_code == 200
    post_id = create_res.json()["id"]

    # 2. Publish
    pub_res = client.post(f"/api/instagram/posts/{post_id}/publish")
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "PUBLISHED"
    remote_id = pub_res.json()["remote_id"]
    assert remote_id.startswith("mock_ig_")

    # 3. Insights
    insights_res = client.get(f"/api/instagram/posts/{post_id}/insights")
    assert insights_res.status_code == 200
    idata = insights_res.json()
    assert idata["reach"] > 0
    assert idata["likes"] >= 0

def test_ai_usage_tracking_api(env):
    client, factory = env
    # Trigger an AI generate call
    gen_res = client.post("/api/ai/generate", json={
        "task_type": "writing",
        "prompt": "봄철 옷장 정리 노하우",
        "account_id": 2
    })
    assert gen_res.status_code == 200
    assert len(gen_res.json()["content"]) > 0

    # Query usage summary
    usage_res = client.get("/api/ai/usage")
    assert usage_res.status_code == 200
    u = usage_res.json()
    assert u["today_calls"] >= 1
    assert u["today_cost_usd"] >= 0.0
    assert "usage_by_model" in u
    assert "cost_by_account" in u

def test_telegram_v3_commands(env):
    client, factory = env
    with factory() as db:
        chat_id = settings().telegram_allowed_chat_id

        # /instagram
        res_ig = command(db, chat_id, "/instagram")
        assert isinstance(res_ig, list)
        assert len(res_ig) == 7

        # /cardnews
        res_cn = command(db, chat_id, "/cardnews")
        assert "생성완료" in res_cn
        assert "게시완료" in res_cn

        # /ai_cost
        res_cost = command(db, chat_id, "/ai_cost")
        assert "today_cost_usd" in res_cost

        # /content_today
        res_today = command(db, chat_id, "/content_today")
        assert "threads_count" in res_today
        assert "instagram_count" in res_today

def test_full_v3_content_commerce_os_flow(env):
    """
    Requirement 14 Complete Flow Verification:
    소재 수집 -> AG Gateway 분석 -> 7개 계정 중 선택 -> Threads 글 생성 ->
    Instagram 카드뉴스 생성 -> 상품 매칭 -> 검수 -> 예약 -> Threads 게시 ->
    Instagram 게시 -> Analytics 수집 -> Telegram 보고
    """
    client, factory = env

    # 1. 소재 수집
    source_res = client.get("/api/sources")
    assert source_res.status_code == 200
    source_id = source_res.json()[0]["id"]

    new_content = client.post("/api/content", json={
        "source_id": source_id,
        "source_title": "캠핑 필수 준비물 체크리스트 2026",
        "source_text": "첫 캠핑에서 가장 중요한 것은 보온과 수납입니다. 조리도구는 올인원 세트로 줄이고 대용량 텀블러를 준비하세요.",
        "category": "여행"
    })
    assert new_content.status_code == 200
    content_id = new_content.json()["id"]

    # 2. AG Gateway 분석
    analyze_res = client.post(f"/api/content/{content_id}/analyze")
    assert analyze_res.status_code == 200

    # 3. 7개 계정 중 최적 브랜드 계정 선택 (Travel)
    accounts = client.get("/api/accounts").json()
    strategy_agent = ContentStrategyAgent()
    chosen_account = strategy_agent.select_best_account(accounts, category="여행")
    account_id = chosen_account["id"]

    # 4. 상품 매칭 및 0-100점 스코어링
    product_res = client.post("/api/products/select-best", json={
        "keyword": "캠핑 보온 텀블러",
        "account_id": account_id
    })
    assert product_res.status_code == 200
    product_id = product_res.json()["product_id"]

    # 5. Threads 글 생성
    threads_gen = client.post(f"/api/content/{content_id}/generate", json={
        "account_id": account_id,
        "goal": "INFORMATION"
    })
    assert threads_gen.status_code == 200
    post_id = threads_gen.json()["id"]

    # 6. Instagram 카드뉴스 생성
    cardnews_res = client.post(f"/api/content/{content_id}/cardnews", json={
        "title": "캠핑 필수 준비물 체크리스트",
        "template": "minimal",
        "content_type": "CHECKLIST"
    })
    assert cardnews_res.status_code == 200
    cardnews_data = cardnews_res.json()
    assert len(cardnews_data["slides"]) >= 3

    # 7. 검수 및 승인
    val_res = client.post(f"/api/posts/{post_id}/validate")
    assert val_res.status_code == 200
    assert val_res.json()["result"] == "PASS"

    appr_res = client.post(f"/api/posts/{post_id}/approve")
    assert appr_res.status_code == 200

    # 8. Threads 예약 및 워커 1회 게시
    from apps.worker.engine import run_once
    sched_res = client.post(f"/api/posts/{post_id}/schedule", json={})
    assert sched_res.status_code == 200
    assert run_once(factory) == 1

    updated_post = client.get(f"/api/posts").json()
    our_post = next(p for p in updated_post if p["id"] == post_id)
    assert our_post["status"] == "SUCCESS"
    assert our_post["remote_id"].startswith("mock_")

    # 9. Instagram 게시
    ig_post = client.post("/api/instagram/posts", json={
        "account_id": account_id,
        "content_id": content_id,
        "media_type": "CAROUSEL",
        "title": cardnews_data["title"],
        "caption": cardnews_data["caption"],
        "carousel_data": cardnews_data,
        "media_urls": ["https://example.com/s1.jpg", "https://example.com/s2.jpg"]
    })
    assert ig_post.status_code == 200
    ig_post_id = ig_post.json()["id"]

    ig_pub = client.post(f"/api/instagram/posts/{ig_post_id}/publish")
    assert ig_pub.status_code == 200
    assert ig_pub.json()["status"] == "PUBLISHED"

    # 10. Analytics 수집
    ig_insights = client.get(f"/api/instagram/posts/{ig_post_id}/insights")
    assert ig_insights.status_code == 200
    assert ig_insights.json()["reach"] > 0

    analytics_res = client.get("/api/analytics")
    assert analytics_res.status_code == 200

    # 11. Telegram 보고
    with factory() as db:
        chat_id = settings().telegram_allowed_chat_id
        report = command(db, chat_id, "/content_today")
        assert report["threads_count"] >= 1
        assert report["instagram_count"] >= 1
