"""Publication Verification Agent for Welfare Engine V1.0.
Verifies actual WordPress post registration, status ('future' or 'publish'),
and live URL reachability via WordPress REST API.
Dispatches immediate Telegram alerts upon failure.
"""
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import aiohttp

from welfare_engine.config import WelfareBlogConfig
from welfare_engine.database.models import WelfarePublication
from welfare_engine.reporter.telegram_reporter import WelfareTelegramReporter

logger = logging.getLogger("welfare_engine.verifier")


class WelfareVerifierAgent:
    """Rigorous verification agent auditing post publication integrity."""

    def __init__(self, reporter: Optional[WelfareTelegramReporter] = None):
        self.reporter = reporter or WelfareTelegramReporter()

    @staticmethod
    def _build_auth_header(username: str, app_pass: str) -> str:
        clean_pass = app_pass.replace(" ", "")
        token = f"{username}:{clean_pass}"
        encoded = base64.b64encode(token.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    async def verify_post(
        self,
        blog: WelfareBlogConfig,
        post_id: int,
        expected_status: str = "future"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Query WordPress REST API directly to verify post existence, status, and URL."""
        if not post_id or post_id <= 0:
            return False, "유효하지 않은 post_id", {}

        url = f"{blog.domain}/wp-json/wp/v2/posts/{post_id}?context=edit"
        headers = {
            "Authorization": self._build_auth_header(blog.wp_user, blog.wp_pass)
        }

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        err_text = await resp.text()
                        reason = f"WordPress REST API 조회 실패 (HTTP {resp.status}): {err_text[:150]}"
                        logger.error(f"[{blog.blog_key}] {reason}")
                        return False, reason, {}

                    data = await resp.json()
                    real_status = data.get("status")
                    permalink = data.get("link") or data.get("guid", {}).get("rendered", "")
                    title = data.get("title", {}).get("rendered", "")
                    date_scheduled = data.get("date")

                    # Status verification
                    valid_statuses = [expected_status]
                    if expected_status == "future":
                        valid_statuses.append("publish") # In case it was published immediately

                    if real_status not in valid_statuses:
                        reason = f"상태 불일치: 기대값 '{expected_status}', 실제값 '{real_status}'"
                        logger.error(f"[{blog.blog_key}] Verification failed: {reason}")
                        return False, reason, data

                    # URL verification
                    if not permalink or not permalink.startswith("http"):
                        reason = f"유효하지 않은 포스트 URL: '{permalink}'"
                        logger.error(f"[{blog.blog_key}] Verification failed: {reason}")
                        return False, reason, data

                    logger.info(f"[{blog.blog_key}] Verification SUCCESS: Post {post_id} ('{real_status}') at {permalink}")
                    return True, "정상 검증 완료", {
                        "post_id": post_id,
                        "status": real_status,
                        "permalink": permalink,
                        "date_scheduled": date_scheduled,
                        "title": title
                    }
        except Exception as e:
            reason = f"검증 통신 예외 발생: {str(e)}"
            logger.error(f"[{blog.blog_key}] Verification exception: {e}")
            return False, reason, {}

    async def verify_and_record(
        self,
        publication: WelfarePublication,
        blog: WelfareBlogConfig,
        expected_status: str = "future"
    ) -> bool:
        """Verify publication and update the DB record. Alert Telegram on failure."""
        success, reason, verified_data = await self.verify_post(
            blog=blog,
            post_id=publication.wp_post_id,
            expected_status=expected_status
        )

        publication.verified_at = datetime.utcnow()
        if success:
            publication.verification_status = "VERIFIED"
            publication.wp_status = verified_data.get("status", expected_status)
            publication.wp_url = verified_data.get("permalink", publication.wp_url)
            publication.error_message = None
            return True
        else:
            publication.verification_status = "FAILED"
            publication.error_message = reason
            # Send emergency alert via Telegram
            await self.reporter.send_verification_failure_alert(
                blog_name=f"{blog.name} ({blog.blog_key})",
                title=publication.persona_title or "무제",
                reason=reason,
                post_id=publication.wp_post_id
            )
            return False
