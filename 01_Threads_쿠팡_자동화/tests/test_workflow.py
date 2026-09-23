import pytest
from agents import MasterAgent

def test_scenario_1_product_search_and_save(client):
    """TEST 1: 상품 검색 -> 상품 저장 -> 상세 페이지"""
    # 1. Search external
    res = client.get("/api/products/search?query=스탠리")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0

    # 2. Save
    target = items[0]
    save_res = client.post("/api/products/save", json={
        "external_id": target["external_id"],
        "name": target["name"],
        "url": target["url"],
        "image_url": target["image_url"],
        "category": target["category"],
        "price": target["price"],
        "rating": target["rating"],
        "review_count": target["review_count"],
        "shipping_type": target["shipping_type"]
    })
    assert save_res.status_code == 200
    prod_id = save_res.json()["product_id"]

    # 3. Detail page view
    detail_res = client.get(f"/products/{prod_id}")
    assert detail_res.status_code == 200
    assert target["name"] in detail_res.text

def test_scenario_2_product_scoring(client):
    """TEST 2: 상품 -> 점수 생성 -> DB 저장"""
    # Create product
    save_res = client.post("/api/products/save", json={
        "external_id": "SCENARIO-02",
        "name": "시나리오 2번 상품",
        "url": "https://coupang.com/s2",
        "category": "디지털",
        "price": 89000,
        "rating": 4.8,
        "review_count": 800
    })
    prod_id = save_res.json()["product_id"]

    # Score
    score_res = client.post(f"/api/workflow/score/{prod_id}")
    assert score_res.status_code == 200
    data = score_res.json()
    assert data["status"] == "SUCCESS"
    assert data["score"]["total_score"] > 0
    assert data["score"]["reason"] != ""

def test_scenario_3_product_dna(client):
    """TEST 3: 상품 -> DNA 생성 -> DB 저장"""
    save_res = client.post("/api/products/save", json={
        "external_id": "SCENARIO-03",
        "name": "시나리오 3번 상품",
        "url": "https://coupang.com/s3",
        "category": "뷰티",
        "price": 25000,
        "rating": 4.9,
        "review_count": 3500
    })
    prod_id = save_res.json()["product_id"]

    dna_res = client.post(f"/api/workflow/dna/{prod_id}")
    assert dna_res.status_code == 200
    data = dna_res.json()
    assert data["status"] == "SUCCESS"
    assert data["dna"]["target_person"] != ""
    assert data["dna"]["ai_summary"] != ""

def test_scenario_4_idea_generation(client):
    """TEST 4: 상품 -> 아이디어 10개 생성"""
    save_res = client.post("/api/products/save", json={
        "external_id": "SCENARIO-04",
        "name": "시나리오 4번 상품",
        "url": "https://coupang.com/s4",
        "category": "생활",
        "price": 19000
    })
    prod_id = save_res.json()["product_id"]

    idea_res = client.post(f"/api/workflow/ideas/{prod_id}")
    assert idea_res.status_code == 200
    data = idea_res.json()
    assert data["count"] == 10
    assert len(data["ideas"]) == 10

def test_scenario_5_threads_writer(client):
    """TEST 5: 아이디어 -> Threads 본문 생성"""
    save_res = client.post("/api/products/save", json={
        "external_id": "SCENARIO-05",
        "name": "시나리오 5번 상품",
        "url": "https://coupang.com/s5",
        "category": "주방",
        "price": 30000
    })
    prod_id = save_res.json()["product_id"]

    ideas_res = client.post(f"/api/workflow/ideas/{prod_id}")
    idea_id = ideas_res.json()["ideas"][0]["id"]

    write_res = client.post("/api/workflow/threads/write", json={
        "product_id": prod_id,
        "idea_id": idea_id,
        "rewrite_mode": "natural"
    })
    assert write_res.status_code == 200
    data = write_res.json()
    assert data["status"] == "SUCCESS"
    assert len(data["body"]) > 20

def test_scenario_6_comment_generation(client):
    """TEST 6: 본문 -> 댓글 생성"""
    save_res = client.post("/api/products/save", json={
        "external_id": "SCENARIO-06",
        "name": "시나리오 6번 상품",
        "url": "https://coupang.com/s6",
        "category": "뷰티",
        "price": 15000
    })
    prod_id = save_res.json()["product_id"]

    comm_res = client.post("/api/workflow/comments/generate", json={
        "product_id": prod_id,
        "partner_link": "https://link.coupang.com/a/testlink"
    })
    assert comm_res.status_code == 200
    comments = comm_res.json()["comments"]
    assert len(comments) >= 1
    assert "https://link.coupang.com/a/testlink" in comments[0]["body"]

def test_scenario_7_full_workflow_e2e(db_session):
    """TEST 7: 전체 workflow (상품 -> 평가 -> DNA -> 아이디어 -> 본문 -> 댓글 -> APPROVED)"""
    master = MasterAgent(db_session)
    result = master.execute_full_pipeline(
        product_data={
            "external_id": "E2E-MASTER-01",
            "name": "브리타 마레라 메모 정수기 2.4L",
            "url": "https://coupang.com/vp/products/brita",
            "image_url": "https://example.com/brita.jpg",
            "category": "주방용품",
            "price": 34900,
            "rating": 4.9,
            "review_count": 21000,
            "shipping_type": "로켓배송",
            "description": "생수병 분리수거 탈출 꿀템"
        },
        selected_angle_index=0,
        partner_link="https://link.coupang.com/a/brita"
    )

    assert result["product"].id is not None
    assert result["score"].total_score >= 80
    assert result["dna"].ai_summary != ""
    assert len(result["ideas"]) == 10
    assert result["selected_idea"] is not None
    assert result["threads_post"].body != ""
    assert len(result["comments"]) >= 1
    assert result["content"].status == "DRAFT"