"""Media downloading, validation, and WordPress media upload service."""
import os
from typing import Optional, Tuple
import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.models import Media, Movie
from app.publishers.wordpress import WordPressPublisher
from app.utils.logging import get_logger

logger = get_logger("media_service")

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class MediaService:
    """Manages movie image downloads, safety validation, and WordPress media uploads."""

    def __init__(self, wp_publisher: Optional[WordPressPublisher] = None) -> None:
        self.wp = wp_publisher or WordPressPublisher()
        self.settings = get_settings()

    async def upload_movie_poster(
        self,
        db: Session,
        movie: Movie
    ) -> Tuple[Optional[int], Optional[str]]:
        """Download, validate, and upload movie poster to WordPress.

        Returns:
            (wordpress_media_id, error_message)
        """
        if not self.settings.MEDIA_UPLOAD_ENABLED:
            logger.info("Media upload disabled in configuration. Skipping poster upload for '%s'.", movie.title)
            return None, None

        if not movie.poster_reference:
            logger.info("No poster reference available for '%s'.", movie.title)
            return None, None

        # Check if already uploaded in DB
        existing_media = db.query(Media).filter(
            Media.movie_id == movie.id,
            Media.status == "uploaded",
            Media.wordpress_media_id.isnot(None)
        ).first()

        if existing_media and existing_media.wordpress_media_id:
            logger.info("Reusing existing WordPress media ID %d for movie '%s'", existing_media.wordpress_media_id, movie.title)
            return existing_media.wordpress_media_id, None

        # Download and validate image
        logger.info("Downloading poster for '%s' from %s...", movie.title, movie.poster_reference)
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(movie.poster_reference)
                if res.status_code != 200:
                    err = f"포스터 다운로드 실패 (HTTP {res.status_code})"
                    logger.warning(err)
                    return None, err

                content_type = res.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                if content_type not in ALLOWED_MIME_TYPES:
                    err = f"허용되지 않은 미디어 파일 형식입니다: {content_type}"
                    logger.warning(err)
                    return None, err

                file_bytes = res.content
                if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
                    err = f"포스터 파일 크기 초과 (용량: {len(file_bytes)} bytes / 최대 5MB)"
                    logger.warning(err)
                    return None, err

                # Upload to WordPress
                ext = "jpg" if "jpeg" in content_type else "png" if "png" in content_type else "webp"
                filename = f"movie-poster-{movie.external_id}.{ext}"
                alt_text = f"{movie.title} 영화 포스터"

                media_id = await self.wp.upload_media(
                    file_bytes=file_bytes,
                    filename=filename,
                    alt_text=alt_text,
                    content_type=content_type
                )

                if not media_id:
                    err = "워드프레스 미디어 엔드포인트 업로드 실패"
                    # Record failure in media table
                    failed_rec = Media(
                        movie_id=movie.id,
                        source_reference=movie.poster_reference,
                        media_type="poster",
                        status="failed",
                        failure_reason=err
                    )
                    db.add(failed_rec)
                    db.commit()
                    return None, err

                # Record success in media table
                media_record = Media(
                    movie_id=movie.id,
                    source_reference=movie.poster_reference,
                    media_type="poster",
                    wordpress_media_id=media_id,
                    status="uploaded"
                )
                db.add(media_record)
                db.commit()
                return media_id, None

        except Exception as e:
            err = f"포스터 처리 중 예외 발생: {str(e)}"
            logger.error(err, exc_info=True)
            return None, err
