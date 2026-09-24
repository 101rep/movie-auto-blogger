"""Tests for Naver Movie Rating Scraper Service and HTML integration."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.ai.schemas import ArticleOutput, FAQItem
from app.database.models import Base, Movie
from app.services.article_service import ArticleService
from app.services.naver_rating_service import (
    NaverRatingResult,
    NaverRatingService,
)


@pytest.fixture
def db_session():
    """In-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_clean_title():
    """Verify movie title normalization for Naver search."""
    assert NaverRatingService.clean_title("파묘 (2024)") == "파묘"
    assert NaverRatingService.clean_title("베놈: 라스트 댄스") == "베놈"
    assert NaverRatingService.clean_title("인셉션") == "인셉션"
    assert NaverRatingService.clean_title("아바타: 물의 길 (3D)") == "아바타"


def test_parse_rating_html_primary_dom():
    """Verify extraction from Naver's primary area_star_number DOM."""
    html_sample = """
    <div class="lego_rating_box_see">
      <strong class="area_subtitle">실관람객 평점</strong>
      <span class="area_star_number">8.23<span class="area_star_total_number">10</span></span>
      <span class="area_people">3,199명 참여</span>
    </div>
    """
    res = NaverRatingService._parse_rating_html(html_sample, "파묘", "https://search.naver.com")
    assert res is not None
    assert res.movie_title == "파묘"
    assert res.rating == 8.23
    assert res.rating_type == "실관람객"
    assert res.vote_count_str == "3,199명"


def test_parse_rating_html_netizen_fallback():
    """Verify fallback to netizen rating pattern."""
    html_sample = """
    <div class="rating_box">
      <span>네티즌 평점 7.50점</span>
    </div>
    """
    res = NaverRatingService._parse_rating_html(html_sample, "테스트 영화", "https://search.naver.com")
    assert res is not None
    assert res.rating == 7.50
    assert res.rating_type == "네티즌"


def test_parse_rating_html_no_rating():
    """Verify graceful None return when page does not contain ratings."""
    html_sample = "<html><body>검색 결과가 없습니다.</body></html>"
    res = NaverRatingService._parse_rating_html(html_sample, "미개봉영화", "https://search.naver.com")
    assert res is None


def test_movie_model_naver_rating_persistence(db_session):
    """Verify Movie model persists Naver rating fields."""
    movie = Movie(
        id=1,
        external_id="tmdb-naver-1",
        title="파묘",
        naver_rating=8.23,
        naver_rating_type="실관람객",
        naver_vote_count="3,199명"
    )
    db_session.add(movie)
    db_session.commit()

    retrieved = db_session.query(Movie).filter(Movie.id == 1).first()
    assert retrieved is not None
    assert retrieved.naver_rating == 8.23
    assert retrieved.naver_rating_type == "실관람객"
    assert retrieved.naver_vote_count == "3,199명"


def test_render_html_with_naver_rating_badge():
    """Verify rendered HTML includes Naver rating badge when movie has naver_rating."""
    movie = Movie(
        id=2,
        external_id="tmdb-naver-2",
        title="베놈: 라스트 댄스",
        naver_rating=7.13,
        naver_rating_type="실관람객",
        naver_vote_count="1,367명"
    )

    article = ArticleOutput(
        title="베놈 라스트 댄스 솔직 후기 및 관람 가이드",
        excerpt="베놈 라스트 댄스의 줄거리와 관람 포인트를 정리한 글입니다. 영화의 볼거리가 가득합니다.",
        slug_hint="venom-review",
        introduction="영화 베놈은 빌런 히어로의 매력을 보여주는 완벽한 작품입니다.",
        basic_info_summary="톰 하디 주연의 SF 액션 블록버스터 영화입니다.",
        spoiler_free_synopsis="에디와 베놈은 도망자 신세가 되어 쫓기는 신세에 처합니다.",
        cast_and_director="톰 하디와 켈리 마르셀 감독의 세 번째 협업작입니다.",
        viewing_points=["화려한 액션 시퀀스", "에디와 베놈의 케미스트리"],
        recommended_for=["액션 영화 매니아"],
        conclusion="베놈 시리즈의 대미를 장식하는 유쾌한 액션 영화입니다.",
        seo_title="베놈 라스트 댄스 관람 포인트 평점 정리",
        meta_description="베놈 라스트 댄스의 줄거리와 네이버 평점, 관람 팁 총정리.",
        tags=["베놈", "톰하디"],
        rating_score=8.5
    )

    article_service = ArticleService()
    rendered = article_service.render_html(
        article=article,
        movie_title=movie.title,
        movie=movie
    )

    assert "mab-badge-naver" in rendered
    assert "7.13" in rendered
    assert "네이버 실관람객" in rendered
    assert "1,367명" in rendered
