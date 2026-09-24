# -*- coding: utf-8 -*-
"""Test suite for repair_blog_post_content tool."""
import pytest
from router.gemini_tools import GEMINI_FUNCTION_DECLARATIONS, execute_tool_call
from security.permission import permission_engine, PermissionLevel

def test_tool_declaration():
    tool_names = [t["name"] for t in GEMINI_FUNCTION_DECLARATIONS]
    assert "repair_blog_post_content" in tool_names
    decl = next(t for t in GEMINI_FUNCTION_DECLARATIONS if t["name"] == "repair_blog_post_content")
    assert "site_id" in decl["parameters"]["properties"]
    assert "post_id" in decl["parameters"]["properties"]
    assert "movie_title" in decl["parameters"]["properties"]

def test_permission_level():
    level = permission_engine.evaluate_action_level("repair_blog_post_content", {"site_id": 2, "post_id": 137})
    assert level == PermissionLevel.LEVEL_2_SOFT_CONTROL
    allowed, _, _ = permission_engine.check_execution_permission("6290024230", "repair_blog_post_content", {"site_id": 2, "post_id": 137})
    assert allowed is True

def test_unauthorized_user():
    allowed, reason, _ = permission_engine.check_execution_permission("9999999999", "repair_blog_post_content", {"site_id": 2, "post_id": 137})
    assert allowed is False
    assert "인가되지 않은 사용자" in reason

def test_render_netflix_dark_magazine_html():
    from adapters.blog_post_manager import render_netflix_dark_magazine_html, validate_and_close_html
    import re
    data = {
        "hook_quote": "테스트 명대사 카피",
        "intro": "테스트 인트로 문단입니다.",
        "synopsis_p1": "줄거리 1문단입니다.",
        "synopsis_p2": "줄거리 2문단입니다.",
        "synopsis_p3": "줄거리 3문단입니다.",
        "director_analysis": "감독 연출 스타일 분석입니다.",
        "cast_analysis": "배우 연기 분석입니다.",
        "viewing_points": [{"title": "포인트1", "desc": "설명1"}],
        "recommended_for": ["추천대상1"],
        "not_recommended_for": ["비추천1"],
        "closing_verdict": "총평 문단입니다."
    }
    meta = {
        "title": "하트 오브 비스트",
        "original_title": "Heart of the Beast",
        "director": "데이비드 에이어",
        "cast": ["브래드 피트"],
        "genres": ["액션", "드라마"],
        "release_date": "2026-09-19",
        "runtime": 102,
        "vote_average": 7.9
    }
    html = render_netflix_dark_magazine_html(data, meta, "https://image.tmdb.org/t/p/w780/test.jpg")
    assert "mab-article-container" in html
    assert "하트 오브 비스트" in html
    assert "데이비드 에이어" in html
    assert "브래드 피트" in html
    
    # 태그 정합성 검증
    div_open = len(re.findall(r"<div\b", html))
    div_close = len(re.findall(r"</div>", html))
    assert div_open == div_close
    
    sec_open = len(re.findall(r"<section\b", html))
    sec_close = len(re.findall(r"</section>", html))
    assert sec_open == sec_close

def test_validate_and_close_html():
    from adapters.blog_post_manager import validate_and_close_html
    broken_html = "<div><p>내용이 중간에 끊어짐"
    fixed_html = validate_and_close_html(broken_html)
    assert fixed_html.endswith("</p></div>") or "</p>" in fixed_html and "</div>" in fixed_html

@pytest.mark.asyncio
async def test_fetch_movie_full_metadata():
    from adapters.blog_post_manager import fetch_movie_full_metadata
    meta = await fetch_movie_full_metadata("하트 오브 더 비스트")
    assert meta["title"] in ["하트 오브 비스트", "하트 오브 더 비스트", "Heart of the Beast"]
    assert "데이비드 에이어" in meta["director"] or meta["director"] != "미상"
    assert len(meta["cast"]) > 0
    assert meta["poster_url"] is not None

