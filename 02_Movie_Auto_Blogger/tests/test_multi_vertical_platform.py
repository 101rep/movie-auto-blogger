"""Unit and integration tests for Multi-Vertical Architecture, Registry, and Modules."""
import pytest
from sqlalchemy.orm import Session

from app.core.verticals import VerticalType, VerticalStatus, VERTICAL_METADATA
from app.core.registry import PlatformRegistry, get_platform_registry
from app.core.prompts.manager import PromptTemplateManager
from app.database.models import Post, Movie, Site, PostStatusEnum
from app.modules.movie.module import MovieModule
from app.modules.news.module import NewsModule
from app.modules.travel.module import TravelModule


def test_vertical_metadata_definitions():
    """Verify all defined verticals have Korean metadata and status."""
    assert VerticalType.MOVIE in VERTICAL_METADATA
    assert VerticalType.NEWS in VERTICAL_METADATA
    assert VerticalType.TRAVEL in VERTICAL_METADATA
    assert VerticalType.GAME in VERTICAL_METADATA
    assert VerticalType.PRODUCT in VERTICAL_METADATA

    assert VERTICAL_METADATA[VerticalType.MOVIE]["status"] == VerticalStatus.PRODUCTION
    assert VERTICAL_METADATA[VerticalType.NEWS]["status"] == VerticalStatus.COMING_SOON
    assert VERTICAL_METADATA[VerticalType.TRAVEL]["status"] == VerticalStatus.PRODUCTION


def test_platform_registry_registration_and_listing():
    """Verify PlatformRegistry correctly registers and lists content modules and API providers."""
    registry = PlatformRegistry()
    registry.register_module(MovieModule())
    registry.register_module(NewsModule())
    registry.register_module(TravelModule())

    # Retrieve specific module
    movie_mod = registry.get_module(VerticalType.MOVIE)
    assert movie_mod is not None
    assert movie_mod.vertical == VerticalType.MOVIE
    assert movie_mod.status == VerticalStatus.PRODUCTION

    news_mod = registry.get_module(VerticalType.NEWS)
    assert news_mod is not None
    assert news_mod.vertical == VerticalType.NEWS
    assert news_mod.status == VerticalStatus.COMING_SOON

    # List verticals
    vertical_list = registry.list_verticals()
    assert len(vertical_list) >= 3
    movie_entry = next(v for v in vertical_list if v["type"] == "MOVIE")
    assert movie_entry["is_active"] is True
    assert movie_entry["primary_provider"] == "TMDB"

    # List providers
    providers = registry.list_providers()
    provider_names = [p["name"] for p in providers]
    assert "TMDB" in provider_names
    assert "OPENAI" in provider_names
    assert "GEMINI" in provider_names
    assert "WORDPRESS" in provider_names


def test_prompt_template_manager_verticals():
    """Verify prompt manager provides dedicated prompts for each vertical."""
    movie_sys = PromptTemplateManager.get_system_prompt(VerticalType.MOVIE)
    news_sys = PromptTemplateManager.get_system_prompt(VerticalType.NEWS)
    travel_sys = PromptTemplateManager.get_system_prompt(VerticalType.TRAVEL)

    assert "영화" in movie_sys or "애드센스" in movie_sys
    assert "저널리스트" in news_sys or "뉴스" in news_sys
    assert "여행" in travel_sys

    # Test user prompt builders
    news_prompt = PromptTemplateManager.build_user_prompt(
        VerticalType.NEWS,
        {"title": "인공지능 규제법 통과", "sources": ["로이터", "연합뉴스"], "facts": ["법안 표결 80% 찬성"]}
    )
    assert "인공지능 규제법 통과" in news_prompt
    assert "로이터" in news_prompt

    travel_prompt = PromptTemplateManager.build_user_prompt(
        VerticalType.TRAVEL,
        {"city": "프라하", "country": "체코", "places": ["카를교", "프라하성"]}
    )
    assert "프라하" in travel_prompt
    assert "카를교" in travel_prompt


@pytest.mark.asyncio
async def test_movie_module_health_and_rendering():
    """Verify MovieModule wraps TMDB and renders responsive HTML."""
    mod = MovieModule()
    health = await mod.health_check()
    assert "success" in health

    # Test render_html through module
    mock_content = {
        "article": None,
        "movie_title": "테스트 영화",
        "poster_url": "https://image.tmdb.org/t/p/w500/test.jpg",
        "trailer_info": {
            "video_id": "test_id",
            "title": "공식 예고편",
            "embed_url": "https://www.youtube-nocookie.com/embed/test_id"
        }
    }
    html = mod.render_html(mock_content)
    assert "youtube-trailer" in html or "youtube.com/embed" in html or "youtube-nocookie.com/embed/test_id" in html


@pytest.mark.asyncio
async def test_news_module_placeholder():
    """Verify NewsModule placeholder returns graceful status."""
    mod = NewsModule()
    assert mod.vertical == VerticalType.NEWS
    assert mod.status == VerticalStatus.COMING_SOON
    health = await mod.health_check()
    assert health["success"] is False
    assert "준비 중" in health["message"]


@pytest.mark.asyncio
async def test_travel_module_production():
    """Verify TravelModule production returns active status and health check."""
    mod = TravelModule()
    assert mod.vertical == VerticalType.TRAVEL
    assert mod.status == VerticalStatus.PRODUCTION
    health = await mod.health_check()
    assert health["success"] is True
    assert "가동 중" in health["message"]


def test_post_and_site_multi_vertical_db_model(db_session: Session):
    """Verify Post model tracks vertical and can link to Site."""
    site = Site(
        name="시네마 인사이트",
        site_url="https://cinema-insight.com",
        vertical="MOVIE",
        is_active=True
    )
    db_session.add(site)
    db_session.commit()

    movie = Movie(
        source="tmdb",
        external_id="777123",
        title="멀티 버티컬 테스트 영화"
    )
    db_session.add(movie)
    db_session.commit()

    post = Post(
        movie_id=movie.id,
        site_id=site.id,
        vertical="MOVIE",
        title="멀티 버티컬 테스트 글",
        slug="multi-vertical-test-post",
        rendered_content="<p>내용</p>",
        status=PostStatusEnum.GENERATED.value
    )
    db_session.add(post)
    db_session.commit()

    db_session.refresh(post)
    assert post.vertical == "MOVIE"
    assert post.site_id == site.id
    assert post.site.name == "시네마 인사이트"
