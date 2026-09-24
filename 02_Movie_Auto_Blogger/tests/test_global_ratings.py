"""Tests for Global and Domestic Multi-Rating system."""
import pytest
from app.collectors.base import NormalizedMovie
from app.database.models import Movie
from app.services.global_rating_service import GlobalRatingService, GlobalRatingBundle
from app.services.article_service import ArticleService
from app.ai.schemas import ArticleOutput, FAQItem
from app.ai.prompts import build_user_prompt


@pytest.mark.asyncio
async def test_synthesize_fallback_ratings():
    """Verify fallback rating calculation produces accurate and sensible metrics."""
    res = GlobalRatingService.synthesize_fallback_ratings(
        tmdb_vote_average=8.4,
        tmdb_vote_count=2500,
        naver_rating=8.9
    )
    assert res["imdb_rating"] == 8.4
    assert "명" in res["imdb_votes"]
    assert "%" in res["rotten_tomatoes_score"]
    assert "Fresh" in res["rotten_tomatoes_score"]
    assert "/ 100" in res["metacritic_score"]
    assert res["watcha_rating"] > 3.5


@pytest.mark.asyncio
async def test_aggregate_ratings_bundle():
    """Verify aggregate_ratings returns complete GlobalRatingBundle."""
    bundle = await GlobalRatingService.aggregate_ratings(
        title="인셉션",
        original_title="Inception",
        release_date="2010-07-16",
        imdb_id="tt1375666",
        tmdb_vote_average=8.36,
        tmdb_vote_count=34000,
        naver_rating=9.60,
        naver_rating_type="실관람객",
        naver_vote_count="2,345명"
    )
    assert isinstance(bundle, GlobalRatingBundle)
    assert bundle.imdb_rating is not None
    assert bundle.naver_rating == 9.60
    assert bundle.rotten_tomatoes_score is not None
    assert bundle.metacritic_score is not None
    assert bundle.watcha_rating is not None


def test_movie_model_global_ratings_persistence(db_session):
    """Verify all global rating columns persist correctly in Movie DB model."""
    movie = Movie(
        source="tmdb",
        external_id="test_global_movie_1",
        title="글로벌 블록버스터",
        imdb_id="tt9999999",
        imdb_rating=8.7,
        imdb_votes="150,000명",
        rotten_tomatoes_score="94% Certified Fresh",
        metacritic_score="85 / 100",
        watcha_rating=4.3,
        naver_rating=8.95,
        naver_rating_type="실관람객",
        naver_vote_count="1,200명"
    )
    db_session.add(movie)
    db_session.commit()

    retrieved = db_session.query(Movie).filter(Movie.external_id == "test_global_movie_1").first()
    assert retrieved is not None
    assert retrieved.imdb_id == "tt9999999"
    assert retrieved.imdb_rating == 8.7
    assert retrieved.rotten_tomatoes_score == "94% Certified Fresh"
    assert retrieved.metacritic_score == "85 / 100"
    assert retrieved.watcha_rating == 4.3
    assert retrieved.naver_rating == 8.95


def test_render_html_with_all_global_rating_badges():
    """Verify rendered HTML includes all global rating badges."""
    movie = Movie(
        source="tmdb",
        external_id="test_render_ratings_1",
        title="어벤져스",
        imdb_rating=8.4,
        imdb_votes="1,200,000명",
        rotten_tomatoes_score="92% Certified Fresh",
        metacritic_score="79 / 100",
        watcha_rating=4.1,
        naver_rating=8.80,
        naver_rating_type="실관람객",
        naver_vote_count="5,000명",
        release_date="2026-05-01",
        runtime=150
    )

    article = ArticleOutput(
        title="영화 어벤져스 리뷰 줄거리 총정리",
        slug_hint="avengers-review",
        excerpt="어벤져스의 역대급 리뷰입니다.",
        introduction="도입부 내용입니다. 200자 이상으로 길게 작성합니다. 영화의 감동과 전율을 생생하게 전달합니다.",
        basic_info_summary="액션 히어로 블록버스터의 정점",
        theme_symbolism="영웅들의 연대와 희생을 상징하는 서사",
        spoiler_free_synopsis="지구를 위협하는 거대한 악에 맞서 히어로들이 뭉치는 초중반 이야기입니다.",
        cast_and_director="초호화 캐스팅과 명감독의 뛰어난 연출력이 빛납니다.",
        character_dynamics="개성 강한 영웅들 사이의 갈등과 화합이 매력적입니다.",
        director_vision="압도적인 스케일의 전투 씬과 정교한 시각효과",
        hook_quote="우리는 어벤져스다.",
        viewing_points=["화려한 액션", "캐릭터 케미", "사운드트랙"],
        recommended_for=["마블 팬", "블록버스터 애호가"],
        not_recommended_for=["단순한 드라마를 선호하는 분"],
        spoiler_deep_dive="마지막 결말의 복선과 차기작 떡밥 해설입니다.",
        post_credit_scene="엔딩 크레딧 후 2개의 쿠키 영상이 있습니다.",
        faq=[FAQItem(question="쿠키 영상 몇 개인가요?", answer="2개입니다.")],
        conclusion="어벤져스는 최고의 히어로 영화입니다.",
        rating_score=9.2,
        rating_reason="완벽한 시각적 쾌감과 서사의 조화",
        seo_title="영화 어벤져스 리뷰 평점 총정리",
        meta_description="어벤져스 리뷰와 평점 정보",
        tags=["어벤져스", "영화 리뷰"],
        engagement_question="여러분은 어떤 히어로의 활약이 가장 인상 깊으셨나요?"
    )

    article_service = ArticleService()
    rendered = article_service.render_html(
        article=article,
        movie_title="어벤져스",
        movie=movie
    )

    assert "mab-badge-imdb" in rendered
    assert "IMDb 8.4" in rendered
    assert "mab-badge-rotten" in rendered
    assert "로튼토마토 92%" in rendered
    assert "mab-badge-metacritic" in rendered
    assert "메타크리틱 79" in rendered
    assert "mab-badge-naver" in rendered
    assert "네이버 실관람객 8.8" in rendered
    assert "mab-badge-watcha" in rendered
    assert "왓챠피디아 ★ 4.1" in rendered


def test_build_user_prompt_with_global_ratings():
    """Verify build_user_prompt includes global ratings in factual section."""
    movie_data = {
        "title": "오펜하이머",
        "original_title": "Oppenheimer",
        "release_date": "2023-08-15",
        "runtime": 180,
        "genres": ["드라마", "역사"],
        "director": "크리스토퍼 놀란",
        "major_cast": ["킬리언 머피", "에밀리 블런트"],
        "vote_average": 8.1,
        "vote_count": 9500,
        "imdb_rating": 8.9,
        "imdb_votes": "750,000명",
        "rotten_tomatoes_score": "93% Certified Fresh",
        "metacritic_score": "88 / 100",
        "naver_rating": 8.52,
        "naver_rating_type": "실관람객",
        "naver_vote_count": "14,500명",
        "watcha_rating": 4.2
    }

    prompt = build_user_prompt(movie_data)
    assert "글로벌 IMDb 평점: 8.9/10점" in prompt
    assert "로튼 토마토 신선도 지수: 93% Certified Fresh" in prompt
    assert "메타크리틱 메타스코어: 88 / 100" in prompt
    assert "국내 네이버 평점" in prompt
    assert "국내 왓챠피디아 평점: ★ 4.2/5.0점" in prompt
