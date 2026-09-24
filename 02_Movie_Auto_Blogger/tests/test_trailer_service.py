"""Tests for TrailerService v2, YouTubeService, and upgraded multi-video article features."""
import pytest
from app.ai.schemas import ArticleOutput
from app.services.article_service import ArticleService
from app.services.trailer_service import TrailerService
from app.services.youtube_service import YouTubeService, YouTubeVideoInfo, AudienceReaction
from app.services.scoring_service import CandidateScoringService
from tests.test_ai_providers import create_sample_article


# ─── TrailerService (backward-compat) ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_trailer_service_tmdb_priority(monkeypatch):
    """Verify TrailerService retrieves YouTube trailer from TMDB videos first."""
    class FakeTMDB:
        async def get_movie_videos(self, movie_id: str):
            return [
                {"site": "Vimeo", "type": "Trailer", "key": "12345"},
                {"site": "YouTube", "type": "Teaser", "key": "teaser_key"},
                {"site": "YouTube", "type": "Trailer", "name": "공식 메인 예고편", "key": "official_trailer_key"}
            ]

    svc = TrailerService(tmdb_provider=FakeTMDB(), youtube_api_key="test-key")
    res = await svc.get_trailer_info("테스트 영화", external_id="12345")

    assert res is not None
    assert res["video_id"] == "official_trailer_key"
    assert "https://www.youtube-nocookie.com/embed/official_trailer_key" == res["embed_url"]
    assert res["source"] == "tmdb"


@pytest.mark.asyncio
async def test_trailer_service_graceful_none_when_empty():
    """Verify TrailerService returns None gracefully when no videos found."""
    class EmptyTMDB:
        async def get_movie_videos(self, movie_id: str):
            return []

    svc = TrailerService(tmdb_provider=EmptyTMDB(), youtube_api_key="")
    res = await svc.get_trailer_info("미지의 영화", external_id="999999")
    assert res is None


# ─── YouTubeService Unit Tests ──────────────────────────────────────────────────

def test_youtube_hype_score_high_viral():
    """Viral video (20M views, 5% like ratio, 100K comments) should score 10."""
    score = YouTubeService._compute_hype_score(
        view_count=20_000_000,
        like_count=1_000_000,   # 5% ratio
        comment_count=100_000,
    )
    assert score == 10


def test_youtube_hype_score_moderate():
    """Moderate video (500K views, 2% likes, 2K comments) should score 4-6."""
    score = YouTubeService._compute_hype_score(
        view_count=500_000,
        like_count=10_000,   # 2% ratio
        comment_count=2_000,
    )
    assert 3 <= score <= 6


def test_youtube_hype_score_zero_views():
    """Video with zero views should score 0."""
    score = YouTubeService._compute_hype_score(view_count=0, like_count=0, comment_count=0)
    assert score == 0


def test_youtube_hype_score_max_cap():
    """Score should never exceed 10."""
    score = YouTubeService._compute_hype_score(
        view_count=100_000_000,
        like_count=10_000_000,
        comment_count=5_000_000,
    )
    assert score == 10


def test_youtube_sentiment_summary_labels():
    """Sentiment labels should correspond correctly to hype scores."""
    assert YouTubeService._derive_sentiment_summary(9, 50000) == "폭발적인 기대감 (초화제작)"
    assert YouTubeService._derive_sentiment_summary(7, 10000) == "높은 기대감 (화제작)"
    assert YouTubeService._derive_sentiment_summary(5, 5000) == "긍정적 반응 (기대작)"
    assert YouTubeService._derive_sentiment_summary(3, 1000) == "관심 증가 중"
    assert YouTubeService._derive_sentiment_summary(1, 100) == "반응 집계 중"


def test_youtube_classify_tmdb_type():
    """TMDB video types should map to internal type keys correctly."""
    assert YouTubeService._classify_tmdb_type("Trailer") == "trailer"
    assert YouTubeService._classify_tmdb_type("Teaser") == "teaser"
    assert YouTubeService._classify_tmdb_type("Featurette") == "making"
    assert YouTubeService._classify_tmdb_type("Behind the Scenes") == "making"
    assert YouTubeService._classify_tmdb_type("Clip") == "clip"
    assert YouTubeService._classify_tmdb_type("Unknown") == "other"


def test_youtube_video_info_to_dict():
    """YouTubeVideoInfo.to_dict() should contain all required keys."""
    info = YouTubeVideoInfo(
        video_id="abc123",
        title="테스트 예고편",
        video_type="trailer",
        embed_url="https://www.youtube-nocookie.com/embed/abc123",
        watch_url="https://www.youtube.com/watch?v=abc123",
        view_count=1_000_000,
        like_count=50_000,
        comment_count=3_000,
        channel_name="Test Channel",
    )
    d = info.to_dict()
    assert d["video_id"] == "abc123"
    assert d["type_label"] == "공식 예고편"
    assert d["view_count"] == 1_000_000
    assert d["channel_name"] == "Test Channel"


def test_youtube_disabled_without_api_key(monkeypatch):
    """YouTubeService should be disabled when no API key is configured."""
    # Monkeypath settings to return empty key so the service is truly disabled
    from app import config as cfg
    monkeypatch.setattr(cfg.get_settings(), "YOUTUBE_API_KEY", "", raising=False)
    svc = YouTubeService(youtube_api_key="")
    assert not svc._enabled


def test_youtube_build_search_queries_with_existing_trailer():
    """Should skip teaser query when trailer already found."""
    queries = YouTubeService._build_search_queries("범죄도시4", already_found=1)
    types = [q[1] for q in queries]
    assert "teaser" not in types
    assert "making" in types


def test_youtube_build_search_queries_no_trailer():
    """Should include teaser query when no trailer found yet."""
    queries = YouTubeService._build_search_queries("범죄도시4", already_found=0)
    types = [q[1] for q in queries]
    assert "teaser" in types


def test_audience_reaction_to_dict():
    """AudienceReaction.to_dict() should return expected structure."""
    reaction = AudienceReaction(
        total_comment_count=5000,
        top_comments=["정말 기대됩니다!", "역대급 영상미네요"],
        sentiment_summary="높은 기대감 (화제작)",
        hype_score=7,
    )
    d = reaction.to_dict()
    assert d["hype_score"] == 7
    assert d["total_comment_count"] == 5000
    assert "정말 기대됩니다!" in d["top_comments"]


# ─── CandidateScoringService with YouTube Bonus ───────────────────────────────

def test_scoring_with_youtube_bonus():
    """YouTube bonus should be added to total score correctly."""
    from app.collectors.base import NormalizedMovie
    from datetime import date

    movie = NormalizedMovie(
        source="tmdb",
        external_id="12345",
        title="테스트 영화",
        popularity=50.0,
        vote_average=7.5,
        vote_count=500,
        release_date="2026-08-01",
        overview="테스트 줄거리 내용입니다 충분히 길게 작성합니다.",
        poster_reference="https://example.com/poster.jpg",
        director="홍길동",
        major_cast=["배우A", "배우B", "배우C"],
    )
    ref = date(2026, 9, 15)

    # Without bonus
    score_no_bonus, breakdown_no_bonus = CandidateScoringService.calculate_score(movie, ref, youtube_bonus=0.0)
    # With bonus
    score_with_bonus, breakdown_with_bonus = CandidateScoringService.calculate_score(movie, ref, youtube_bonus=8.0)

    assert breakdown_with_bonus["youtube_bonus"] == 8.0
    assert abs(score_with_bonus - score_no_bonus - 8.0) < 0.01
    assert "youtube_bonus" in breakdown_no_bonus
    assert breakdown_no_bonus["youtube_bonus"] == 0.0


def test_scoring_youtube_bonus_clamped_to_10():
    """YouTube bonus exceeding 10 should be clamped to 10."""
    from app.collectors.base import NormalizedMovie

    movie = NormalizedMovie(
        source="tmdb",
        external_id="99999",
        title="초화제작",
        popularity=200.0,
        vote_average=9.0,
        vote_count=5000,
    )
    _, breakdown = CandidateScoringService.calculate_score(movie, youtube_bonus=50.0)
    assert breakdown["youtube_bonus"] == 10.0


def test_scoring_youtube_bonus_negative_clamped_to_zero():
    """Negative YouTube bonus should be clamped to 0."""
    from app.collectors.base import NormalizedMovie

    movie = NormalizedMovie(
        source="tmdb",
        external_id="11111",
        title="저인기 영화",
        popularity=5.0,
        vote_average=5.0,
        vote_count=50,
    )
    _, breakdown = CandidateScoringService.calculate_score(movie, youtube_bonus=-5.0)
    assert breakdown["youtube_bonus"] == 0.0


# ─── Article Rendering with Multi-Video & Audience Reaction ───────────────────

def test_article_rendering_with_trailer_and_schema():
    """Verify ArticleService renders YouTube trailer embed and Schema.org JSON-LD."""
    article = create_sample_article()
    article.hook_quote = "과거에 얽매이면 미래를 잃는다."
    article.director_vision = "빛과 그림자의 강렬한 대비를 통해 내면의 불안을 시각화함."
    article.not_recommended_for = ["빠른 전개의 팝콘 무비를 원하는 분"]
    article.post_credit_scene = "엔딩 크레딧 후 다음 시리즈를 암시하는 쿠키 영상 1개가 있습니다."
    article.rating_score = 9.2
    article.rating_reason = "압도적인 미장센과 깊이 있는 메시지"

    service = ArticleService()
    trailer_info = {
        "video_id": "abc123xyz",
        "title": "공식 예고편",
        "embed_url": "https://www.youtube-nocookie.com/embed/abc123xyz",
        "watch_url": "https://www.youtube.com/watch?v=abc123xyz",
        "source": "tmdb"
    }

    rendered = service.render_html(
        article=article,
        movie_title="테스트 영화",
        poster_url="https://image.tmdb.org/poster.jpg",
        media_enabled=True,
        trailer_info=trailer_info
    )

    # 1. Check YouTube Trailer embed
    assert 'src="https://www.youtube-nocookie.com/embed/abc123xyz"' in rendered
    assert "공식 예고편 영상" in rendered

    # 2. Check Schema.org JSON-LD
    assert 'application/ld+json' in rendered
    assert '"@type": "Review"' in rendered
    assert '"@type": "Movie"' in rendered
    assert '"ratingValue": "9.2"' in rendered

    # 3. Check E-E-A-T elements
    assert "과거에 얽매이면 미래를 잃는다." in rendered
    assert "빛과 그림자의 강렬한 대비" in rendered
    assert "쿠키 영상 유무 및 관람 꿀팁" in rendered
    assert "에디터 평점 9.2" in rendered


def test_article_rendering_with_audience_reaction():
    """Verify audience reaction section renders correctly in article HTML."""
    article = create_sample_article()
    service = ArticleService()
    trailer_info = {
        "video_id": "xyz789",
        "title": "공식 예고편",
        "embed_url": "https://www.youtube-nocookie.com/embed/xyz789",
        "watch_url": "https://www.youtube.com/watch?v=xyz789",
        "source": "tmdb",
    }
    audience_reaction = {
        "total_comment_count": 15000,
        "top_comments": ["이번 영화 진짜 기대됩니다!", "역대급 예고편이네요"],
        "sentiment_summary": "높은 기대감 (화제작)",
        "hype_score": 7,
    }

    rendered = service.render_html(
        article=article,
        movie_title="테스트 영화",
        trailer_info=trailer_info,
        audience_reaction=audience_reaction,
    )

    assert "유튜브 관객 반응" in rendered
    assert "15,000" in rendered
    assert "화제도 7/10" in rendered
    assert "높은 기대감 (화제작)" in rendered
    assert "이번 영화 진짜 기대됩니다!" in rendered


def test_article_rendering_with_multi_videos():
    """Verify multi-video grid section renders correctly in article HTML."""
    article = create_sample_article()
    service = ArticleService()
    multi_videos = [
        {
            "video_id": "making001",
            "title": "메이킹 필름 - 비하인드 더 씬",
            "video_type": "making",
            "type_label": "메이킹 필름",
            "embed_url": "https://www.youtube-nocookie.com/embed/making001",
            "watch_url": "https://www.youtube.com/watch?v=making001",
            "source": "youtube_api",
            "view_count": 250000,
            "like_count": 8000,
            "comment_count": 300,
            "channel_name": "영화사 공식채널",
        },
        {
            "video_id": "ost001",
            "title": "메인 OST - 감동의 선율",
            "video_type": "ost",
            "type_label": "OST / 사운드트랙",
            "embed_url": "https://www.youtube-nocookie.com/embed/ost001",
            "watch_url": "https://www.youtube.com/watch?v=ost001",
            "source": "youtube_api",
            "view_count": 120000,
            "like_count": None,
            "comment_count": 150,
            "channel_name": None,
        }
    ]

    rendered = service.render_html(
        article=article,
        movie_title="테스트 영화",
        multi_videos=multi_videos,
    )

    assert "관련 영상 더 보기" in rendered
    assert "메이킹 필름" in rendered
    assert "OST / 사운드트랙" in rendered
    assert "making001" in rendered
    assert "ost001" in rendered
    assert "250,000" in rendered
    assert "영화사 공식채널" in rendered


def test_article_rendering_empty_multi_videos_no_section():
    """When multi_videos is empty, related video section should not appear."""
    article = create_sample_article()
    service = ArticleService()

    rendered = service.render_html(
        article=article,
        movie_title="테스트 영화",
        multi_videos=[],
    )

    assert "관련 영상 더 보기" not in rendered


def test_article_rendering_no_audience_reaction_no_section():
    """When audience_reaction is None, reaction section should not appear."""
    article = create_sample_article()
    service = ArticleService()
    trailer_info = {
        "video_id": "noreaction",
        "title": "예고편",
        "embed_url": "https://www.youtube-nocookie.com/embed/noreaction",
        "watch_url": "https://www.youtube.com/watch?v=noreaction",
        "source": "tmdb",
    }

    rendered = service.render_html(
        article=article,
        movie_title="테스트 영화",
        trailer_info=trailer_info,
        audience_reaction=None,
    )

    assert "유튜브 관객 반응" not in rendered
