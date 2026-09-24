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

