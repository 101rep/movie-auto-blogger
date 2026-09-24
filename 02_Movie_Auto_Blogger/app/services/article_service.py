"""Article generation coordinator and HTML rendering service."""
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.ai.router import AIProviderRouter
from app.ai.schemas import ArticleOutput, GenerationResult
from app.config import get_settings
from app.database.models import Movie, Post, PostStatusEnum, QualityStatusEnum
from app.services.quality_service import QualityGateService
from app.services.trailer_service import TrailerService
from app.utils.logging import get_logger
from app.utils.slug import generate_slug

logger = get_logger("article_service")

# Initialize Jinja2 environment for article rendering
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml"])
)


class ArticleService:
    """Service responsible for AI article generation, quality checks, and HTML rendering."""

    def __init__(self, ai_router: Optional[AIProviderRouter] = None, trailer_service: Optional[TrailerService] = None) -> None:
        self.router = ai_router or AIProviderRouter()
        self.trailer_service = trailer_service or TrailerService()
        self.settings = get_settings()

    def render_html(
        self,
        article: ArticleOutput,
        movie_title: str,
        poster_url: Optional[str] = None,
        media_enabled: bool = True,
        internal_links: Optional[List[Dict[str, str]]] = None,
        trailer_info: Optional[Dict[str, str]] = None,
        movie: Optional[Any] = None,
        multi_videos: Optional[List[Dict[str, Any]]] = None,
        audience_reaction: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Render ArticleOutput into controlled, semantic WordPress-compatible HTML.

        New parameters v2:
            multi_videos: List of additional video dicts (trailers, making-of, OST, interviews).
            audience_reaction: YouTube comment sentiment data for trailer.
        """
        template = jinja_env.get_template("article.html")
        return template.render(
            article=article,
            movie_title=movie_title,
            poster_url=poster_url,
            media_enabled=media_enabled,
            internal_links=internal_links or [],
            trailer_info=trailer_info,
            movie=movie,
            multi_videos=multi_videos or [],
            audience_reaction=audience_reaction,
        )

    async def generate_article_for_movie(
        self,
        db: Session,
        movie: Movie,
        save_post: bool = True
    ) -> Tuple[Optional[Post], GenerationResult, QualityStatusEnum, List[str]]:
        """Generate, validate, and optionally persist an article for a given Movie."""
        logger.info("Generating article for movie: %s (ID: %s)...", movie.title, movie.external_id)

        # Parse stored json fields
        genres = json.loads(movie.genres_json) if movie.genres_json else []
        major_cast = json.loads(movie.cast_json) if movie.cast_json else []

        movie_data = {
            "title": movie.title,
            "original_title": movie.original_title,
            "overview": movie.overview,
            "release_date": movie.release_date,
            "runtime": movie.runtime,
            "genres": genres,
            "popularity": movie.popularity,
            "vote_average": movie.vote_average,
            "vote_count": movie.vote_count,
            "imdb_id": getattr(movie, "imdb_id", None),
            "imdb_rating": getattr(movie, "imdb_rating", None),
            "imdb_votes": getattr(movie, "imdb_votes", None),
            "rotten_tomatoes_score": getattr(movie, "rotten_tomatoes_score", None),
            "metacritic_score": getattr(movie, "metacritic_score", None),
            "watcha_rating": getattr(movie, "watcha_rating", None),
            "naver_rating": getattr(movie, "naver_rating", None),
            "naver_rating_type": getattr(movie, "naver_rating_type", None),
            "naver_vote_count": getattr(movie, "naver_vote_count", None),
            "director": movie.director,
            "major_cast": major_cast,
        }

        # 1. AI Generation via Router (Primary -> Fallback)
        gen_result = await self.router.generate_article(movie_data)

        if not gen_result.success or not gen_result.article:
            logger.error("Article generation completely failed for movie '%s': %s", movie.title, gen_result.error_message)
            if save_post:
                failed_post = Post(
                    movie_id=movie.id,
                    title=f"[생성 실패] {movie.title}",
                    slug=generate_slug(f"failed-{movie.external_id}"),
                    status=PostStatusEnum.FAILED.value,
                    ai_requested_provider=gen_result.requested_provider,
                    ai_used_provider=gen_result.used_provider,
                    fallback_used=gen_result.fallback_used,
                    quality_status=QualityStatusEnum.FAIL.value,
                    failure_reason=gen_result.error_message
                )
                db.add(failed_post)
                db.commit()
                return failed_post, gen_result, QualityStatusEnum.FAIL, [gen_result.error_message or "AI 생성 실패"]
            return None, gen_result, QualityStatusEnum.FAIL, [gen_result.error_message or "AI 생성 실패"]

        article = gen_result.article

        # 2. Quality Gate Evaluation
        quality_status, issues = QualityGateService.evaluate(article, expected_movie_title=movie.title, movie=movie)

        # 3. Discover Multi-Video Content & HTML Rendering
        trailer_info = await self.trailer_service.get_trailer_info(
            movie_title=movie.title,
            external_id=movie.external_id
        )

        # 3a. Fetch all related YouTube videos (trailers, teasers, making-of, OST, interviews)
        multi_videos: List[Dict] = []
        try:
            all_vids = await self.trailer_service.get_all_movie_videos(
                movie_title=movie.title,
                external_id=movie.external_id,
                max_additional=3,
            )
            # Exclude primary trailer from supplemental list (already shown as main)
            primary_id = trailer_info.get("video_id") if trailer_info else None
            multi_videos = [v for v in all_vids if v.get("video_id") != primary_id]
        except Exception as e:
            logger.warning("Failed to fetch multi-videos for '%s': %s", movie.title, e)

        # 3b. Fetch audience reaction (YouTube comments sentiment) for main trailer
        audience_reaction = None
        try:
            if trailer_info and trailer_info.get("video_id"):
                audience_reaction = await self.trailer_service.get_audience_reaction_for_trailer(
                    trailer_video_id=trailer_info["video_id"]
                )
        except Exception as e:
            logger.warning("Failed to fetch audience reaction for '%s': %s", movie.title, e)

        rendered_html = self.render_html(
            article=article,
            movie_title=movie.title,
            poster_url=movie.poster_reference,
            media_enabled=True,
            trailer_info=trailer_info,
            movie=movie,
            multi_videos=multi_videos,
            audience_reaction=audience_reaction,
        )

        # 4. Determine initial Post status
        if quality_status == QualityStatusEnum.PASS:
            post_status = PostStatusEnum.GENERATED.value
        elif quality_status == QualityStatusEnum.REVIEW:
            post_status = PostStatusEnum.REVIEW.value
        else:
            post_status = PostStatusEnum.FAILED.value

        slug = generate_slug(article.slug_hint or article.title)

        post = None
        if save_post:
            post = Post(
                movie_id=movie.id,
                external_id=str(movie.external_id) if movie.external_id else None,
                site_id=2,
                vertical="MOVIE",
                title=article.title,
                slug=slug,
                article_json=article.model_dump_json(),
                rendered_content=rendered_html,
                excerpt=article.excerpt,
                seo_title=article.seo_title,
                meta_description=article.meta_description,
                ai_requested_provider=gen_result.requested_provider,
                ai_used_provider=gen_result.used_provider,
                fallback_used=gen_result.fallback_used,
                prompt_version=gen_result.prompt_version,
                quality_status=quality_status.value,
                status=post_status,
                failure_reason=", ".join(issues) if issues else None
            )
            db.add(post)
            db.commit()
            db.refresh(post)

        return post, gen_result, quality_status, issues
