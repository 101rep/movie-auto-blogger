"""Background retries and WordPress publication status sync jobs."""
import asyncio
from sqlalchemy.orm import Session
from app.database.models import (
    ContentJob,
    JobStatusEnum,
    Post,
    PostStatusEnum,
    Site,
    utc_now,
)
from app.database.session import SessionLocal
from app.publishers.base import PostStatus
from app.services.job_service import JobService
from app.services.publishing_service import PublishingService
from app.services.retry_service import RetryService
from app.utils.logging import get_logger

logger = get_logger("scheduler_retries")


async def process_due_retries(db: Session, max_jobs: int = 5) -> int:
    """Scan and process jobs in RETRY_WAIT whose backoff time has elapsed."""
    due_jobs = RetryService.get_due_retry_jobs(db, limit=max_jobs)
    if not due_jobs:
        return 0

    logger.info("Found %d due retry job(s) to process...", len(due_jobs))
    processed_count = 0

    publishing_service = PublishingService()

    for job in due_jobs:
        # Idempotency check: Has this movie already been published/scheduled?
        existing_post = RetryService.verify_post_idempotency(db, job.movie_id)
        if existing_post:
            logger.info("Movie %s is already published (Post %d). Marking retry job as COMPLETED.", job.movie_id, existing_post.id)
            JobService.update_job_status(db, job, JobStatusEnum.COMPLETED, post_id=existing_post.id)
            processed_count += 1
            continue

        # Check if a post record already exists and only publishing failed
        post = db.query(Post).filter(Post.id == job.post_id).first() if job.post_id else None
        if post and post.rendered_content:
            logger.info("Retrying WordPress publication for Post %d (Job %s)...", post.id, job.job_uuid)
            JobService.update_job_status(db, job, JobStatusEnum.PUBLISHING)
            pub_res = await publishing_service.publish_article(db, post, target_status=PostStatus.FUTURE)
            if pub_res.success:
                JobService.update_job_status(db, job, JobStatusEnum.COMPLETED, post_id=post.id)
                logger.info("Retry publication succeeded for Post %d", post.id)
            else:
                RetryService.schedule_job_retry(db, job, RuntimeError(f"Retry publication failed: {pub_res.error_message}"))
            processed_count += 1
        else:
            # Need re-generation: mark as claimed and allow pipeline or re-run
            logger.info("Retry job %s needs re-generation for movie %s", job.job_uuid, job.movie_id)
            processed_count += 1

    return processed_count


def sync_published_posts_status(db: Session) -> int:
    """Sync posts in DB that have already been published on WordPress to PUBLISHED status."""
    import httpx
    from app.publishers.wordpress import WordPressPublisher

    sched_posts = db.query(Post).filter(Post.status == PostStatusEnum.SCHEDULED.value).all()
    if not sched_posts:
        return 0

    sites = {
        s.vertical: WordPressPublisher(
            site_url=s.site_url,
            username=s.wp_username,
            app_password=s.wp_application_password
        )
        for s in db.query(Site).all()
    }

    synced_count = 0
    for p in sched_posts:
        vert = p.vertical or "MOVIE"
        pub = sites.get(vert)
        if not pub or not p.wordpress_post_id:
            continue

        try:
            r = httpx.get(f"{pub.api_base_url}/posts/{p.wordpress_post_id}", headers=pub._get_headers(), timeout=8.0, verify=False)
            if r.status_code == 200:
                wp_status = r.json().get("status")
                if wp_status == "publish":
                    p.status = PostStatusEnum.PUBLISHED.value
                    p.published_at = p.scheduled_at or utc_now()
                    synced_count += 1
                elif wp_status == "trash":
                    p.status = "TRASH"
                    synced_count += 1
        except Exception as err:
            logger.debug("WP status sync check skipped for Post %d: %s", p.id, err)

    if synced_count > 0:
        db.commit()
        logger.info("Auto-synced %d post(s) from WordPress to PUBLISHED status.", synced_count)

    return synced_count


def scheduled_retry_job() -> None:
    """Periodic job called by APScheduler to process due retries and sync WP status."""
    with SessionLocal() as db:
        asyncio.run(process_due_retries(db))
        sync_published_posts_status(db)
