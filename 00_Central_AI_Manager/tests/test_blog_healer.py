# -*- coding: utf-8 -*-
"""
Tests for Universal Blog Audit and Self-Healing Engine (BlogHealer)
and Telegram Control Center integration.
"""
import os
import sys
import pytest
from PIL import Image

# Ensure paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.audit.blog_healer import (
    blog_healer,
    WORDPRESS_SITES,
    THREADS_ACCOUNTS,
    WordPressSiteConfig,
    ThreadsAccountConfig
)
from router.intent_router import intent_router


def test_wordpress_sites_inventory():
    """Verify all 8 WordPress blogs have full configuration."""
    assert len(WORDPRESS_SITES) == 8, f"Expected 8 sites, got {len(WORDPRESS_SITES)}"
    names = [s.name for s in WORDPRESS_SITES]
    assert "TravelPick24" in names
    assert "TrendSpot24" in names
    assert "ItemPick24" in names
    assert "EnterPick24" in names
    assert "WelfarePick23" in names
    assert "WelfarePick24" in names
    assert "WelfarePick25" in names
    assert "NewsPick24" in names

    for s in WORDPRESS_SITES:
        assert s.url.startswith("https://")
        assert len(s.app_pwd) >= 16
        assert len(s.category) > 0
        assert len(s.theme_color) == 3
        assert s.auth_header.startswith("Basic ")


def test_threads_accounts_inventory():
    """Verify all 7 Threads accounts are properly configured."""
    assert len(THREADS_ACCOUNTS) == 7, f"Expected 7 accounts, got {len(THREADS_ACCOUNTS)}"
    handles = [a.username for a in THREADS_ACCOUNTS]
    assert "kth.101rep" in handles
    assert "toontoooon" in handles
    assert "lookatmeai" in handles
    assert "taechi.tube" in handles
    assert "101rep80" in handles
    assert "yr170425" in handles
    assert "ktaehoon80" in handles

    for a in THREADS_ACCOUNTS:
        assert a.profile_url.startswith("https://www.threads.net/@")
        assert "item.travelpick24.com/pick/?user=" in a.bridge_url


def test_normalize_title():
    """Verify title normalization for deduplication."""
    t1 = "[추천] 여수 2박 3일 여행 코스 총정리!"
    t2 = "여수 2박 3일 여행 코스 총정리"
    assert blog_healer._normalize_title(t1) == blog_healer._normalize_title(t2)

    t3 = "신청 안 하면 매달 20만 원 손해! 청년 월세 특별지원 (최대 240만원)"
    t4 = "신청 안 하면 매달 20만 원 손해! 청년 월세 특별지원"
    # Core title should match or be closely related
    assert "청년 월세 특별지원" in blog_healer._normalize_title(t3)


def test_thumbnail_generation():
    """Verify 16:9 aspect ratio and dimensions (1200x675)."""
    site = WORDPRESS_SITES[0]
    out_file = blog_healer.generate_16_9_thumbnail(
        title="테스트 16:9 맞춤형 썸네일 검증용 제목",
        category=site.category,
        site_name=site.name,
        theme_color=site.theme_color,
        output_filename="test_thumb_16_9.png"
    )

    assert os.path.exists(out_file)
    with Image.open(out_file) as im:
        assert im.size == (1200, 675), f"Expected 1200x675, got {im.size}"
        assert im.format == "PNG"
    
    # Clean up test artifact
    try:
        os.remove(out_file)
    except Exception:
        pass


def test_synthesize_quality_content():
    """Verify E-E-A-T and Universal Quality Engine structure in synthesized content."""
    site = WORDPRESS_SITES[0]
    html_content = blog_healer.synthesize_quality_content(
        site=site,
        title="2026 청년 정책 총정리",
        existing_content="짧은 글"
    )

    assert "quality-engine-article" in html_content
    assert "핵심 요약 & 팩트 체크" in html_content
    assert "심층 분석 및 실전 가이드" in html_content
    assert "실사용자 취재 인터뷰" in html_content
    assert "자주 묻는 질문 (FAQ)" in html_content
    assert "최종 결론 및 권장 가이드" in html_content
    # Cross-links enabled (AdSense subdomain isolation lifted)
    assert "item.travelpick24.com" in html_content
    assert "trendspot24.com" in html_content


def test_telegram_formatters():
    """Verify Telegram message formatting for /sites and /threads_all."""
    sites_msg = blog_healer.format_sites_telegram_message()
    assert "TravelPick24" in sites_msg
    assert "TrendSpot24" in sites_msg
    assert "ItemPick24" in sites_msg
    assert "NewsPick24" in sites_msg
    assert "8대 워드프레스 블로그" in sites_msg

    threads_msg = blog_healer.format_threads_telegram_message()
    assert "@kth.101rep" in threads_msg
    assert "@toontoooon" in threads_msg
    assert "@lookatmeai" in threads_msg
    assert "7대 Threads 계정" in threads_msg


@pytest.mark.asyncio
async def test_intent_router_commands():
    """Verify fast routing of all new commands."""
    user_id = "6290024230"

    # 1. /sites
    resp, _ = await intent_router.route_and_execute("/sites", user_id)
    assert "8대 워드프레스 블로그" in resp

    # 2. /threads_all
    resp, _ = await intent_router.route_and_execute("/threads_all", user_id)
    assert "7대 Threads 계정" in resp

    # 3. Korean alias: '전체블로그'
    resp, _ = await intent_router.route_and_execute("전체블로그", user_id)
    assert "8대 워드프레스 블로그" in resp

    # 4. Korean alias: '전체스레드'
    resp, _ = await intent_router.route_and_execute("전체스레드", user_id)
    assert "7대 Threads 계정" in resp
