import json
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, List, Dict
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
from app.services.opportunity_service import OpportunityService, TravelOpportunityService, UniversalOpportunityService
from app.services.publishing_service import PublishingService
from app.services.settings_service import SettingsService
from app.utils.logging import get_logger
from app.utils.security import verify_password
from app.admin.common import templates, get_current_admin

logger = get_logger("admin")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    site_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Render Super Auto Blogger v3 Multi-Site Command Center Dashboard."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    settings = get_settings()
    overview = settings.get_masked_overview()
    db_settings = SettingsService().get_all_settings(db)
    overview["auto_publish"] = db_settings.get("auto_publish", settings.AUTO_PUBLISH)
    scheduler = get_scheduler()

    # Query all registered sites
    sites = db.query(Site).order_by(Site.id.asc()).all()

    # Calculate post counts
    status_counts = dict(
        db.query(Post.status, func.count(Post.id)).group_by(Post.status).all()
    )

    counts = {
        "generated": status_counts.get(PostStatusEnum.GENERATED.value, 0),
        "scheduled": status_counts.get(PostStatusEnum.SCHEDULED.value, 0),
        "published": status_counts.get(PostStatusEnum.PUBLISHED.value, 0),
        "failed": status_counts.get(PostStatusEnum.FAILED.value, 0),
        "review": status_counts.get(PostStatusEnum.REVIEW.value, 0),
        "total_sites": len(sites)
    }

    # Meta definitions for vertical aesthetics
    vertical_meta = {
        "TRAVEL": {"name": "여행 & 명소", "icon": "bi-airplane-fill", "color": "info", "border": "border-info"},
        "MOVIE": {"name": "영화 & OTT", "icon": "bi-film", "color": "primary", "border": "border-primary"},
        "PRODUCT": {"name": "상품 & 스펙", "icon": "bi-cart4", "color": "warning", "border": "border-warning"},
        "ENTERTAINMENT": {"name": "연예 & K-컬처", "icon": "bi-stars", "color": "danger", "border": "border-danger"},
        "WELFARE": {"name": "복지 & 지원금", "icon": "bi-gift-fill", "color": "success", "border": "border-success"},
        "NEWS": {"name": "뉴스 브리핑", "icon": "bi-newspaper", "color": "dark", "border": "border-dark"}
    }

    # Enrich each site
    site_cards = []
    for s in sites:
        v_key = (s.vertical or "MOVIE").upper()
        meta = vertical_meta.get(v_key, {"name": v_key, "icon": "bi-window", "color": "secondary", "border": "border-secondary"})
        is_travel_hub = "travelpick24" in (s.site_url or "").lower()

        # Posts stats for this vertical/site
        site_posts_q = db.query(Post).filter(
            (Post.vertical == v_key) | (Post.vertical == None if v_key == "MOVIE" else False)
        )
        total_p = site_posts_q.count()
        sched_p = site_posts_q.filter(Post.status == PostStatusEnum.SCHEDULED.value).count()
        pub_p = site_posts_q.filter(Post.status == PostStatusEnum.PUBLISHED.value).count()

        site_cards.append({
            "id": s.id,
            "name": s.name,
            "site_url": s.site_url,
            "clean_domain": s.site_url.replace("https://", "").replace("http://", "").rstrip("/"),
            "vertical": v_key,
            "vertical_name": meta["name"],
            "icon": meta["icon"],
            "badge_color": meta["color"],
            "border_class": meta["border"],
            "is_active": s.is_active,
            "hub": "TRAVEL_HUB" if is_travel_hub else "TREND_HUB",
            "hub_label": "트래블픽 허브" if is_travel_hub else "트렌드스팟 허브",
            "total_posts": total_p,
            "scheduled_posts": sched_p,
            "published_posts": pub_p,
            "ssl_status": "VALID",
            "is_isolated_adsense": True if "travelpick24" in (s.site_url or "") and s.id != 1 else False
        })

    # Determine Focused Site
    focused_site = None
    if site_id:
        focused_site = next((s for s in site_cards if s["id"] == site_id), None)
    if not focused_site and site_cards:
        focused_site = site_cards[0]

    # Fetch Opportunities & Recent Posts for Focused Site
    focused_opportunities = []
    focused_recent_posts = []

    if focused_site:
        v_focused = focused_site["vertical"]
        focused_opportunities = await UniversalOpportunityService.get_opportunities_for_vertical(
            v_focused, db, top_n=5
        )

        focused_recent_posts = (
            db.query(Post)
            .filter(
                (Post.vertical == v_focused) | (Post.vertical == None if v_focused == "MOVIE" else False)
            )
            .order_by(Post.created_at.desc())
            .limit(10)
            .all()
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_user": current_user,
            "overview": overview,
            "counts": counts,
            "site_cards": site_cards,
            "focused_site": focused_site,
            "focused_opportunities": focused_opportunities,
            "focused_recent_posts": focused_recent_posts,
            "scheduler_status": scheduler.get_status(),
        }
    )
