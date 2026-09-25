# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for EnterPick24 V4 Master Engine.
Tests ContentPlanner, Fingerprint, DuplicateEngine, PosterManager, QualityEvaluator,
Dark Editorial Styles, and Existing Post Auditor.
"""

import pytest
from movie_content_skills.content_planner import DailyContentPlanner
from movie_content_skills.fingerprint import ContentFingerprint, normalize_title, normalize_entity_name
from movie_content_skills.duplicate_engine import DuplicateEngine, DuplicateCheckResult
from movie_content_skills.poster_manager import PosterManager
from movie_content_skills.quality_evaluator import V4QualityEvaluator
from movie_content_skills.styles import ENTERPICK24_DARK_EDITORIAL_CSS
from movie_content_skills.audit_service import ExistingPostAuditor


def test_01_content_planner():
    planner = DailyContentPlanner()
    plans = planner.create_daily_plan("2026-09-25")
    assert len(plans) == 3

    intents = [p["search_intent"] for p in plans]
    assert len(set(intents)) == 3, "3 slots must have unique search intents"

    entities = [p["primary_entity"] for p in plans]
    assert len(set(entities)) == 3, "No duplicate primary entities on the same day"

    report = planner.format_plan_report(plans)
    assert "EnterPick24 오늘의 편성 계획" in report
    assert "09:00" in report
    assert "20:00" in report


def test_02_fingerprint_and_normalization():
    # Test bilingual normalization
    assert normalize_entity_name("Squid Game") == "SQUID_GAME"
    assert normalize_entity_name("오징어 게임") == "SQUID_GAME"
    assert normalize_entity_name("오징어게임") == "SQUID_GAME"

    assert normalize_entity_name("Stranger Things") == "STRANGER_THINGS"
    assert normalize_entity_name("기묘한 이야기") == "STRANGER_THINGS"

    assert normalize_entity_name("The Glory") == "THE_GLORY"
    assert normalize_entity_name("더 글로리") == "THE_GLORY"

    # Test title normalization
    t1 = normalize_title("넷플릭스 '오징어 게임' 심층 비평!")
    t2 = normalize_title("넷플릭스 오징어게임 심층비평")
    assert t1 == t2, "Title normalization must equate special characters and whitespace"

    fp = ContentFingerprint(
        content_id="test_01",
        content_type="single_review",
        title="기묘한 이야기 시즌4 심층 리뷰",
        primary_entity="Stranger Things",
        search_intent="single_title_deep_dive",
        summary="80년대 레트로 호러의 정점"
    )
    assert fp.primary_entity == "STRANGER_THINGS"
    assert fp.fingerprint is not None
    assert len(fp.fingerprint) == 16


def test_03_4level_duplicate_engine():
    engine = DuplicateEngine()

    # Base post in corpus: Stranger Things published today
    fp_base = ContentFingerprint(
        content_id="post_27",
        content_type="single_review",
        title="기묘한 이야기 심층 리뷰",
        primary_entity="Stranger Things",
        search_intent="single_title_deep_dive",
        summary="초자연적 현상과 호킨스 마을 이야기",
        published_at="2026-09-25T10:00:00"
    )
    engine.add_to_corpus(fp_base)

    # 1. Level 1 Test: Exact Title Match -> Must BLOCK
    fp_exact = ContentFingerprint(
        content_id="post_cand_1",
        content_type="single_review",
        title="기묘한이야기 심층리뷰!",
        primary_entity="Stranger Things",
        published_at="2026-09-25T11:00:00"
    )
    res_l1 = engine.evaluate(fp_exact)
    assert res_l1.is_blocked is True
    assert res_l1.level_triggered == 1
    assert res_l1.risk_level == "HIGH"
    assert res_l1.risk_score == 100.0

    # 2. Level 2 Test: Same entity single review within 30 days -> Must BLOCK
    fp_entity = ContentFingerprint(
        content_id="post_cand_2",
        content_type="single_review",
        title="넷플릭스 화제작 기묘한 이야기 관전 포인트",
        primary_entity="기묘한 이야기",
        published_at="2026-09-25T12:00:00"
    )
    res_l2 = engine.evaluate(fp_entity)
    assert res_l2.is_blocked is True
    assert res_l2.level_triggered == 2
    assert res_l2.risk_level == "HIGH"

    # 3. Completely different entity -> Must PASS
    fp_different = ContentFingerprint(
        content_id="post_cand_3",
        content_type="single_review",
        title="세브란스 단절 심층 비평",
        primary_entity="Severance",
        search_intent="single_title_deep_dive",
        summary="직장과 사생활의 기억 분리 실험",
        published_at="2026-09-25T13:00:00"
    )
    res_diff = engine.evaluate(fp_different)
    assert res_diff.is_blocked is False
    assert res_diff.risk_level == "LOW"
    assert res_diff.risk_score < 30.0


def test_04_poster_manager():
    mgr = PosterManager()
    poster = mgr.create_or_get_poster(
        movie_id="m101",
        localized_title="기생충",
        original_title="Parasite",
        raw_image_url="https://example.com/poster.jpg",
        platform="넷플릭스",
        media_type="영화"
    )
    assert poster.localized_title == "기생충"
    assert "넷플릭스 영화 기생충 공식 포스터" == poster.poster_alt
    assert poster.poster_license_status == "VERIFIED"

    html = mgr.render_poster_html(poster)
    assert "ep-poster-wrapper" in html
    assert "aspect-ratio: 2/3" in html
    assert "max-width: 340px" in html
    assert 'alt="넷플릭스 영화 기생충 공식 포스터"' in html


def test_05_quality_evaluator():
    evaluator = V4QualityEvaluator()
    dummy_dup_low = DuplicateCheckResult(is_blocked=False, risk_level="LOW", risk_score=10.0)

    good_content = """
    <div class="ep-card">
      <div class="ep-poster-wrapper">
        <img src="poster.jpg" alt="넷플릭스 영화 기생충 공식 포스터" />
      </div>
      <h3 class="ep-card-title">기생충 (2019년 개봉, 132분)</h3>
      <p>공식 평점: 8.6점 / 10점 만점. 넷플릭스 스트리밍 중이며 광고형 월 5,500원 요금제 제공.</p>
      <div class="ep-table-container" style="overflow-x: auto;">
        <table class="ep-dark-table"><tr><td>비교</td></tr></table>
      </div>
      <div>OTT 정보 확인: 2026년 09월 25일</div>
    </div>
    """
    res = evaluator.evaluate(
        title="몰입감 넘치는 스릴러 영화 추천 5편",
        content_html=good_content,
        dup_result=dummy_dup_low,
        ott_verified=True,
        has_posters=True
    )
    assert res.total_score >= 85
    assert res.status == "AUTO_PUBLISH_ELIGIBLE"

    # High duplicate risk override test
    dummy_dup_high = DuplicateCheckResult(is_blocked=True, risk_level="HIGH", risk_score=95.0, block_reason="중복 감지")
    res_blocked = evaluator.evaluate(
        title="몰입감 넘치는 스릴러 영화 추천 5편",
        content_html=good_content,
        dup_result=dummy_dup_high,
        ott_verified=True,
        has_posters=True
    )
    assert res_blocked.status == "BLOCK"


def test_06_dark_editorial_css_override():
    # Verify dark CSS tokens and WordPress comment overrides
    css = ENTERPICK24_DARK_EDITORIAL_CSS
    assert "--ep-bg: #070a12;" in css
    assert "--ep-surface-card: #0f172a;" in css
    assert "#comments," in css
    assert ".comments-area," in css
    assert "textarea#comment" in css
    assert "#submit" in css
    assert "overflow-x: auto" in css
    assert "@media screen and (max-width: 540px)" in css


def test_07_existing_post_audit_logic():
    auditor = ExistingPostAuditor()
    audit_res = auditor.audit_existing_corpus()
    assert "total_posts" in audit_res
    assert audit_res["total_posts"] >= 5

    report = auditor.format_audit_report(audit_res)
    assert "EnterPick24 기존 게시물 중복 감사 리포트" in report
    assert "CANONICAL_CANDIDATE" in report or "KEEP" in report


def test_08_timestamp_synchronization():
    from zoneinfo import ZoneInfo
    from datetime import datetime, timezone
    from unittest.mock import patch, MagicMock
    from movie_content_skills.enterpick_adapter import EnterPickContentPipeline

    pipeline = EnterPickContentPipeline()
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "id": 999,
            "link": "https://enter.trendspot24.com/?p=999",
            "status": "future",
            "date": "2026-09-26T14:00:00",
            "date_gmt": "2026-09-26T05:00:00"
        }
        mock_post.return_value = mock_resp

        res = pipeline.publish_to_wordpress(
            title="테스트 예약 포스트",
            content="<p>내용</p>",
            status="future",
            scheduled_time_kst="2026-09-26 14:00:00"
        )

        assert res["success"] is True
        assert res["status"] == "future"
        assert res["scheduled_date_kst"] == "2026-09-26T14:00:00"
        assert res["scheduled_date_gmt"] == "2026-09-26T05:00:00"

        # Verify exact payload sent to WordPress REST API
        called_args, called_kwargs = mock_post.call_args
        payload = called_kwargs.get("json", {})
        assert payload["date"] == "2026-09-26T14:00:00"
        assert payload["date_gmt"] == "2026-09-26T05:00:00"
        assert payload["status"] == "future"


def test_09_daily_limit_cap():
    from core.reliability.daily_limit_engine import DEFAULT_DAILY_LIMITS
    assert DEFAULT_DAILY_LIMITS[4] == 3, "EnterPick24 (Site ID 4) daily limit must be strictly 3"

