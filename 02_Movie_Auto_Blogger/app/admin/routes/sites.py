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

