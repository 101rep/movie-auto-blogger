# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Movie Content Skills Package (EnterPick24).
"""

import pytest
from movie_content_skills.data_adapter import VerifiedOTTDataAdapter
from movie_content_skills.generators import MovieSkillsEngine
from movie_content_skills.enterpick_adapter import EnterPickIsolationGuard, EnterPickContentPipeline
from core.reliability.quality_gate import ContentQualityGate


def test_01_isolation_guard():
    # Must pass for Site ID 4 (EnterPick24)
    EnterPickIsolationGuard.verify(4, "https://enter.trendspot24.com")

    # Must raise PermissionError for other sites
    with pytest.raises(PermissionError):
        EnterPickIsolationGuard.verify(1, "https://travelpick24.com")

    with pytest.raises(PermissionError):
        EnterPickIsolationGuard.verify(2, "https://trendspot24.com")

    with pytest.raises(PermissionError):
        EnterPickIsolationGuard.verify(3, "https://item.travelpick24.com")


def test_02_data_adapter():
    adapter = VerifiedOTTDataAdapter()
    show = adapter.search_title("Stranger Things")
    assert show is not None
    assert show["title"] == "Stranger Things"
    assert show["has_commercial_license"] is True
    assert show["backdrop_url"] is not None

    avail = adapter.get_streaming_availability("Squid Game")
    assert avail is not None
    assert "넷플릭스" in avail["availability"]
    assert avail["verified_date"] == "2026-09-25"


def test_03_generators_all_4_skills():
    engine = MovieSkillsEngine()

    # Skill 1: Movie TOP 5
    top5 = engine.generate_top5("스릴러")
    assert top5["skill"] == "movie-top5-writer"
    assert len(top5["movie_list"]) == 5
    assert "추천" in top5["title"]
    assert "추천 작품 비교 매트릭스" in top5["content"]
    assert len(top5["content"]) > 2500

    # Skill 2: OTT Movie Review
    review = engine.generate_review("Stranger Things")
    assert review["skill"] == "ott-movie-review"
    assert "Stranger Things" in review["title"]
    assert "스포일러 없는 줄거리" in review["content"]
    assert len(review["content"]) > 2500

    # Skill 3: OTT Theme Curator
    curation = engine.generate_curation("넷플릭스 범죄 수사극")
    assert curation["skill"] == "ott-theme-curator"
    assert len(curation["movie_list"]) == 4
    assert "분위기 & 템포 비교표" in curation["content"]
    assert len(curation["content"]) > 2500

    # Skill 4: OTT Streaming Guide
    guide = engine.generate_streaming_guide("Squid Game")
    assert guide["skill"] == "ott-streaming-guide"
    assert "보는 곳" in guide["title"]
    assert "플랫폼별 제공 현황" in guide["content"]
    assert "자주 묻는 질문" in guide["content"]
    assert len(guide["content"]) > 2000


def test_04_quality_gate_compliance():
    engine = MovieSkillsEngine()
    skills_data = [
        engine.generate_top5("미스터리"),
        engine.generate_review("Wednesday"),
        engine.generate_curation("디즈니+ 가족 영화"),
        engine.generate_streaming_guide("Kingdom")
    ]

    for data in skills_data:
        gate = ContentQualityGate.evaluate(
            title=data["title"],
            content=data["content"],
            category="OTT 매거진",
            image_url=data.get("featured_image")
        )
        assert gate.passed is True, f"Skill {data['skill']} failed quality gate: {gate.issues}"
        assert gate.score >= 80


def test_05_telegram_report_formatter():
    mock_results = [
        {
            "slot": 1,
            "skill": "movie-top5-writer",
            "title": "주말 스릴러 영화 추천 5편",
            "movie_list": ["영화A", "영화B", "영화C"],
            "scheduled_time": "2026-09-25 08:00 KST",
            "post_id": 991,
            "status": "draft",
            "link": "https://enter.trendspot24.com/?p=991",
            "success": True
        },
        {
            "slot": 2,
            "skill": "ott-movie-review",
            "title": "화제작 리뷰",
            "success": False,
            "error": "품질 검증 실패"
        }
    ]
    report = EnterPickContentPipeline.format_telegram_report(mock_results)
    assert "엔터픽24 영화·OTT 4대 스킬 자동 발행 보고서" in report
    assert "movie-top5-writer" in report
    assert "#991" in report
    assert "품질 검증 실패" in report
    # Ensure sensitive credentials are never in report
    assert "aUma6aot" not in report
    assert "ktaehoon" not in report
