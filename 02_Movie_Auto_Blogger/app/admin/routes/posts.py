import json
import os
from typing import Any, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import (
    AdminUser,
    AutomationEvent,
    AutomationRun,
    InterviewSessionModel,
    Movie,
    Post,
    PostStatusEnum,
    QualityStatusEnum,
    Site,
)
from app.database.session import get_db
from app.publishers.base import PostStatus
from app.scheduler.jobs import run_automation_pipeline
from app.scheduler.scheduler import get_scheduler
from app.services.candidate_service import CandidateService
from app.services.movie_service import MovieService
from app.services.opportunity_service import OpportunityService
from app.services.publishing_service import PublishingService
from app.services.settings_service import SettingsService
from app.utils.logging import get_logger
from app.utils.security import verify_password
from app.admin.common import templates, get_current_admin

logger = get_logger("admin")
router = APIRouter()


@router.get("/test-generate", response_class=HTMLResponse)
async def test_generate_page(
    request: Request,
    movie_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Manual Test Mode: Choose candidate, generate article, and preview safely without publishing."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    # 1. Fetch available candidates list for the dropdown
    all_candidates = (
        db.query(Movie)
        .order_by(Movie.candidate_score.desc().nullslast())
        .limit(30)
        .all()
    )

    if not all_candidates:
        candidate_service = CandidateService()
        all_candidates = await candidate_service.collect_score_and_persist(db, pool_size=20)

    # 2. Pick the requested candidate or the top candidate without a post
    candidate = None
    if movie_id:
        candidate = db.query(Movie).filter(Movie.id == movie_id).first()

    if not candidate:
        # Find highest scored candidate that hasn't been generated yet
        generated_movie_ids = db.query(Post.movie_id).filter(Post.status != PostStatusEnum.FAILED.value).subquery()
        candidate = (
            db.query(Movie)
            .filter(Movie.id.notin_(generated_movie_ids))
            .order_by(Movie.candidate_score.desc().nullslast())
            .first()
        )

    if not candidate and all_candidates:
        candidate = all_candidates[0]

    if not candidate:
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "request": request,
                "current_user": current_user,
                "overview": get_settings().get_masked_overview(),
                "counts": {},
                "recent_posts": [],
                "scheduler_status": get_scheduler().get_status(),
                "error": "영화 후보군을 찾을 수 없습니다. TMDB API 설정을 먼저 확인하세요."
            }
        )

    # Enrich details if needed
    movie_service = MovieService()
    candidate = await movie_service.enrich_movie_details(db, candidate)

    # Fetch YouTube trailer
    from app.services.trailer_service import TrailerService
    trailer_service = TrailerService()
    trailer_info = await trailer_service.get_trailer_info(
        movie_title=candidate.title,
        external_id=candidate.external_id
    )

    # Generate article (save_post=True so post exists for draft publishing)
    from app.services.article_service import ArticleService
    article_service = ArticleService()
    post, gen_result, quality_status, issues = await article_service.generate_article_for_movie(
        db, candidate, save_post=True
    )

    if not gen_result.success or not gen_result.article:
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "request": request,
                "current_user": current_user,
                "overview": get_settings().get_masked_overview(),
                "counts": {},
                "recent_posts": [],
                "scheduler_status": get_scheduler().get_status(),
                "error": f"AI 글 생성 실패 ({gen_result.failure_category}): {gen_result.error_message}"
            }
        )

    # Render HTML with trailer included
    rendered_html = article_service.render_html(
        article=gen_result.article,
        movie_title=candidate.title,
        poster_url=candidate.poster_reference,
        media_enabled=True,
        trailer_info=trailer_info,
        movie=candidate
    )

    # Update the post's rendered_content with the full HTML
    if post:
        post.rendered_content = rendered_html
        db.commit()

    return templates.TemplateResponse(
        request=request,
        name="preview.html",
        context={
            "request": request,
            "current_user": current_user,
            "movie": candidate,
            "all_candidates": all_candidates,
            "article": gen_result.article,
            "post": post,
            "gen_result": gen_result,
            "quality_status": quality_status,
            "issues": issues,
            "rendered_content": rendered_html,
            "trailer_info": trailer_info
        }
    )



@router.get("/posts", response_class=HTMLResponse)
async def posts_page(
    request: Request,
    filter_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Render full post list with status filter."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    query = db.query(Post).order_by(Post.created_at.desc())
    if filter_status and filter_status.upper() != "ALL":
        query = query.filter(Post.status == filter_status.upper())

    posts = query.limit(100).all()

    return templates.TemplateResponse(
        request=request,
        name="posts.html",
        context={
            "request": request,
            "current_user": current_user,
            "posts": posts,
            "filter_status": filter_status or "ALL",
        }
    )



@router.get("/posts/{post_id}/preview", response_class=HTMLResponse)
async def preview_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Preview rendered post HTML and metadata."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    return templates.TemplateResponse(
        request=request,
        name="preview_post.html",
        context={
            "request": request,
            "current_user": current_user,
            "post": post,
        }
    )

