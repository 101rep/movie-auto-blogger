"""Movie Content Module implementing BaseContentModule via existing production services."""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.base_module import BaseContentModule, CandidateItem
from app.core.verticals import VerticalType, VerticalStatus
from app.collectors.tmdb import TMDBMovieProvider
from app.services.candidate_service import CandidateService
from app.services.movie_service import MovieService
from app.services.article_service import ArticleService
from app.services.trailer_service import TrailerService
from app.utils.logging import get_logger

logger = get_logger("movie_module")


class MovieModule(BaseContentModule):
    """Production implementation of the Movie vertical module."""

    def __init__(self):
        self.tmdb = TMDBMovieProvider()
        self.candidate_service = CandidateService(collector=self.tmdb)
        self.movie_service = MovieService(collector=self.tmdb)
        self.article_service = ArticleService()
        self.trailer_service = TrailerService(tmdb_provider=self.tmdb)

    @property
    def vertical(self) -> VerticalType:
        return VerticalType.MOVIE

    @property
    def status(self) -> VerticalStatus:
        return VerticalStatus.PRODUCTION

    async def health_check(self) -> Dict[str, Any]:
        """Check TMDB API connectivity and credentials."""
        return await self.tmdb.health_check()

    async def collect_candidates(self, db: Session, limit: int = 10) -> List[CandidateItem]:
        """Collect, deduplicate, score, and persist movie candidates."""
        movies = await self.candidate_service.collect_score_and_persist(db, pool_size=limit)
        items = []
        for m in movies:
            items.append(
                CandidateItem(
                    external_id=str(m.external_id),
                    vertical=VerticalType.MOVIE,
                    title=m.title,
                    original_title=m.original_title,
                    summary=m.overview,
                    source_attribution="TMDB (The Movie Database)",
                    score=m.candidate_score or 0.0,
                    score_breakdown={
                        "popularity": m.popularity or 0.0,
                        "vote_average": m.vote_average or 0.0
                    },
                    raw_data={
                        "id": m.id,
                        "release_date": m.release_date,
                        "runtime": m.runtime
                    }
                )
            )
        return items

    async def enrich_item(self, db: Session, external_id: str) -> Dict[str, Any]:
        """Fetch full cast, crew, and official YouTube trailer for a movie."""
        from sqlalchemy import select
        from app.database.models import Movie
        import json

        movie = await self.candidate_service.get_by_external_id(db, external_id)
        if not movie:
            stmt = select(Movie).where(Movie.external_id == str(external_id))
            movie = db.execute(stmt).scalar_one_or_none()

        if not movie:
            detailed = await self.candidate_service.collector.get_movie_details(str(external_id))
            if not detailed:
                raise ValueError(f"영화 external_id={external_id}를 찾을 수 없습니다.")
            movie = Movie(
                title=detailed.title,
                original_title=detailed.original_title,
                overview=detailed.overview,
                release_date=detailed.release_date,
                external_id=str(detailed.external_id),
                source=detailed.source,
                director=detailed.director,
                runtime=detailed.runtime,
                vote_average=detailed.vote_average,
                vote_count=detailed.vote_count,
                poster_url=detailed.poster_url,
                backdrop_url=detailed.backdrop_url,
                genres_json=json.dumps(detailed.genres, ensure_ascii=False) if detailed.genres else None,
                cast_json=json.dumps(detailed.major_cast, ensure_ascii=False) if detailed.major_cast else None,
            )
            db.add(movie)
            db.commit()
            db.refresh(movie)

        movie = await self.movie_service.enrich_movie_details(db, movie)
        trailer = await self.trailer_service.get_trailer_info(movie.title, external_id=movie.external_id)

        return {
            "movie": movie,
            "trailer": trailer
        }

    async def generate_content(self, db: Session, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate full E-E-A-T article using ArticleService."""
        movie = enriched_data["movie"]
        post, gen_result, quality_status, issues = await self.article_service.generate_article_for_movie(
            db, movie, save_post=False
        )
        article_obj = gen_result.article if (gen_result and hasattr(gen_result, "article") and gen_result.article) else None
        p_url = getattr(movie, "poster_reference", None) or getattr(movie, "poster_url", None)
        return {
            "article": article_obj,
            "movie_title": movie.title,
            "poster_url": p_url,
            "trailer_info": enriched_data.get("trailer"),
            "movie": movie,
            "post": post,
            "result": gen_result,
            "quality_status": quality_status,
            "issues": issues
        }

    def render_html(self, content_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Render full HTML with trailer, badges, and E-E-A-T styling."""
        article = content_data.get("article")
        movie_title = content_data.get("movie_title", "")
        poster_url = content_data.get("poster_url")
        trailer_info = content_data.get("trailer_info")
        movie = content_data.get("movie")

        return self.article_service.render_html(
            article=article,
            movie_title=movie_title,
            poster_url=poster_url,
            trailer_info=trailer_info,
            movie=movie
        )

    def extract_metadata(
        self,
        gen_result: Dict[str, Any],
        enriched_data: Dict[str, Any],
        candidate: CandidateItem
    ) -> Dict[str, Any]:
        art = gen_result.get("article")
        movie = gen_result.get("movie") or enriched_data.get("movie")
        title = candidate.title
        excerpt = candidate.summary or candidate.title
        seo_title = title
        meta_description = excerpt
        tags = ["영화", "영화추천", "영화리뷰"]
        article_json_str = "{}"
        if art:
            title = art.title
            excerpt = art.excerpt
            seo_title = art.seo_title
            meta_description = art.meta_description
            tags = art.tags or tags
            article_json_str = art.model_dump_json() if hasattr(art, "model_dump_json") else "{}"

        p_url = gen_result.get("poster_url") or (getattr(movie, "poster_reference", None) if movie else None) or (getattr(movie, "poster_url", None) if movie else None)
        return {
            "title": title,
            "excerpt": excerpt,
            "seo_title": seo_title,
            "meta_description": meta_description,
            "tags": tags,
            "featured_image_url": p_url,
            "article_json_str": article_json_str
        }

    def get_core_entities(self, text: str) -> List[str]:
        return [text.strip()]

