"""Unit tests for HTML article rendering and generation pipeline."""
import pytest
from sqlalchemy.orm import Session

from app.ai.router import AIProviderRouter
from app.database.models import Movie, Post, PostStatusEnum, QualityStatusEnum
from app.services.article_service import ArticleService
from tests.test_ai_providers import MockProvider, create_sample_article


def test_article_html_rendering():
    """Verify ArticleOutput renders into valid semantic HTML with required headings."""
    article = create_sample_article()
    service = ArticleService()

    rendered = service.render_html(
        article=article,
        movie_title="인사이드 아웃 2",
        poster_url="https://image.tmdb.org/t/p/w780/sample.jpg",
        media_enabled=True,
        internal_links=[{"title": "이전 글 보기", "url": "https://blog.com/prev-movie"}]
    )

    # Check semantic H2 sections per Section 14
    assert "<h2>영화 기본정보</h2>" in rendered
    assert "<h2>💡 제목의 의미와 숨겨진 상징성</h2>" in rendered
    assert "<h2>스포일러 없는 줄거리</h2>" in rendered
    assert "<h2>감독과 주요 출연진</h2>" in rendered
    assert "<h2>🎭 인물 갈등 구도와 심리전 분석</h2>" in rendered
    assert "<h2>관람 포인트</h2>" in rendered
    assert "<h2>이런 분께 추천합니다</h2>" in rendered
    assert "<h2>함께 살펴볼 영화</h2>" in rendered
    assert "⚠️ [스포일러 주의] 결말 복선 및 심층 해석 보기" in rendered
    assert "<h2>자주 묻는 질문</h2>" in rendered
    assert "<h2>마무리</h2>" in rendered
    assert "에디터의 생각거리 & 독자 토론" in rendered

    # Check poster rendering
    assert 'src="https://image.tmdb.org/t/p/w780/sample.jpg"' in rendered

    # Check internal links
    assert "https://blog.com/prev-movie" in rendered


@pytest.mark.asyncio
async def test_generate_article_for_movie_pipeline(db_session: Session):
    """Verify complete generation pipeline saves Post with GENERATED status."""
    movie = Movie(
        source="tmdb",
        external_id="1022789",
        title="인사이드 아웃 2",
        overview="13살이 된 라일리의 감정 컨트롤 본부 이야기.",
        release_date="2024-06-12",
        director="켈시 만",
        popularity=1200.0,
        poster_reference="https://image.tmdb.org/poster.jpg"
    )
    db_session.add(movie)
    db_session.commit()

    sample_art = create_sample_article()
    mock_provider = MockProvider("openai", should_succeed=True, return_article=sample_art)
    mock_router = AIProviderRouter(openai_provider=mock_provider, primary="openai")
    service = ArticleService(ai_router=mock_router)

    post, gen_result, quality_status, issues = await service.generate_article_for_movie(
        db_session, movie, save_post=True
    )

    assert post is not None
    assert post.id is not None
    assert post.title == sample_art.title
    assert post.status == PostStatusEnum.GENERATED.value
    assert quality_status == QualityStatusEnum.PASS
    assert "<h2>영화 기본정보</h2>" in post.rendered_content
    assert post.ai_used_provider == "openai"
