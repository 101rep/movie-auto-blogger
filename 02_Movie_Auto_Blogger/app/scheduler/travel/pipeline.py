"""Travel Vertical Automation Pipeline for Trendspot/TravelPick24."""
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.config import get_settings
from app.core.verticals import VerticalType
from app.core.registry import get_platform_registry
from app.database.models import (
    AutomationRun,
    Post,
    PostStatusEnum,
    QualityStatusEnum,
    Site,
    utc_now,
)
from app.publishers.base import PostStatus
from app.services.publishing_service import PublishingService
from app.services.internal_link_service import InternalLinkService
from app.services.quality_service import QualityGateService
from app.utils.logging import get_logger
from app.scheduler.logging_helpers import log_event as _log_event_helper
from app.scheduler.common import calculate_schedule_datetimes

logger = get_logger("scheduler_travel_pipeline")


async def run_travel_automation_pipeline(db: Session, force: bool = False) -> AutomationRun:
    """Execute end-to-end idempotent automation pipeline for Travel vertical (TravelPick24).

    Generates and schedules daily travel guides (default 4 posts) at configured KST times.
    """
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

    logger.info("========== [START TRAVEL AUTOMATION RUN %s] ==========", run_uuid)

    # Wrapper for shared logging helper in travel pipeline
    def log_event(stage: str, event_code: str, message: str, severity: str = "info", entity_type: Optional[str] = None, entity_id: Optional[str] = None):
        _log_event_helper(run.id, db, stage, event_code, message, severity, entity_type, entity_id)

    log_event("init", "RUN_STARTED", f"여행 자동화 파이프라인 가동 시작 (Run UUID: {run_uuid})")

    # Verify automation is enabled unless force=True
    if not settings.AUTO_PUBLISH and not force:
        msg = "여행 자동화 실행 중단: AUTO_PUBLISH 설정이 비활성화(false)되어 있습니다."
        logger.info(msg)
        log_event("init", "AUTOMATION_DISABLED", msg, severity="warning")
        run.status = "completed"
        run.summary = msg
        run.finished_at = utc_now()
        db.commit()
        return run

    try:
        # 1. Resolve Travel Module
        from app.modules.travel.module import TravelModule
        registry = get_platform_registry()
        travel_mod = registry.get_module(VerticalType.TRAVEL)
        if not travel_mod:
            travel_mod = TravelModule()
            registry.register_module(travel_mod)

        # 2. Collect destination candidates
        post_target_count = min(max(settings.DAILY_POST_COUNT, 1), 10)
        candidates = await travel_mod.collect_candidates(db, limit=30)
        run.candidate_count = len(candidates)
        log_event("collector", "DISCOVERY_COMPLETED", f"여행 후보지 {len(candidates)}곳 수집 완료")

        if not candidates:
            msg = "수집된 여행 후보지가 없습니다."
            logger.warning(msg)
            run.status = "completed"
            run.summary = msg
            run.finished_at = utc_now()
            db.commit()
            return run

        # 3. Resolve active TRAVEL site
        site = db.execute(
            select(Site).where(Site.vertical == "TRAVEL", Site.is_active == True)
        ).scalar_one_or_none()

        # 4. Calculate publication times in Asia/Seoul
        schedule_times = calculate_schedule_datetimes(
            settings.PUBLISH_TIME_1,
            settings.PUBLISH_TIME_2,
            settings.PUBLISH_TIME_3,
            settings.PUBLISH_TIME_4,
            tz_str=settings.APP_TIMEZONE,
            post_count=post_target_count
        )

        publishing_service = PublishingService()
        selected_candidates = []

        # Filter out already published/scheduled destinations
        for cand in candidates:
            already_done = db.query(Post).filter(
                Post.vertical == "TRAVEL",
                Post.external_id == cand.external_id,
                Post.status.in_([PostStatusEnum.SCHEDULED.value, PostStatusEnum.PUBLISHED.value])
            ).first()
            if not already_done:
                selected_candidates.append(cand)
            if len(selected_candidates) >= post_target_count:
                break

        # Fallback if catalog fully exhausted: allow all candidates
        if not selected_candidates:
            selected_candidates = candidates[:post_target_count]

        run.eligible_count = len(selected_candidates)

        for idx, cand in enumerate(selected_candidates):
            target_time = schedule_times[idx] if idx < len(schedule_times) else schedule_times[-1]

            logger.info("Processing travel candidate [%d/%d]: '%s' (External ID: %s)", idx + 1, len(selected_candidates), cand.title, cand.external_id)
            log_event("pipeline", "PROCESSING_TRAVEL", f"여행지 '{cand.title}' 기사 생성 및 예약 착수", entity_type="candidate", entity_id=cand.external_id)

            try:
                # Enrich & Generate
                enriched = await travel_mod.enrich_item(db, cand.external_id)
                gen = await travel_mod.generate_content(db, enriched)
                article_obj = gen.get("travel_article")

                # Fetch travel internal links
                travel_internal_links = InternalLinkService.get_related_travel_links(db, current_destination=cand.title)
                gen["internal_links"] = travel_internal_links

                rendered_html = travel_mod.render_html(gen)

                title = article_obj.title if article_obj else cand.title
                excerpt = article_obj.excerpt if article_obj else cand.summary
                article_json_str = article_obj.model_dump_json() if article_obj else "{}"

                # Deterministic Quality Gate & Travel Fact Check
                travel_item_obj = enriched.get("travel_item") or cand
                quality_status, quality_issues = QualityGateService.evaluate_travel(
                    article=article_obj,
                    expected_destination=cand.title,
                    travel_item=travel_item_obj
                )

                if quality_status == QualityStatusEnum.PASS:
                    initial_status = PostStatusEnum.APPROVED.value
                elif quality_status == QualityStatusEnum.REVIEW:
                    initial_status = PostStatusEnum.REVIEW.value
                else:
                    initial_status = PostStatusEnum.FAILED.value

                post = Post(
                    title=title,
                    slug=f"travel-{cand.external_id.lower()}-{uuid.uuid4().hex[:6]}",
                    rendered_content=rendered_html,
                    excerpt=excerpt,
                    seo_title=article_obj.seo_title if article_obj else title,
                    meta_description=article_obj.meta_description if article_obj else excerpt,
                    vertical="TRAVEL",
                    external_id=cand.external_id,
                    site_id=site.id if site else None,
                    status=initial_status,
                    quality_status=quality_status.value,
                    article_json=article_json_str,
                    scheduled_at=target_time,
                    failure_reason=", ".join(quality_issues) if quality_issues else None
                )
                db.add(post)
                db.commit()
                db.refresh(post)
                run.generated_count += 1

                # Schedule on WordPress only if quality PASS
                if quality_status == QualityStatusEnum.PASS:
                    pub_res = await publishing_service.publish_article(
                        db,
                        post,
                        target_status=PostStatus.FUTURE,
                        scheduled_time=target_time
                    )

                    if pub_res.success:
                        run.scheduled_count += 1
                        log_event("publisher", "POST_SCHEDULED", f"[{cand.external_id}] '{title}' 워드프레스 예약 발행 성공 (원격 ID: {pub_res.remote_post_id}, 예약시각: {target_time})", entity_type="post", entity_id=post.id)
                    else:
                        run.failed_count += 1
                        log_event("publisher", "POST_SCHEDULE_FAILED", f"[{cand.external_id}] '{title}' 예약 실패: {pub_res.error_message}", severity="error", entity_type="post", entity_id=post.id)
                else:
                    log_event("quality", "POST_HELD_FOR_REVIEW", f"[{cand.external_id}] '{title}' 품질 게이트 미달로 자동 예약 보류 (상태: {quality_status.value}, 사유: {', '.join(quality_issues)})", severity="warning", entity_type="post", entity_id=post.id)

            except Exception as item_err:
                run.failed_count += 1
                logger.error("Error processing travel candidate %s: %s", cand.external_id, str(item_err), exc_info=True)
                log_event("pipeline", "ITEM_ERROR", f"'{cand.external_id}' 처리 중 오류: {str(item_err)}", severity="error")

        run.status = "completed"
        run.summary = f"여행 콘텐츠 생성: {run.generated_count}건, 예약: {run.scheduled_count}건, 실패: {run.failed_count}건"
        run.finished_at = utc_now()
        db.commit()

        log_event("finish", "RUN_COMPLETED", f"여행 자동화 파이프라인 정상 완료. ({run.summary})")
        logger.info("========== [END TRAVEL AUTOMATION RUN %s: %s] ==========", run_uuid, run.summary)
        return run

    except Exception as e:
        logger.error("Travel automation fatal exception: %s", str(e), exc_info=True)
        run.status = "failed"
        run.summary = f"여행 파이프라인 실행 중 오류 발생: {str(e)}"
        run.finished_at = utc_now()
        db.commit()
        log_event("error", "FATAL_EXCEPTION", str(e), severity="error")
        return run
