"""Movie Vertical Automation Pipeline for Trendspot24."""
import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import (
    AutomationRun,
    JobStatusEnum,
    PostStatusEnum,
    QualityStatusEnum,
    utc_now,
)
from app.publishers.base import PostStatus
from app.services.article_service import ArticleService
from app.services.candidate_service import CandidateService
from app.services.job_service import JobService
from app.services.retry_service import RetryService
from app.services.movie_service import MovieService
from app.services.publishing_service import PublishingService
from app.utils.logging import get_logger
from app.scheduler.logging_helpers import log_event as _log_event_helper
from app.scheduler.common import calculate_schedule_datetimes

logger = get_logger("scheduler_movie_pipeline")


async def run_automation_pipeline(db: Session, force: bool = False) -> AutomationRun:
    """Execute the full end-to-end idempotent automation pipeline for Movie vertical.

    Idempotent: Rerunning will not re-select or duplicate already published/scheduled movies.
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

    logger.info("========== [START AUTOMATION RUN %s] ==========", run_uuid)

    # Wrapper for shared logging helper
    def log_event(stage: str, event_code: str, message: str, severity: str = "info", entity_type: Optional[str] = None, entity_id: Optional[str] = None):
        _log_event_helper(run.id, db, stage, event_code, message, severity, entity_type, entity_id)

    log_event("init", "RUN_STARTED", f"자동화 파이프라인 가동 시작 (Run UUID: {run_uuid})")

    # 1. Verify automation is enabled unless force=True
    if not settings.AUTO_PUBLISH and not force:
        msg = "자동화 실행 중단: AUTO_PUBLISH 설정이 비활성화(false)되어 있습니다."
        logger.info(msg)
        log_event("init", "AUTOMATION_DISABLED", msg, severity="warning")
        run.status = "completed"
        run.summary = msg
        run.finished_at = utc_now()
        db.commit()
        return run

    try:
        # 2. Discover, deduplicate, score, and persist candidate pool
        candidate_service = CandidateService()
        log_event("collector", "DISCOVERY_STARTED", f"후보 영화 수집 시작 (풀 크기: {settings.CANDIDATE_POOL_SIZE})")

        ranked_movies = await candidate_service.collect_score_and_persist(db, pool_size=settings.CANDIDATE_POOL_SIZE)
        run.candidate_count = len(ranked_movies)
        log_event("collector", "DISCOVERY_COMPLETED", f"후보 영화 {len(ranked_movies)}편 수집 및 점수화 완료")

        if not ranked_movies:
            msg = "수집된 적격 후보 영화가 없습니다. TMDB API 및 중복 필터를 확인하세요."
            logger.warning(msg)
            log_event("collector", "NO_CANDIDATES", msg, severity="warning")
            run.status = "completed"
            run.summary = msg
            run.finished_at = utc_now()
            db.commit()
            return run

        # 3. Select top N candidates based on daily post count (max 10)
        post_target_count = min(max(settings.DAILY_POST_COUNT, 1), 10)
        selected_movies = ranked_movies[:post_target_count]
        run.eligible_count = len(selected_movies)

        # 4. Calculate publication times in Asia/Seoul
        schedule_times = calculate_schedule_datetimes(
            settings.PUBLISH_TIME_1,
            settings.PUBLISH_TIME_2,
            settings.PUBLISH_TIME_3,
            settings.PUBLISH_TIME_4,
            tz_str=settings.APP_TIMEZONE,
            post_count=post_target_count
        )

        movie_service = MovieService()
        article_service = ArticleService()
        publishing_service = PublishingService()

        # 5. Process each candidate: Enrich -> Generate -> Quality Gate -> WordPress Schedule
        for idx, movie in enumerate(selected_movies):
            target_time = schedule_times[idx] if idx < len(schedule_times) else schedule_times[-1]

            # Atomic Job Claim & Duplicate Execution Prevention
            claimed, job, claim_msg = JobService.claim_movie_job(db, movie.id, worker_id=run.run_uuid)
            if not claimed:
                logger.info("Skipping candidate '%s': %s", movie.title, claim_msg)
                log_event("pipeline", "JOB_SKIPPED", f"영화 '{movie.title}' 건너뜀: {claim_msg}", severity="info", entity_type="movie", entity_id=movie.id)
                continue

            logger.info("Processing candidate [%d/%d]: '%s' (Score: %.1f)", idx + 1, len(selected_movies), movie.title, movie.candidate_score or 0.0)
            log_event("pipeline", "PROCESSING_MOVIE", f"영화 '{movie.title}' 기사 생성 및 예약 착수", entity_type="movie", entity_id=movie.id)

            # Transition job status: PROCESSING
            JobService.update_job_status(db, job, JobStatusEnum.PROCESSING)

            # A. Enrich details
            movie = await movie_service.enrich_movie_details(db, movie)

            # B. AI Generation
            post, gen_result, quality_status, issues = await article_service.generate_article_for_movie(
                db, movie, save_post=True
            )

            if not gen_result.success or not post:
                run.failed_count += 1
                gen_err = RuntimeError(gen_result.error_message or "AI 기사 생성 실패")
                RetryService.schedule_job_retry(db, job, gen_err)
                log_event("ai", "GENERATION_FAILED", f"'{movie.title}' AI 기사 생성 실패: {gen_result.error_message} (상태: {job.status}, 재시도: {job.retry_count})", severity="error", entity_type="movie", entity_id=movie.id)
                continue

            run.generated_count += 1
            # Transition job status: QUALITY_CHECK
            JobService.update_job_status(db, job, JobStatusEnum.QUALITY_CHECK, post_id=post.id)

            log_event(
                "ai",
                "GENERATION_SUCCESS",
                f"'{movie.title}' 기사 생성 완료 (사용 AI: {gen_result.used_provider}, 등급: {quality_status.value})",
                entity_type="post",
                entity_id=post.id
            )

            # C. Quality Gate Routing & WordPress Publishing
            if quality_status == QualityStatusEnum.PASS:
                JobService.update_job_status(db, job, JobStatusEnum.PUBLISHING, post_id=post.id)
                pub_res = await publishing_service.publish_article(
                    db,
                    post,
                    target_status=PostStatus.FUTURE,
                    scheduled_time=target_time
                )
                if pub_res.success:
                    run.scheduled_count += 1
                    JobService.update_job_status(db, job, JobStatusEnum.COMPLETED, post_id=post.id)
                    log_event("publisher", "POST_SCHEDULED", f"워드프레스 예약 발행 성공 (원격 ID: {pub_res.remote_post_id}, 예약시각: {target_time})", entity_type="post", entity_id=post.id)
                else:
                    run.failed_count += 1
                    pub_err = RuntimeError(f"WordPress publish failed: {pub_res.error_message}")
                    RetryService.schedule_job_retry(db, job, pub_err)
                    log_event("publisher", "PUBLISH_FAILED", f"워드프레스 예약 등록 실패: {pub_res.error_message} (재시도 예약: {job.next_retry_at})", severity="error", entity_type="post", entity_id=post.id)

            elif quality_status == QualityStatusEnum.REVIEW:
                pub_res = await publishing_service.publish_article(db, post, target_status=PostStatus.DRAFT)
                JobService.update_job_status(db, job, JobStatusEnum.COMPLETED, post_id=post.id)
                log_event("publisher", "SAVED_AS_DRAFT", f"품질 기준 REVIEW로 인해 워드프레스 초안으로 안전 저장됨 ({', '.join(issues)})", severity="warning", entity_type="post", entity_id=post.id)

            else:
                run.failed_count += 1
                quality_err = ValueError(f"품질 기준 미달: {', '.join(issues)}")
                RetryService.schedule_job_retry(db, job, quality_err)
                log_event("quality", "QUALITY_FAILED", f"품질 기준 미달(FAIL)로 발행 중단: {', '.join(issues)}", severity="error", entity_type="post", entity_id=post.id)

        # 6. Finalize Run
        run.status = "completed"
        run.summary = f"생성: {run.generated_count}건, 예약: {run.scheduled_count}건, 실패/보류: {run.failed_count}건"
        run.finished_at = utc_now()
        db.commit()

        log_event("finish", "RUN_COMPLETED", f"자동화 파이프라인 정상 완료. ({run.summary})")
        logger.info("========== [END AUTOMATION RUN %s: %s] ==========", run_uuid, run.summary)
        return run

    except Exception as e:
        logger.error("Automation pipeline fatal exception: %s", str(e), exc_info=True)
        run.status = "failed"
        run.summary = f"파이프라인 실행 중 오류 발생: {str(e)}"
        run.finished_at = utc_now()
        db.commit()
        log_event("error", "FATAL_EXCEPTION", str(e), severity="error")
        return run
