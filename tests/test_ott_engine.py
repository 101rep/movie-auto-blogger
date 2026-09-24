# -*- coding: utf-8 -*-
"""
Tests for EnterPick24 OTT Automation Engine.
Validates TVmazeClient, FanartClient, DarkMagazineRenderer, and OTTWriter.
"""

import pytest
from core.ott_engine.tvmaze_client import TVmazeClient
from core.ott_engine.fanart_client import FanartClient
from core.ott_engine.template_renderer import DarkMagazineRenderer
from core.ott_engine.ott_writer import OTTWriter


def test_01_tvmaze_search():
    client = TVmazeClient()
    show = client.search_show("Stranger Things")
    assert show is not None
    assert show["name"] == "Stranger Things"
    assert show["tvdb_id"] is not None
    assert show["rating"] > 7.0
    assert len(show["genres"]) > 0
    assert len(show["cast"]) > 0


def test_02_fanart_assets():
    fanart = FanartClient()
    # Stranger Things TVDB ID is 305288
    assets_raw = fanart.get_tv_assets(305288)
    assert assets_raw is not None
    selected = fanart.select_best_assets(assets_raw)
    assert selected["backdrop"] is not None
    assert selected["hd_logo"] is not None


def test_03_template_rendering():
    dummy_show = {
        "name": "Test OTT Series",
        "platform": "Netflix",
        "rating": 9.2,
        "runtime": 55,
        "genres": ["스릴러", "SF"],
        "total_episodes": 8,
        "summary": "테스트 요약 내용입니다.",
        "image_original": "https://example.com/poster.jpg",
        "next_episode": None,
        "episodes": [
            {"season": 1, "number": 1, "name": "시작", "rating": 9.0}
        ],
        "cast": [
            {"person_name": "배우A", "character_name": "주인공", "person_image": None}
        ]
    }
    dummy_visuals = {
        "backdrop": "https://example.com/backdrop.jpg",
        "hd_logo": "https://example.com/logo.png",
        "clearart": None,
    }
    dummy_article = {
        "hook_lead": "압도적인 스릴을 선사하는 넷플릭스 신작.",
        "title_symbolism": "<p>상징성 분석 내용</p>",
        "synopsis_section": "<p>줄거리 내용</p>",
        "faqs": [{"q": "Q. 질문인가요?", "a": "A. 답변입니다."}],
        "verdict": "필람작입니다."
    }

    html = DarkMagazineRenderer.render_article(
        show_data=dummy_show,
        visual_assets=dummy_visuals,
        article_content=dummy_article,
        post_title="넷플릭스 화제작 'Test OTT Series' 완벽 분석"
    )

    assert "mab-article-container" in html
    assert "Pretendard" in html
    assert "NETFLIX" in html
    assert "Test OTT Series" in html
    assert "https://example.com/logo.png" in html
    assert "한국 넷플릭스 미공개작 안전 시청 가이드" in html  # Commercial box
    assert "https://schema.org" in html  # Structured data


def test_04_ott_writer_pipeline():
    writer = OTTWriter()
    result = writer.generate_article_for_show("Stranger Things")
    assert result is not None
    assert "Stranger Things" in result["title"]
    assert len(result["content"]) > 3000
    assert result["featured_image_url"] is not None
    assert result["quality_gate"]["passed"] is True
