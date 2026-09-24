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



@router.post("/api/test-telegram")
async def api_test_telegram_connection(request: Request):
    """Test Telegram Bot API connectivity and send verification message."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    try:
        body = await request.json()
    except Exception:
        body = {}

    settings = get_settings()
    bot_token = body.get("bot_token") or settings.TELEGRAM_BOT_TOKEN or ""
    chat_id = body.get("chat_id") or settings.TELEGRAM_CHAT_ID or ""

    from app.services.telegram_service import TelegramAlertService
    return await TelegramAlertService.test_connection(bot_token, chat_id)



@router.post("/api/detect-telegram-chat-id")
async def api_detect_telegram_chat_id(request: Request):
    """Detect most recent Chat ID from Telegram getUpdates."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    try:
        body = await request.json()
    except Exception:
        body = {}

    settings = get_settings()
    bot_token = body.get("bot_token") or settings.TELEGRAM_BOT_TOKEN or ""

    from app.services.telegram_service import TelegramAlertService
    return await TelegramAlertService.get_recent_updates(bot_token)



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
    vertical: str = "ALL",
    db: Session = Depends(get_db)
):
    """Trigger the end-to-end automation pipeline immediately for MOVIE, TRAVEL, or ALL."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    from app.scheduler.jobs import run_automation_pipeline, run_travel_automation_pipeline
    target_vertical = vertical.strip().upper()

    try:
        if target_vertical == "MOVIE":
            run = await run_automation_pipeline(db, force=True)
            return {
                "success": run.status == "completed",
                "vertical": "MOVIE",
                "run_uuid": run.run_uuid,
                "status": run.status,
                "summary": f"[영화] {run.summary}",
                "candidate_count": run.candidate_count or 0,
                "generated_count": run.generated_count or 0,
                "scheduled_count": run.scheduled_count or 0,
                "failed_count": run.failed_count or 0,
            }
        elif target_vertical == "TRAVEL":
            run = await run_travel_automation_pipeline(db, force=True)
            return {
                "success": run.status == "completed",
                "vertical": "TRAVEL",
                "run_uuid": run.run_uuid,
                "status": run.status,
                "summary": f"[여행] {run.summary}",
                "candidate_count": run.candidate_count or 0,
                "generated_count": run.generated_count or 0,
                "scheduled_count": run.scheduled_count or 0,
                "failed_count": run.failed_count or 0,
            }
        else:
            # ALL: Run universal multi-site automation across all active blogs
            from app.scheduler.multisite_pipeline import run_all_active_sites_pipeline
            run = await run_all_active_sites_pipeline(db, post_count_per_site=settings.DAILY_POST_COUNT, force=True)

            return {
                "success": run.status == "completed",
                "vertical": "ALL",
                "run_uuid": run.run_uuid,
                "status": run.status,
                "summary": run.summary,
                "scheduled_count": run.scheduled_count or 0,
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


@router.get("/api/logs")
async def api_get_live_logs(request: Request, lines: int = 60):
    """Retrieve tail of application log file for real-time dashboard terminal."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    log_file_path = os.path.join(get_settings().LOGS_DIR, "app.log")
    if not os.path.exists(log_file_path):
        return {"success": True, "logs": [f"[{os.path.basename(log_file_path)}] 아직 생성된 로그가 없습니다."]}

    try:
        with open(log_file_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            tail_lines = [line.strip() for line in all_lines[-lines:] if line.strip()]
        return {"success": True, "logs": tail_lines}
    except Exception as e:
        logger.error("Error reading live logs: %s", str(e))
        return {"success": False, "logs": [f"로그 읽기 오류: {str(e)}"]}


@router.post("/api/trigger-site/{site_id}")
async def api_trigger_single_site(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Trigger automated content preparation and scheduling for a specific site."""
    if not get_current_admin(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")

    site = db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사이트를 찾을 수 없습니다.")

    logger.info("Admin manually triggered automation for site [%d] %s (%s)", site.id, site.name, site.vertical)

    try:
        from app.services.single_site_runner import SingleSiteRunner
        result = await SingleSiteRunner.run_site(db, site_id)
        return {
            "success": result["success"],
            "site_id": site.id,
            "site_name": site.name,
            "vertical": site.vertical,
            "summary": result["summary"],
            "published_url": result.get("published_url")
        }
    except Exception as e:
        logger.error("Error executing single-site automation for site %d: %s", site_id, str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"사이트 자동화 실패: {str(e)}")


