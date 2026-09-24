import json
import os
from typing import Any, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
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

logger = get_logger("admin")
router = APIRouter(prefix="/admin", tags=["admin"])

# Set up Jinja2 templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

STATUS_KOREAN = {
    "COLLECTED": "영화 수집",
    "GENERATING": "AI 작성중",
    "GENERATED": "생성 완료",
    "APPROVED": "초안 완료",
    "SCHEDULED": "예약 대기",
    "PUBLISHED": "발행 완료",
    "REVIEW": "검토 필요",
    "FAILED": "생성 실패",
    "DRAFT": "임시글",
}

QUALITY_KOREAN = {
    "PASS": "검수 통과",
    "REVIEW": "검토 필요",
    "FAIL": "기준 미달",
}

def status_to_korean(val: Optional[str]) -> str:
    if not val:
        return "-"
    return STATUS_KOREAN.get(str(val).upper(), str(val))

def quality_to_korean(val: Optional[str]) -> str:
    if not val:
        return "-"
    return QUALITY_KOREAN.get(str(val).upper(), str(val))

RUN_STATUS_KOREAN = {
    "COMPLETED": "완료",
    "RUNNING": "실행 중",
    "FAILED": "실패",
}

def run_status_to_korean(val: Optional[str]) -> str:
    if not val:
        return "-"
    return RUN_STATUS_KOREAN.get(str(val).upper(), str(val))

def to_kst_datetime(val: Optional[Any]) -> str:
    """Convert UTC datetime to clean KST datetime string (YYYY-MM-DD HH:MM)."""
    if not val:
        return "-"
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime, timezone
        kst_tz = ZoneInfo("Asia/Seoul")
        if isinstance(val, datetime):
            if val.tzinfo is None:
                val = val.replace(tzinfo=timezone.utc)
            return val.astimezone(kst_tz).strftime("%m-%d %H:%M")
        return str(val)[:16]
    except Exception:
        return str(val)[:16]

templates.env.filters["ko_status"] = status_to_korean
templates.env.filters["ko_quality"] = quality_to_korean
templates.env.filters["ko_run_status"] = run_status_to_korean
templates.env.filters["kst_datetime"] = to_kst_datetime


def get_current_admin(request: Request) -> Optional[str]:

    """Extract authenticated admin username from session cookie."""
    return request.session.get("admin_user")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render admin login page."""
    if get_current_admin(request):
        return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )


@router.post("/login", response_class=HTMLResponse)
async def process_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Authenticate admin user and establish session."""
    user = db.execute(
        select(AdminUser).where(AdminUser.username == username.strip(), AdminUser.is_active == True)
    ).scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Failed admin login attempt for username: %s", username)
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "아이디 또는 비밀번호가 일치하지 않습니다."},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Establish session
    request.session["admin_user"] = user.username
    logger.info("Admin login successful for username: %s", user.username)
    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
async def logout(request: Request):
    """Terminate admin session."""
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Render primary admin dashboard shell with real system status and counts."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = get_settings()
    overview = settings.get_masked_overview()
    db_settings = SettingsService().get_all_settings(db)
    overview["auto_publish"] = db_settings.get("auto_publish", settings.AUTO_PUBLISH)
    scheduler = get_scheduler()


    # Query real counts from database
    status_counts = dict(
        db.query(Post.status, func.count(Post.id)).group_by(Post.status).all()
    )

    counts = {
        "generated": status_counts.get(PostStatusEnum.GENERATED.value, 0),
        "scheduled": status_counts.get(PostStatusEnum.SCHEDULED.value, 0),
        "published": status_counts.get(PostStatusEnum.PUBLISHED.value, 0),
        "failed": status_counts.get(PostStatusEnum.FAILED.value, 0),
        "review": status_counts.get(PostStatusEnum.REVIEW.value, 0),
    }

    recent_movie_posts = (
        db.query(Post)
        .filter((Post.vertical == "MOVIE") | (Post.vertical == None))
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )

    recent_travel_posts = (
        db.query(Post)
        .filter(Post.vertical == "TRAVEL")
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )

    recent_posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )

    # Opportunity Engine Recommendations (Movie & Travel)
    opportunity_service = OpportunityService()
    try:
        top_opportunities = await opportunity_service.get_top_opportunities(db, pool_size=25, top_n=5)
    except Exception as oe:
        logger.warning("Failed to fetch top opportunities: %s", str(oe))
        top_opportunities = []

    from app.services.opportunity_service import TravelOpportunityService
    travel_opp_service = TravelOpportunityService()
    try:
        top_travel_opportunities = travel_opp_service.get_top_opportunities(db, top_n=5)
    except Exception as toe:
        logger.warning("Failed to fetch top travel opportunities: %s", str(toe))
        top_travel_opportunities = []

    movie_site = db.query(Site).filter(Site.vertical == "MOVIE").first()
    travel_site = db.query(Site).filter(Site.vertical == "TRAVEL").first()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_user": current_user,
            "overview": overview,
            "movie_site": movie_site,
            "travel_site": travel_site,
            "counts": counts,
            "recent_posts": recent_posts,
            "recent_movie_posts": recent_movie_posts,
            "recent_travel_posts": recent_travel_posts,
            "top_opportunities": top_opportunities,
            "top_travel_opportunities": top_travel_opportunities,
            "scheduler_status": scheduler.get_status(),
        }
    )


@router.post("/api/test-movie-api")
async def api_test_movie_connection(request: Request):
    """Test Movie API (TMDB) connectivity and authentication."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    movie_service = MovieService()
    result = await movie_service.test_connection()
    return result


@router.post("/api/test-openai")
async def api_test_openai_connection(request: Request):
    """Test OpenAI API connectivity and credentials."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.ai.openai_provider import OpenAIArticleProvider
    provider = OpenAIArticleProvider()
    return await provider.health_check()


@router.post("/api/test-gemini")
async def api_test_gemini_connection(request: Request):
    """Test Google Gemini API connectivity and credentials."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.ai.gemini_provider import GeminiArticleProvider
    provider = GeminiArticleProvider()
    return await provider.health_check()


@router.post("/api/test-wordpress")
async def api_test_wordpress_connection(request: Request):
    """Test WordPress REST API connectivity and credentials."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.publishers.wordpress import WordPressPublisher
    publisher = WordPressPublisher()
    return await publisher.health_check()


@router.post("/api/send-draft/{post_id}")
async def api_send_draft_to_wordpress(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Send an existing post to WordPress as a draft."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    from app.publishers.base import PostStatus
    from app.services.publishing_service import PublishingService
    pub_service = PublishingService()
    result = await pub_service.publish_article(db, post, target_status=PostStatus.DRAFT)
    return {
        "success": result.success,
        "remote_post_id": result.remote_post_id,
        "remote_url": result.remote_url,
        "error_message": result.error_message
    }


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


@router.post("/api/posts/{post_id}/publish-draft")
async def api_publish_post_draft(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Publish a post immediately to WordPress as DRAFT."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    publishing_service = PublishingService()
    result = await publishing_service.publish_article(db, post, target_status=PostStatus.DRAFT)
    return {
        "success": result.success,
        "post_id": result.remote_post_id,
        "url": result.remote_url,
        "error": result.error_message
    }




@router.post("/api/discover-candidates")
async def api_discover_candidates(
    request: Request,
    db: Session = Depends(get_db)
):
    """Trigger on-demand candidate discovery, scoring, and persistence."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    candidate_service = CandidateService()
    movies = await candidate_service.collect_score_and_persist(db)
    return {
        "success": True,
        "count": len(movies),
        "candidates": [
            {
                "id": m.id,
                "title": m.title,
                "score": m.candidate_score,
                "release_date": m.release_date,
                "popularity": m.popularity,
                "vote_average": m.vote_average
            }
            for m in movies
        ]
    }


@router.post("/api/trigger-automation")
async def api_trigger_automation(
    request: Request,
    db: Session = Depends(get_db)
):
    """Trigger the end-to-end automation pipeline immediately."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    try:
        run = await run_automation_pipeline(db, force=True)
        return {
            "success": run.status == "completed",
            "run_uuid": run.run_uuid,
            "status": run.status,
            "summary": run.summary,
            "candidate_count": run.candidate_count,
            "generated_count": run.generated_count,
            "scheduled_count": run.scheduled_count,
            "failed_count": run.failed_count,
        }
    except Exception as e:
        logger.error("Admin trigger-automation error: %s", str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"자동화 실행 실패: {str(e)}")


@router.post("/api/toggle-automation")
async def api_toggle_automation(
    request: Request,
    db: Session = Depends(get_db)
):
    """Toggle AUTO_PUBLISH operational setting on/off."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    service = SettingsService()
    new_state = service.toggle_auto_publish(db)
    return {
        "success": True,
        "auto_publish": new_state,
        "message": f"자동 발행 모드가 {'활성화(ON)' if new_state else '비활성화(OFF)'}되었습니다."
    }


@router.post("/api/publish-now/{post_id}")
async def api_publish_now_to_wordpress(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Publish a post immediately to WordPress."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    pub_service = PublishingService()
    result = await pub_service.publish_article(db, post, target_status=PostStatus.PUBLISH)
    return {
        "success": result.success,
        "remote_post_id": result.remote_post_id,
        "remote_url": result.remote_url,
        "error_message": result.error_message
    }


@router.post("/api/delete-post/{post_id}")
async def api_delete_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a post from local database."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    db.delete(post)
    db.commit()
    return {"success": True, "message": "게시글이 삭제되었습니다."}


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Render operational settings page."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    service = SettingsService()
    current_settings = service.get_all_settings(db)
    overview = get_settings().get_masked_overview()

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "request": request,
            "current_user": current_user,
            "settings": current_settings,
            "overview": overview,
            "message": request.query_params.get("msg"),
            "error": request.query_params.get("err"),
        }
    )


@router.post("/settings", response_class=HTMLResponse)
async def update_settings_action(
    request: Request,
    db: Session = Depends(get_db),
    daily_post_count: int = Form(4),
    candidate_pool_size: int = Form(30),
    publish_time_1: str = Form("08:00"),
    publish_time_2: str = Form("12:30"),
    publish_time_3: str = Form("18:00"),
    publish_time_4: str = Form("22:00"),
    primary_ai: str = Form("openai"),
    fallback_ai: str = Form("gemini"),
    openai_model: str = Form("gpt-4o-mini"),
    gemini_model: str = Form("gemini-1.5-flash"),
    auto_publish: Optional[str] = Form(None),
    media_upload_enabled: Optional[str] = Form(None),
    wordpress_url: Optional[str] = Form(None),
    wordpress_username: Optional[str] = Form(None),
    wordpress_app_password: Optional[str] = Form(None),
):
    """Update operational settings from HTML form."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    service = SettingsService()
    try:
        service.update_settings(
            db,
            {
                "daily_post_count": daily_post_count,
                "candidate_pool_size": candidate_pool_size,
                "publish_time_1": publish_time_1,
                "publish_time_2": publish_time_2,
                "publish_time_3": publish_time_3,
                "publish_time_4": publish_time_4,
                "primary_ai": primary_ai,
                "fallback_ai": fallback_ai,
                "openai_model": openai_model,
                "gemini_model": gemini_model,
                "auto_publish": auto_publish is not None,
                "media_upload_enabled": media_upload_enabled is not None,
                "wordpress_url": wordpress_url or "",
                "wordpress_username": wordpress_username or "",
                "wordpress_app_password": wordpress_app_password or "",
            }
        )
        return RedirectResponse(
            url="/admin/settings?msg=설정이+성공적으로+저장되었습니다.",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        logger.warning("Failed to update settings: %s", str(e))
        return RedirectResponse(
            url=f"/admin/settings?err={str(e)}",
            status_code=status.HTTP_302_FOUND
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


@router.post("/api/posts/{post_id}/refresh")
async def api_refresh_post(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Re-enrich movie with latest Naver rating and re-render article HTML."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or not post.movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글 또는 영화 정보를 찾을 수 없습니다.")

    # 1. Fetch fresh Naver rating
    try:
        from app.services.naver_rating_service import NaverRatingService
        naver_data = await NaverRatingService.fetch_rating(post.movie.title)
        if naver_data:
            post.movie.naver_rating = naver_data.rating
            post.movie.naver_rating_type = naver_data.rating_type
            post.movie.naver_vote_count = naver_data.vote_count_str
    except Exception as e:
        logger.warning("Failed refreshing Naver rating for post %d: %s", post_id, str(e))

    # 2. Re-render HTML with new rating and spec badges
    if post.article_json:
        try:
            import json
            from app.ai.schemas import ArticleOutput
            from app.services.article_service import ArticleService
            article_data = json.loads(post.article_json)
            article_obj = ArticleOutput.model_validate(article_data)
            article_svc = ArticleService()

            trailer_info = None
            try:
                trailer_info = await article_svc.trailer_service.get_trailer_info(
                    movie_title=post.movie.title,
                    external_id=post.movie.external_id
                )
            except Exception:
                pass

            post.rendered_content = article_svc.render_html(
                article=article_obj,
                movie_title=post.movie.title,
                poster_url=post.movie.poster_reference,
                media_enabled=True,
                trailer_info=trailer_info,
                movie=post.movie
            )
        except Exception as err:
            logger.error("Error re-rendering post HTML: %s", str(err))

    db.commit()
    db.refresh(post)
    return {
        "success": True,
        "naver_rating": post.movie.naver_rating,
        "naver_vote_count": post.movie.naver_vote_count
    }


@router.get("/runs", response_class=HTMLResponse)
async def runs_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Render automation runs history and execution events."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    runs = db.query(AutomationRun).order_by(AutomationRun.started_at.desc()).limit(30).all()

    return templates.TemplateResponse(
        request=request,
        name="runs.html",
        context={
            "request": request,
            "current_user": current_user,
            "runs": runs,
        }
    )


@router.get("/help", response_class=HTMLResponse)
async def help_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Render comprehensive Operations, Infrastructure & Security Guide Hub."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = get_settings()
    overview = settings.get_masked_overview()
    db_settings = SettingsService().get_all_settings(db)
    overview["auto_publish"] = db_settings.get("auto_publish", settings.AUTO_PUBLISH)

    server_info = {
        "domain": "trendspot24.com",
        "site_url": "https://trendspot24.com",
        "wp_admin_url": "https://trendspot24.com/wp-admin",
        "wp_custom_css_url": "https://trendspot24.com/wp-admin/customize.php?autofocus[section]=custom_css",
        "wp_posts_url": "https://trendspot24.com/wp-admin/edit.php",
        "wp_plugin_url": "https://trendspot24.com/wp-admin/plugins.php",
        "hosting_provider": "Cloudways (DigitalOcean)",
        "hosting_url": "https://platform.cloudways.com/",
        "server_ip": "139.59.125.237",
        "server_region": "싱가포르 (Singapore Data Center)",
        "web_server": "Nginx + Varnish 캐시 + PHP 8.2 + MariaDB",
        "google_search_console_url": "https://search.google.com/search-console",
        "naver_search_advisor_url": "https://searchadvisor.naver.com/",
        "bing_webmasters_url": "https://www.bing.com/webmasters",
        "sitemap_url": "https://trendspot24.com/wp-sitemap.xml",
        "rss_feed_url": "https://trendspot24.com/feed",
        "openai_platform_url": "https://platform.openai.com/usage",
        "google_ai_studio_url": "https://aistudio.google.com/",
        "tmdb_developer_url": "https://www.themoviedb.org/settings/api",
        "adsense_url": "https://adsense.google.com/",
    }

    return templates.TemplateResponse(
        request=request,
        name="help.html",
        context={
            "request": request,
            "current_user": current_user,
            "overview": overview,
            "settings": settings,
            "server_info": server_info,
        }
    )


# ==========================================
# Multi-Site & Multi-Vertical Management Endpoints
# ==========================================

@router.get("/sites", response_class=HTMLResponse)
async def list_sites_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Render multi-site and multi-vertical publishing dashboard."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    from app.core.registry import get_platform_registry
    registry = get_platform_registry()

    sites = db.execute(select(Site).order_by(Site.id.asc())).scalars().all()
    verticals = registry.list_verticals()
    providers = registry.list_providers()

    # Flash messages in session
    success_msg = request.session.pop("flash_success", None)
    error_msg = request.session.pop("flash_error", None)

    settings = get_settings()

    return templates.TemplateResponse(
        request=request,
        name="sites.html",
        context={
            "request": request,
            "current_user": current_user,
            "settings": settings,
            "sites": sites,
            "verticals": verticals,
            "providers": providers,
            "success_msg": success_msg,
            "error_msg": error_msg
        }
    )


@router.post("/sites/create")
async def create_site(
    request: Request,
    name: str = Form(...),
    site_url: str = Form(...),
    vertical: str = Form("MOVIE"),
    wp_username: Optional[str] = Form(None),
    wp_application_password: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Register a new WordPress target domain and vertical binding."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    clean_url = site_url.strip().rstrip("/")
    if not clean_url.startswith("http"):
        clean_url = f"https://{clean_url}"

    new_site = Site(
        name=name.strip(),
        site_url=clean_url,
        vertical=vertical.strip().upper(),
        wp_username=wp_username.strip() if wp_username else None,
        wp_application_password=wp_application_password.replace(" ", "").strip() if wp_application_password else None,
        is_active=True
    )
    db.add(new_site)
    db.commit()

    request.session["flash_success"] = f"새 사이트 '{new_site.name}' ({new_site.site_url})가 성공적으로 등록되었습니다!"
    return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)


@router.post("/sites/{site_id}/test")
async def test_site_connection(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Test live WordPress REST API connectivity for a specific site."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    site = db.get(Site, site_id)
    if not site:
        request.session["flash_error"] = f"사이트 ID {site_id}를 찾을 수 없습니다."
        return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)

    from app.publishers.wordpress import WordPressPublisher
    settings = get_settings()

    publisher = WordPressPublisher(
        site_url=site.site_url,
        username=site.wp_username or settings.WORDPRESS_USERNAME,
        app_password=site.wp_application_password or settings.WORDPRESS_APPLICATION_PASSWORD
    )

    health = await publisher.health_check()
    if health.get("success"):
        request.session["flash_success"] = f"[{site.name}] 연결 성공: {health.get('message')}"
    else:
        request.session["flash_error"] = f"[{site.name}] 연결 실패: {health.get('message')}"

    return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)


@router.post("/sites/{site_id}/toggle")
async def toggle_site_status(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Toggle site active status."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    site = db.get(Site, site_id)
    if site:
        site.is_active = not site.is_active
        db.commit()
        state = "활성화" if site.is_active else "비활성화"
        request.session["flash_success"] = f"[{site.name}] 사이트가 {state}되었습니다."

    return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)


@router.post("/sites/{site_id}/delete")
async def delete_site(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a site from platform configuration."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    site = db.get(Site, site_id)
    if site:
        name = site.name
        db.delete(site)
        db.commit()
        request.session["flash_success"] = f"'{name}' 사이트가 삭제되었습니다."

    return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)


@router.post("/verticals/trigger")
async def trigger_vertical_action(
    request: Request,
    vertical_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """Trigger candidate collection and test article generation for a vertical."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    from app.core.registry import get_platform_registry
    from app.core.verticals import VerticalType

    try:
        v_enum = VerticalType(vertical_type.upper())
    except ValueError:
        request.session["flash_error"] = f"알 수 없는 버티컬 타입입니다: {vertical_type}"
        return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)

    registry = get_platform_registry()
    mod = registry.get_module(v_enum)
    if not mod:
        request.session["flash_error"] = f"{v_enum.value} 모듈이 등록되어 있지 않습니다."
        return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)

    try:
        candidates = await mod.collect_candidates(db, limit=3)
        if not candidates:
            request.session["flash_error"] = f"{v_enum.value} 수집 후보가 없습니다."
            return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)

        # Generate for first candidate
        first = candidates[0]
        enriched = await mod.enrich_item(db, first.external_id)
        gen = await mod.generate_content(db, enriched)

        rendered_html = ""
        if v_enum == VerticalType.WELFARE:
            rendered_html = mod.render_html(gen)
            article_obj = gen.get("welfare_article")
            title = article_obj.title if article_obj else first.title
            excerpt = article_obj.excerpt if article_obj else first.summary
            article_json_str = article_obj.model_dump_json() if article_obj else "{}"
        elif v_enum == VerticalType.ENTERTAINMENT:
            rendered_html = mod.render_html(gen)
            article_obj = gen.get("entertainment_article")
            title = article_obj.title if article_obj else first.title
            excerpt = article_obj.excerpt if article_obj else first.summary
            article_json_str = article_obj.model_dump_json() if article_obj else "{}"
        elif v_enum == VerticalType.TRAVEL:
            rendered_html = mod.render_html(gen)
            article_obj = gen.get("travel_article")
            title = article_obj.title if article_obj else first.title
            excerpt = article_obj.excerpt if article_obj else first.summary
            article_json_str = article_obj.model_dump_json() if article_obj else "{}"
        else:
            title = first.title
            excerpt = first.summary
            article_json_str = "{}"

        # Bind to active site of this vertical if available
        site = db.execute(
            select(Site).where(Site.vertical == v_enum.value, Site.is_active == True)
        ).scalar_one_or_none()

        post = Post(
            title=title,
            slug=f"{v_enum.value.lower()}-{first.external_id.lower()}",
            rendered_content=rendered_html,
            excerpt=excerpt,
            seo_title=title,
            meta_description=excerpt,
            vertical=v_enum.value,
            site_id=site.id if site else None,
            status=PostStatusEnum.APPROVED.value,
            quality_status=QualityStatusEnum.PASS.value,
            article_json=article_json_str
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        target_name = f"'{site.name}' 사이트" if site else "기본 사이트"
        request.session["flash_success"] = f"[{v_enum.value}] '{title}' 원고가 성공적으로 생성되어 저장되었습니다 (연결: {target_name})!"
    except Exception as e:
        db.rollback()
        logger.error("Vertical trigger failed: %s", str(e), exc_info=True)
        request.session["flash_error"] = f"실행 중 오류 발생: {str(e)}"

    return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)


@router.post("/verticals/trigger-travel-batch", response_class=HTMLResponse)
async def trigger_travel_batch_schedule_action(
    request: Request,
    db: Session = Depends(get_db)
):
    """Trigger 4-post daily travel guide generation & WordPress scheduling on demand."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    from app.scheduler.jobs import run_travel_automation_pipeline

    try:
        run = await run_travel_automation_pipeline(db, force=True)
        request.session["flash_success"] = f"[여행 4개 예약 발행 완료] {run.summary}"
    except Exception as e:
        db.rollback()
        logger.error("Travel batch trigger failed: %s", str(e), exc_info=True)
        request.session["flash_error"] = f"여행 일괄 예약 실행 실패: {str(e)}"

    return RedirectResponse(url="/admin/sites", status_code=status.HTTP_302_FOUND)


# ---------------------------------------------------------------------------
# Experience Studio Endpoints
# ---------------------------------------------------------------------------

@router.get("/experience", response_class=HTMLResponse)
async def experience_studio_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Render Experience Studio for interactive interview and content generation."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    sites = db.query(Site).filter(Site.is_active == True).all()
    settings = get_settings()

    return templates.TemplateResponse(
        request=request,
        name="experience.html",
        context={
            "request": request,
            "current_user": current_user,
            "sites": sites,
            "settings": settings
        }
    )


@router.post("/experience/start")
async def api_experience_start(
    request: Request,
    db: Session = Depends(get_db)
):
    """Start an interview session."""
    current_user = get_current_admin(request)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.services.experience_service import ExperienceService

    data = await request.json()
    topic = (data.get("topic") or "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="취재 주제(topic)를 입력해주세요.")

    main_keyword = data.get("main_keyword")
    exp_service = ExperienceService()
    state, first_question = exp_service.start_interview(topic=topic, main_keyword=main_keyword)

    return {
        "session_id": state.session_id,
        "first_question": first_question,
        "state": state.model_dump()
    }


@router.post("/experience/respond")
async def api_experience_respond(
    request: Request,
    db: Session = Depends(get_db)
):
    """Process user answer and advance interview."""
    current_user = get_current_admin(request)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.services.experience_service import ExperienceService

    data = await request.json()
    session_id = data.get("session_id")
    answer = (data.get("answer") or "").strip()
    if not session_id or not answer:
        raise HTTPException(status_code=400, detail="session_id와 answer가 필요합니다.")

    exp_service = ExperienceService()
    state, next_question, is_completed = exp_service.process_answer(session_id, answer)
    is_drill = bool(state.turns and state.turns[-1].is_drilldown)

    return {
        "session_id": session_id,
        "is_drill_down": is_drill,
        "next_question": next_question,
        "is_complete": is_completed,
        "state": state.model_dump()
    }


@router.post("/experience/outline")
async def api_experience_outline(
    request: Request,
    db: Session = Depends(get_db)
):
    """Generate structured outline from context notebook."""
    current_user = get_current_admin(request)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.services.experience_service import ExperienceService

    data = await request.json()
    session_id = data.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id가 필요합니다.")

    exp_service = ExperienceService()
    outline = exp_service.generate_outline(session_id)

    return {
        "session_id": session_id,
        "outline": outline.model_dump()
    }


@router.post("/experience/draft")
async def api_experience_draft(
    request: Request,
    db: Session = Depends(get_db)
):
    """Generate grounded draft from outline and notebook."""
    current_user = get_current_admin(request)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.services.experience_service import ExperienceService

    data = await request.json()
    session_id = data.get("session_id")
    selected_title = data.get("selected_title")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id가 필요합니다.")

    exp_service = ExperienceService()
    # If selected_title is given, update outline before generating draft
    if selected_title:
        session_model = db.query(InterviewSessionModel).filter_by(session_uuid=session_id).first()
        if session_model and session_model.outline_json:
            outline_dict = json.loads(session_model.outline_json)
            titles = [selected_title] + [t for t in outline_dict.get("titles", []) if t != selected_title]
            outline_dict["titles"] = titles
            session_model.outline_json = json.dumps(outline_dict, ensure_ascii=False)
            db.commit()

    draft, grounding_report = exp_service.generate_draft(session_id)

    return {
        "session_id": session_id,
        "draft": draft.model_dump(),
        "grounding_report": grounding_report.model_dump()
    }


@router.post("/experience/approve")
async def api_experience_approve(
    request: Request,
    db: Session = Depends(get_db)
):
    """Approve draft, persist as Post, and optionally publish to WordPress."""
    current_user = get_current_admin(request)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.services.experience_service import ExperienceService

    data = await request.json()
    session_id = data.get("session_id")
    publish_now = bool(data.get("publish_now", False))
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id가 필요합니다.")

    exp_service = ExperienceService()
    post = exp_service.approve_and_create_post(session_id, db)

    msg = f"게시글이 성공적으로 승인 및 저장되었습니다! (Post ID #{post.id})"

    if publish_now:
        try:
            publishing_service = PublishingService()
            result = await publishing_service.publish_article(db, post, target_status=PostStatus.PUBLISH)
            if result.success:
                msg = f"워드프레스에 즉시 발행 완료되었습니다! (WP ID: {result.remote_post_id})"
            else:
                msg = f"DB 저장은 완료되었으나 워드프레스 발행 중 오류: {result.error_message}"
        except Exception as wp_err:
            logger.error("WordPress publish error in experience studio: %s", str(wp_err))
            msg = f"DB 저장은 완료되었으나 워드프레스 발행 예외 발생: {str(wp_err)}"

    return {
        "success": True,
        "post_id": post.id,
        "status": post.status,
        "message": msg
    }




