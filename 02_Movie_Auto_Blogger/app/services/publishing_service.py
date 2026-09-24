"""Publishing coordinator service managing WordPress post lifecycle."""
import json
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.ai.schemas import ArticleOutput
from app.config import get_settings
from app.database.models import Post, PostStatusEnum, QualityStatusEnum
from app.publishers.base import PostStatus, PublishRequest, PublishResult
from app.publishers.wordpress import WordPressPublisher
from app.services.article_service import ArticleService
from app.services.indexnow_service import IndexNowService
from app.services.internal_link_service import InternalLinkService
from app.services.media_service import MediaService
from app.utils.logging import get_logger

logger = get_logger("publishing_service")


class PublishingService:
    """Coordinates media upload, internal linking, taxonomy mapping, and WordPress publishing."""

    def __init__(
        self,
        publisher: Optional[WordPressPublisher] = None,
        media_service: Optional[MediaService] = None,
        indexnow_service: Optional[IndexNowService] = None
    ) -> None:
        self.publisher = publisher or WordPressPublisher()
        self.media_service = media_service or MediaService(wp_publisher=self.publisher)
        self.indexnow_service = indexnow_service or IndexNowService()
        self.article_service = ArticleService()
        self.settings = get_settings()

    async def publish_article(
        self,
        db: Session,
        post: Post,
        target_status: PostStatus = PostStatus.DRAFT,
        scheduled_time: Optional[datetime] = None
    ) -> PublishResult:
        """Publish or schedule an article on WordPress."""
        logger.info("Initiating WordPress publishing for Post ID %d ('%s') as %s...", post.id, post.title, target_status.value)
        # Resolve publisher (Site-specific if post is bound to a site)
        active_publisher = self.publisher
        if post.site and post.site.site_url:
            active_publisher = WordPressPublisher(
                site_url=post.site.site_url,
                username=post.site.wp_username or self.settings.WORDPRESS_USERNAME,
                app_password=post.site.wp_application_password or self.settings.WORDPRESS_APPLICATION_PASSWORD
            )

        featured_media_id = None
        categories: list[str] = []
        tags: list[str] = []
        movie = post.movie

        if movie:
            # 1. Media handling for movies
            if self.settings.MEDIA_UPLOAD_ENABLED:
                media_id, media_err = await self.media_service.upload_movie_poster(db, movie)
                if media_err:
                    logger.warning("Media upload error: %s. Setting post to REVIEW.", media_err)
                    post.status = PostStatusEnum.REVIEW.value
                    post.failure_reason = f"미디어 업로드 실패: {media_err}"
                    db.commit()
                    return PublishResult(success=False, error_message=media_err)
                featured_media_id = media_id

            # 2. Internal Linking & HTML re-rendering for movies
            internal_links = InternalLinkService.get_related_links(db, movie, limit=3)
            if post.article_json:
                try:
                    article_data = json.loads(post.article_json)
                    article_obj = ArticleOutput.model_validate(article_data)
                    trailer_info = None
                    try:
                        trailer_info = await self.article_service.trailer_service.get_trailer_info(
                            movie_title=movie.title,
                            external_id=movie.external_id
                        )
                    except Exception as te:
                        logger.debug("Could not fetch trailer during re-render: %s", str(te))

                    post.rendered_content = self.article_service.render_html(
                        article=article_obj,
                        movie_title=movie.title,
                        poster_url=movie.poster_reference,
                        media_enabled=self.settings.MEDIA_UPLOAD_ENABLED,
                        internal_links=internal_links,
                        trailer_info=trailer_info,
                        movie=movie
                    )
                except Exception as e:
                    logger.warning("Could not re-render HTML with internal links: %s", str(e))

            # 3. Taxonomy Preparation for movie
            categories = json.loads(movie.genres_json) if movie.genres_json else ["영화"]
            if post.article_json:
                try:
                    tags = json.loads(post.article_json).get("tags", [])
                except Exception:
                    pass
            if movie.director and movie.director not in tags:
                tags.append(movie.director)
        else:
            # Non-movie verticals (Welfare, Entertainment, etc.)
            vertical_name = (post.vertical or "NEWS").upper()
            if vertical_name == "WELFARE":
                categories = ["정부지원", "복지혜택"]
            elif vertical_name in ("ENTERTAINMENT", "NEWS"):
                categories = ["연예", "K-컬처"]
            elif vertical_name == "TRAVEL":
                categories = ["여행", "해외여행", "추천코스"]
            else:
                categories = [vertical_name]

            if post.article_json:
                try:
                    art_dict = json.loads(post.article_json)
                    tags = art_dict.get("tags", [])
                    hero_image_url = art_dict.get("hero_image_url")
                    if hero_image_url and self.settings.MEDIA_UPLOAD_ENABLED:
                        try:
                            import httpx
                            async with httpx.AsyncClient(timeout=15.0) as client:
                                res = await client.get(hero_image_url)
                                if res.status_code == 200:
                                    content_type = res.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                                    ext = "jpg" if "jpeg" in content_type else "png" if "png" in content_type else "webp"
                                    media_id = await active_publisher.upload_media(
                                        file_bytes=res.content,
                                        filename=f"{vertical_name.lower()}-{post.slug}.{ext}",
                                        alt_text=f"{post.title} 대표 썸네일",
                                        content_type=content_type
                                    )
                                    if media_id:
                                        featured_media_id = media_id
                        except Exception as m_err:
                            logger.warning("Failed to upload featured media for %s post %d: %s", vertical_name, post.id, m_err)
                except Exception:
                    pass

        # 4. Schedule Formatting (ISO 8601 UTC string for WP date_gmt and local string for WP date)
        scheduled_at_str = None
        scheduled_at_local_str = None
        if target_status == PostStatus.FUTURE:
            sched = scheduled_time or post.scheduled_at or datetime.now(timezone.utc)
            scheduled_at_str = sched.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            from zoneinfo import ZoneInfo
            kst_tz = ZoneInfo("Asia/Seoul")
            scheduled_at_local_str = sched.astimezone(kst_tz).strftime("%Y-%m-%dT%H:%M:%S")
            post.scheduled_at = sched

        # 5. Build PublishRequest
        pub_request = PublishRequest(
            title=post.title,
            content=post.rendered_content or post.excerpt or "",
            excerpt=post.excerpt,
            slug=post.slug,
            status=target_status,
            scheduled_at=scheduled_at_str,
            scheduled_at_local=scheduled_at_local_str,
            featured_media_id=featured_media_id,
            categories=categories,
            tags=tags
        )

        # 6. Execute Remote Post with 3-Tier Retries & Telegram Failure Alert
        import asyncio
        max_retries = 3
        result = None
        blog_name = post.site.name if post.site and post.site.name else (post.site.site_url if post.site else "워드프레스 블로그")
        scheduled_display_time = scheduled_at_local_str.split("T")[-1][:5] if scheduled_at_local_str and "T" in scheduled_at_local_str else (scheduled_at_str or "즉시")

        for attempt in range(1, max_retries + 1):
            logger.info("WordPress publishing attempt %d/%d for Post ID %d...", attempt, max_retries, post.id)
            result = await active_publisher.publish_post(pub_request)
            if result.success and result.remote_post_id:
                break

            # Failed attempt -> Immediate Telegram Alert
            logger.warning("WordPress publishing attempt %d failed: %s", attempt, result.error_message)
            await self._send_telegram_failure_alert(
                blog_name=blog_name,
                title=post.title,
                scheduled_time=scheduled_display_time,
                error_msg=result.error_message or "API 오류",
                retry_count=attempt,
                max_retries=max_retries
            )

            if attempt < max_retries:
                await asyncio.sleep(2.0 * attempt)

        # 7. Persist Results
        if result and result.success and result.remote_post_id:
            post.wordpress_post_id = result.remote_post_id
            post.wordpress_url = result.remote_url
            if target_status == PostStatus.FUTURE:
                post.status = PostStatusEnum.SCHEDULED.value
            elif target_status == PostStatus.PUBLISH:
                post.status = PostStatusEnum.PUBLISHED.value
                post.published_at = datetime.now(timezone.utc)
            else:
                post.status = PostStatusEnum.APPROVED.value

            post.failure_reason = None
            db.commit()
            db.refresh(post)
            logger.info("WordPress publishing succeeded after verification: Post ID %d -> Remote ID %d", post.id, result.remote_post_id)

            # 8. IndexNow & Search Engine Instant Notification
            if result.remote_url:
                try:
                    await self.indexnow_service.submit_urls([result.remote_url])
                    await self.indexnow_service.ping_sitemaps()
                except Exception as ie:
                    logger.debug("IndexNow submission non-critical notice: %s", str(ie))
        else:
            post.status = PostStatusEnum.FAILED.value
            post.failure_reason = result.error_message if result else "알 수 없는 발행 실패"
            db.commit()
            logger.error("WordPress publishing permanently failed after %d attempts: %s", max_retries, post.failure_reason)

        return result

    async def _send_telegram_failure_alert(
        self,
        blog_name: str,
        title: str,
        scheduled_time: str,
        error_msg: str,
        retry_count: int,
        max_retries: int = 3
    ) -> None:
        """Send instant failure alert to Telegram matching Master Requirements."""
        token = self.settings.TELEGRAM_BOT_TOKEN or "8932770710:AAFtKYRBUwmz9-VZVxgn2TJenA8_k_B6BKs"
        chat_id = self.settings.TELEGRAM_CHAT_ID or "6290024230"
        if not token or not chat_id:
            return

        lines = [
            "🚨 <b>자동화 실패 알림</b>\n",
            "<b>시스템:</b> WordPress 자동발행",
            f"<b>블로그:</b> {blog_name}",
            f"<b>제목:</b> {title}",
            f"<b>예약시간:</b> {scheduled_time}",
            "<b>상태:</b> FAILED",
            f"<b>원인:</b> {error_msg[:300]}",
            f"<b>재시도:</b> {retry_count}/{max_retries}"
        ]

        if retry_count >= max_retries:
            lines.extend([
                "",
                "🚨 <b>최종 실패</b>",
                "<b>수동 확인 필요</b>"
            ])

        alert_text = "\n".join(lines)
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": str(chat_id), "text": alert_text, "parse_mode": "HTML"}
                )
                if res.status_code != 200:
                    # Retry without parse_mode if entity formatting failed
                    await client.post(
                        f"https://api.telegram.org/bot{token}/sendMessage",
                        json={"chat_id": str(chat_id), "text": alert_text.replace("<b>", "").replace("</b>", "")}
                    )
        except Exception as e:
            logger.warning("Failed to dispatch Telegram failure alert: %s", str(e))
