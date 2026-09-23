# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient
from app.main import app
from database.connection import SessionLocal
from database.models import Content, Product, Account
from services.wordpress_service import WordPressService

client = TestClient(app)

def test_wordpress_status_endpoint():
    resp = client.get("/api/wordpress/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "enabled" in data
    assert "site_url" in data
    assert data["site_url"] == "https://trendspot24.com"
    assert data["connection"]["status"] == "SUCCESS"
    assert data["connection"]["connected"] is True

def test_wordpress_service_health():
    wp = WordPressService()
    res = wp.test_connection()
    assert res["status"] == "SUCCESS"
    assert res["connected"] is True
    assert res["user_name"] == "트렌드스팟24"

def test_eeat_article_generation():
    db = SessionLocal()
    try:
        content = db.query(Content).first()
        if not content:
            pytest.skip("No content found in test DB")

        wp = WordPressService()
        article = wp.generate_eeat_blog_post(content)
        assert "title" in article
        assert "html" in article
        assert "excerpt" in article
        assert len(article["title"]) > 5
        assert "<div" in article["html"] or "<p" in article["html"]
        # Verify Anti-Cliche: no robotic fillers
        assert "알아보겠습니다" not in article["title"]
        assert "살펴보겠습니다" not in article["title"]
    finally:
        db.close()