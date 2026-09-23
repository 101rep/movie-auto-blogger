import pytest
from fastapi.testclient import TestClient
from app.main import app
from database.connection import SessionLocal
from database.models import PickItem, PickLead

client = TestClient(app)

def test_pick_public_views():
    # Test with @ prefix
    res1 = client.get("/pick/@kth.101rep")
    assert res1.status_code == 200
    assert "PICK" in res1.text
    assert "벨킨" in res1.text or "kth.101rep" in res1.text

    # Test without @ prefix
    res2 = client.get("/pick/101rep80")
    assert res2.status_code == 200
    assert "101rep80" in res2.text

    # Test beauty account
    res3 = client.get("/pick/@lookatmeai")
    assert res3.status_code == 200
    assert "독도" in res3.text or "lookatmeai" in res3.text

def test_pick_click_tracking():
    db = SessionLocal()
    item = db.query(PickItem).first()
    assert item is not None
    initial_clicks = item.clicks_count or 0
    item_id = item.id
    db.close()

    res = client.get(f"/pick/click/{item_id}", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] is not None

    db = SessionLocal()
    updated_item = db.query(PickItem).filter(PickItem.id == item_id).first()
    assert updated_item.clicks_count == initial_clicks + 1
    db.close()

def test_pick_lead_submission():
    payload = {
        "account_id": 1,
        "contact_type": "KAKAO",
        "contact_value": "test_buyer_id",
        "memo": "맥북 특가 알림"
    }
    res = client.post("/pick/lead", data=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"

    db = SessionLocal()
    lead = db.query(PickLead).filter(PickLead.contact_value == "test_buyer_id").first()
    assert lead is not None
    # Cleanup test lead
    db.delete(lead)
    db.commit()
    db.close()

def test_pick_manage_view():
    res = client.get("/pick-manage")
    assert res.status_code == 200
    assert "자체 제작 '픽(PICK)' 큐레이션 관리 센터" in res.text
    assert "kth.101rep" in res.text
    assert "5대 커머스" in res.text

def test_toss_sharelink_integration():
    # Verify Toss filter and Toss item badge on public pick page
    res = client.get("/pick/@kth.101rep")
    assert res.status_code == 200
    assert "토스 (10%)" in res.text
    assert "TOSS" in res.text

    # Verify Toss click redirect
    db = SessionLocal()
    toss_item = db.query(PickItem).filter(PickItem.affiliate_platform == "TOSS").first()
    assert toss_item is not None
    assert "toss.im" in toss_item.affiliate_url
    assert toss_item.item_code is not None
    toss_id = toss_item.id
    db.close()

    res_click = client.get(f"/pick/click/{toss_id}", follow_redirects=False)
    assert res_click.status_code == 302
    assert "toss.im" in res_click.headers["location"]
