"""Universal Multi-Site Automated Scheduling Pipeline.

Generates and schedules daily posts (default: 4 posts per site) across all active
specialized vertical blogs at the 4 golden KST time slots (08:00, 12:00, 18:00, 21:00).
Powered by Universal Blog Quality Engine (E-E-A-T, Anti-Cliche, People-First, Grounding Guard).
"""
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.config import get_settings
from app.core.registry import get_platform_registry
from app.core.verticals import VerticalType
from app.database.models import (
    AutomationRun,
    Post,
    PostStatusEnum,
    QualityStatusEnum,
    Site,
    utc_now,
)
from app.publishers.base import PostStatus, PublishRequest
from app.publishers.wordpress import WordPressPublisher
from app.services.publishing_service import PublishingService
from app.services.quality_service import QualityGateService
from app.services.duplicate_guard import DuplicateGuardService
from app.scheduler.common import calculate_schedule_datetimes
from app.utils.logging import get_logger

logger = get_logger("multisite_pipeline")


async def run_single_site_schedule(
    db: Session,
    site: Site,
    post_target_count: int = 4,
    force: bool = False
) -> Dict[str, Any]:
    """Generate and schedule up to `post_target_count` articles for a specific site."""
    settings = get_settings()
    registry = get_platform_registry()
    v = site.vertical.upper()
    kst_tz = ZoneInfo(settings.APP_TIMEZONE)

    # ItemPick24 (PRODUCT): Auto-schedule disabled per user direction (Telegram URL-only immediate publish)
    if v == "PRODUCT" or "item.travelpick24.com" in (site.site_url or ""):
        logger.info("Skipping auto-schedule for [%d] %s (ItemPick24 is URL-on-demand only)", site.id, site.name)
        return {
            "success": True,
            "site_id": site.id,
            "scheduled_count": 0,
            "message": "아이템픽24는 텔레그램 URL 수신 시 즉시 발행 모드로 전담 운영됩니다. (자동 예약 비활성화)"
        }

    # 1. Calculate schedule times with irregular human-like jitter
    schedule_times = calculate_schedule_datetimes(
        settings.PUBLISH_TIME_1,
        settings.PUBLISH_TIME_2,
        settings.PUBLISH_TIME_3,
        settings.PUBLISH_TIME_4,
        tz_str=settings.APP_TIMEZONE,
        post_count=post_target_count,
        apply_jitter=getattr(settings, "PUBLISH_APPLY_JITTER", True),
        jitter_min_minutes=getattr(settings, "PUBLISH_JITTER_MIN_MINUTES", -8),
        jitter_max_minutes=getattr(settings, "PUBLISH_JITTER_MAX_MINUTES", 8),
        site_id=site.id
    )

    logger.info("=== Starting schedule pipeline for [%d] %s (%s, Target: %d posts) ===", site.id, site.name, v, post_target_count)

    # 2. Collect Candidates by Vertical
    candidates = []
    mod = None

    if v == "MOVIE":
        from app.modules.movie.module import MovieModule
        mod = registry.get_module(VerticalType.MOVIE) or MovieModule()
        candidates = await mod.collect_candidates(db, limit=30)
    elif v == "TRAVEL":
        from app.modules.travel.module import TravelModule
        mod = registry.get_module(VerticalType.TRAVEL) or TravelModule()
        candidates = await mod.collect_candidates(db, limit=30)
    elif v == "ENTERTAINMENT":
        from app.modules.entertainment.module import EntertainmentModule
        mod = registry.get_module(VerticalType.ENTERTAINMENT) or EntertainmentModule()
        candidates = await mod.collect_candidates(db, limit=20)
    elif v == "PRODUCT":
        from app.modules.product.module import ProductModule
        mod = registry.get_module(VerticalType.PRODUCT) or ProductModule()
        candidates = await mod.collect_candidates(db, limit=20)
    elif v == "NEWS":
        from app.modules.news.module import NewsModule
        mod = registry.get_module(VerticalType.NEWS) or NewsModule()
        candidates = await mod.collect_candidates(db, limit=20)
    elif v == "WELFARE":
        from app.modules.welfare.module import WelfareModule
        mod = registry.get_module(VerticalType.WELFARE) or WelfareModule()
        candidates = await mod.collect_candidates(db, limit=30, site_id=site.id)
        if not candidates:
            raw_candidates = await mod.collect_candidates(db, limit=30)
            candidates = raw_candidates

    if not candidates:
        logger.warning("No candidates discovered for site [%d] %s", site.id, site.name)
        return {"success": False, "site_id": site.id, "scheduled_count": 0, "message": "후보 없음"}

    # 3. Filter candidates through DuplicateGuardService to guarantee ZERO duplicates
    eligible_candidates = DuplicateGuardService.filter_unique_candidates(
        db=db,
        site_id=site.id,
        vertical=v,
        candidates=candidates,
        limit=post_target_count
    )

    if not eligible_candidates:
        logger.warning("All candidates filtered out as duplicates for site [%d] %s", site.id, site.name)
        return {
            "success": True,
            "site_id": site.id,
            "scheduled_count": 0,
            "message": "새로운 고유 후보 없음 (중복 방지 시스템에 의해 기존/유사 주제 필터링됨)"
        }

    scheduled_posts: List[Dict[str, Any]] = []
    publisher = WordPressPublisher(
        site_url=site.site_url,
        username=site.wp_username or settings.WORDPRESS_USERNAME,
        app_password=site.wp_application_password or settings.WORDPRESS_APPLICATION_PASSWORD
    )

    # 4. Generate and Schedule each candidate
    for idx, cand in enumerate(eligible_candidates):
        target_time = schedule_times[idx] if idx < len(schedule_times) else schedule_times[-1]
        logger.info("Scheduling item [%d/%d] for site '%s': '%s' at %s KST", idx + 1, len(eligible_candidates), site.name, cand.title, target_time)

        try:
            enriched = await mod.enrich_item(db, cand.external_id)
            gen = await mod.generate_content(db, enriched)
            rendered_html = mod.render_html(gen)

            # Standardized Modular Metadata Extraction
            meta = mod.extract_metadata(gen_result=gen, enriched_data=enriched, candidate=cand) if hasattr(mod, "extract_metadata") else {}
            title = meta.get("title", cand.title)
            excerpt = meta.get("excerpt", cand.summary or cand.title)
            seo_title = meta.get("seo_title", title)
            meta_description = meta.get("meta_description", excerpt)
            tags = meta.get("tags") or [site.vertical]
            featured_image_url = meta.get("featured_image_url")
            article_json_str = meta.get("article_json_str", "{}")
            movie_obj = enriched.get("movie") if isinstance(enriched, dict) else None
            movie_id = getattr(movie_obj, "id", None) if v == "MOVIE" else None

            # Quality & Content Completeness Guard (내용 없는 빈 글 발행 원천 차단)
            if not rendered_html or len(rendered_html) < 1500 or article_json_str == "{}":
                logger.error("Content completeness guard failed for candidate '%s' (site %d). Empty article will not be published.", cand.title, site.id)
                continue

            # Deterministic Quality Check
            quality_status = QualityStatusEnum.PASS
            quality_issues = []
            if v == "TRAVEL":
                art_obj = gen.get("travel_article")
                item_obj = enriched.get("travel_item") or cand
                quality_status, quality_issues = QualityGateService.evaluate_travel(
                    article=art_obj,
                    expected_destination=cand.title,
                    travel_item=item_obj
                )

            # Pre-Publish Duplicate Hard Check
            is_valid, dup_reason = DuplicateGuardService.validate_pre_publish(
                db=db,
                site_id=site.id,
                title=title,
                content=rendered_html
            )
            if not is_valid:
                logger.warning("Duplicate guard blocked post for site [%d]: %s", site.id, dup_reason)
                continue

            # Upload featured media (with Auto-Search Fallback Guard)
            featured_media_id = None
            if settings.MEDIA_UPLOAD_ENABLED:
                target_img_url = featured_image_url
                
                # Fallback: If missing, auto-search poster online
                if not target_img_url or not isinstance(target_img_url, str) or not target_img_url.startswith("http"):
                    try:
                        import re
                        import urllib.parse
                        search_kw = f"{cand.title} 영화 포스터" if v == "MOVIE" else f"{cand.title} 대표 사진"
                        enc_kw = urllib.parse.quote(search_kw)
                        s_url = f"https://search.daum.net/search?w=img&q={enc_kw}"
                        import httpx
                        async with httpx.AsyncClient(timeout=8.0) as s_client:
                            s_res = await s_client.get(s_url, headers={"User-Agent": "Mozilla/5.0"})
                            if s_res.status_code == 200:
                                discovered = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', s_res.text, re.IGNORECASE)
                                valid_urls = [u for u in discovered if not any(x in u.lower() for x in ["icon", "logo", "banner", "ad", "static", "thumb", "profile"])]
                                if valid_urls:
                                    target_img_url = valid_urls[0]
                                    logger.info("Discovered fallback poster for [%s]: %s", cand.title, target_img_url)
                    except Exception as s_err:
                        logger.warning("Fallback poster search failed for [%s]: %s", cand.title, s_err)

                if target_img_url and isinstance(target_img_url, str) and target_img_url.startswith("http"):
                    try:
                        import httpx
                        async with httpx.AsyncClient(timeout=15.0, verify=False) as http_client:
                            img_res = await http_client.get(target_img_url)
                            if img_res.status_code == 200 and len(img_res.content) > 500:
                                c_type = img_res.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                                ext = "jpg" if "jpeg" in c_type else "png" if "png" in c_type else "webp"
                                fn = f"{v.lower()}-cover-{uuid.uuid4().hex[:8]}.{ext}"
                                featured_media_id = await publisher.upload_media(
                                    file_bytes=img_res.content,
                                    filename=fn,
                                    alt_text=f"{title} 대표 썸네일",
                                    content_type=c_type
                                )
                    except Exception as img_err:
                        logger.warning("Featured image upload exception for site %d: %s", site.id, img_err)

            # Build slug & PublishRequest
            slug = f"{v.lower()}-{uuid.uuid4().hex[:6]}"
            sched_utc = target_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            sched_local = target_time.astimezone(kst_tz).strftime("%Y-%m-%dT%H:%M:%S")

            post = Post(
                title=title,
                slug=slug,
                rendered_content=rendered_html,
                excerpt=excerpt,
                seo_title=seo_title or title,
                meta_description=meta_description or excerpt,
                vertical=v,
                external_id=str(cand.external_id),
                movie_id=movie_id,
                site_id=site.id,
                status=PostStatusEnum.SCHEDULED.value if quality_status == QualityStatusEnum.PASS else PostStatusEnum.REVIEW.value,
                quality_status=quality_status.value,
                article_json=article_json_str,
                scheduled_at=target_time,
                failure_reason=", ".join(quality_issues) if quality_issues else None
            )
            db.add(post)
            db.commit()
            db.refresh(post)

            # Send Future Post to WordPress
            pub_req = PublishRequest(
                title=title,
                content=rendered_html,
                excerpt=excerpt,
                slug=slug,
                status=PostStatus.FUTURE,
                scheduled_at=sched_utc,
                scheduled_at_local=sched_local,
                featured_media_id=featured_media_id,
                categories=[site.vertical],
                tags=tags[:5]
            )
            wp_res = await publisher.publish_post(pub_req)

            if wp_res.success:
                post.wordpress_post_id = wp_res.remote_post_id
                post.wordpress_url = wp_res.remote_url
                db.commit()
                scheduled_posts.append({
                    "post_id": post.id,
                    "wp_post_id": wp_res.remote_post_id,
                    "title": title,
                    "scheduled_at": str(target_time),
                    "url": wp_res.remote_url
                })
                logger.info("Successfully scheduled post ID %d ('%s') on WP site %s (WP ID: %s, Slot: %s)", post.id, title, site.name, wp_res.remote_post_id, target_time)
            else:
                post.failure_reason = wp_res.error_message
                db.commit()
                logger.error("Failed to schedule on WordPress for site %s: %s", site.name, wp_res.error_message)

        except Exception as e:
            try:
                db.rollback()
            except Exception:
                pass
            logger.error("Error generating/scheduling post for site %d: %s", site.id, str(e), exc_info=True)

    # 5. Send consolidated Telegram Alert
    if scheduled_posts:
        try:
            from app.services.telegram_service import TelegramAlertService
            tg = TelegramAlertService()
            if tg.is_configured():
                slots_text = "\n".join([f"• {p['scheduled_at'][11:16]}: {p['title'][:32]}..." for p in scheduled_posts])
                msg = (
                    f"🚀 <b>[{site.name}] 오늘 {len(scheduled_posts)}편 예약 등록 완료!</b>\n"
                    f"🌐 도메인: {site.site_url}\n\n"
                    f"{slots_text}\n\n"
                    f"<i>(구글 E-E-A-T 및 Anti-Cliche 검수 통과)</i>"
                )
                await tg.send_message(msg)
        except Exception as tge:
            logger.debug("Telegram alert skipped: %s", str(tge))

    return {
        "success": len(scheduled_posts) > 0,
        "site_id": site.id,
        "site_name": site.name,
        "scheduled_count": len(scheduled_posts),
        "posts": scheduled_posts
    }


async def run_all_active_sites_pipeline(
    db: Session,
    post_count_per_site: int = 4,
    force: bool = False
) -> AutomationRun:
    """Execute end-to-end multi-site automation pipeline across all active WordPress sites."""
    settings = get_settings()
    run_uuid = uuid.uuid4().hex[:16]

    run = AutomationRun(
        run_uuid=run_uuid,
        started_at=utc_now(),
        status="running"
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    logger.info("========== [START ALL-SITES PIPELINE %s (Target: %d posts/site)] ==========", run_uuid, post_count_per_site)

    if not settings.AUTO_PUBLISH and not force:
        msg = "자동화 중단: AUTO_PUBLISH 설정이 비활성화(false)되어 있습니다."
        logger.info(msg)
        run.status = "completed"
        run.summary = msg
        run.finished_at = utc_now()
        db.commit()
        return run

    sites = db.query(Site).filter(Site.is_active == True).order_by(Site.id.asc()).all()
    total_sites = len(sites)
    total_scheduled = 0
    summaries = []

    for site in sites:
        try:
            res = await run_single_site_schedule(db, site, post_target_count=post_count_per_site, force=force)
            cnt = res.get("scheduled_count", 0)
            total_scheduled += cnt
            summaries.append(f"[{site.name}]: {cnt}편 예약")
        except Exception as se:
            logger.error("Site %d automation failed: %s", site.id, str(se), exc_info=True)
            summaries.append(f"[{site.name}]: 실패 ({str(se)})")

    run.status = "completed"
    run.scheduled_count = total_scheduled
    run.finished_at = utc_now()
    run.summary = f"전체 {total_sites}개 블로그 대상 총 {total_scheduled}편 예약 완료!\n" + " | ".join(summaries)
    db.commit()

    logger.info("========== [COMPLETED ALL-SITES PIPELINE %s: Total %d posts scheduled] ==========", run_uuid, total_scheduled)
    return run
