"""
AAOS Telegram Control Center Module
Implements commands:
/status, /check_threads, /check_instagram, /check_wordpress, /retry_failed, /log
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import logging
from datetime import datetime, timezone

import asyncio

from core.aaos.job_service import AAOSJobService
from verification.playwright_verifier import PlaywrightVerifier
from core.audit.blog_healer import blog_healer

logger = logging.getLogger("AAOSTelegramControlCenter")

class TelegramControlCenter:
    def __init__(self):
        self.verifier = PlaywrightVerifier()

    async def handle_status(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Returns comprehensive status across all AAOS jobs and platforms."""
        try:
            stats = AAOSJobService.get_system_status()
            total = stats.get("total_jobs", 0)
            verified = stats.get("verified", 0)
            failed = stats.get("failed", 0)
            pending = stats.get("pending", 0)
            success_rate = (verified / total * 100) if total > 0 else 100.0

            platforms = stats.get("platforms", {})
            threads_st = platforms.get("threads", {})
            insta_st = platforms.get("instagram", {})
            wp_st = platforms.get("wordpress", {})

            msg = (
                "🛡️ <b>[AAOS AI Automation Operating System 현황]</b>\n\n"
                f"• <b>전체 작업(Jobs):</b> {total}건\n"
                f"• <b>브라우저 실검증 통과:</b> ✅ <code>{verified}건</code>\n"
                f"• <b>실패/오류:</b> ❌ <code>{failed}건</code>\n"
                f"• <b>진행/대기:</b> ⏳ <code>{pending}건</code>\n"
                f"• <b>실검증 성공률:</b> <b>{success_rate:.1f}%</b>\n\n"
                "📊 <b>플랫폼별 검증 현황:</b>\n"
                f"  🧵 <b>Threads:</b> 총 {threads_st.get('total', 0)}건 | 성공 {threads_st.get('verified', 0)} | 실패 {threads_st.get('failed', 0)}\n"
                f"  📸 <b>Instagram:</b> 총 {insta_st.get('total', 0)}건 | 성공 {insta_st.get('verified', 0)} | 실패 {insta_st.get('failed', 0)}\n"
                f"  ✍️ <b>WordPress:</b> 총 {wp_st.get('total', 0)}건 | 성공 {wp_st.get('verified', 0)} | 실패 {wp_st.get('failed', 0)}\n\n"
                "🔍 <b>명령어 안내:</b>\n"
                "• <code>/check_threads</code> : Threads 최신 포스트 브라우저 검증\n"
                "• <code>/check_instagram</code> : Instagram 최신 포스트 브라우저 검증\n"
                "• <code>/check_wordpress</code> : 워드프레스 블로그 렌더링 검증\n"
                "• <code>/retry_failed</code> : 실패 작업 자동 복구 및 재시도\n"
                "• <code>/log</code> : 최근 실행 및 검증 로그 (10건)"
            )
            return msg, None
        except Exception as e:
            logger.error(f"Error in handle_status: {e}", exc_info=True)
            return f"❌ <b>[AAOS 상태 조회 실패]</b>\n오류: {e}", None

    async def handle_check_threads(self, url: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Runs Playwright verification on Threads post or profile.
        Returns (message, screenshot_path).
        """
        target_url = url or "https://www.threads.net/@ktaehoon80"
        try:
            res = self.verifier.verify_threads(target_url)
            screenshot = res.get("screenshot")
            status_icon = "✅" if res["verified"] else "❌"
            msg = (
                f"{status_icon} <b>[AAOS Threads 브라우저 DOM 검증 결과]</b>\n\n"
                f"• <b>URL:</b> {target_url}\n"
                f"• <b>검증 상태:</b> <b>{res['status']}</b>\n"
                f"• <b>판정 결과:</b> {'정상 노출 확인됨' if res['verified'] else '게시물 미발견 또는 오류'}\n"
                f"• <b>상세:</b> <i>{res['details']}</i>\n"
                f"• <b>캡처 스크린샷:</b> <code>{os.path.basename(screenshot) if screenshot else 'None'}</code>"
            )
            return msg, screenshot
        except Exception as e:
            return f"❌ <b>[Threads 검증 실패]</b> {e}", None

    async def handle_check_wordpress(self, url: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Runs Playwright verification on WordPress post or homepage.
        Returns (message, screenshot_path).
        """
        target_url = url or "https://item.travelpick24.com"
        try:
            res = self.verifier.verify_wordpress(target_url)
            screenshot = res.get("screenshot")
            status_icon = "✅" if res["verified"] else "❌"
            msg = (
                f"{status_icon} <b>[AAOS WordPress 브라우저 DOM 검증 결과]</b>\n\n"
                f"• <b>대상 URL:</b> {target_url}\n"
                f"• <b>검증 상태:</b> <b>{res['status']}</b>\n"
                f"• <b>확인된 타이틀:</b> <b>{res.get('rendered_title', 'N/A')}</b>\n"
                f"• <b>발견된 이미지:</b> {res.get('images_found', 0)}개 정상 렌더링\n"
                f"• <b>상세:</b> <i>{res['details']}</i>\n"
                f"• <b>캡처 스크린샷:</b> <code>{os.path.basename(screenshot) if screenshot else 'None'}</code>"
            )
            return msg, screenshot
        except Exception as e:
            return f"❌ <b>[WordPress 검증 실패]</b> {e}", None

    async def handle_check_instagram(self, url: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Runs Playwright verification on Instagram post.
        Returns (message, screenshot_path).
        """
        target_url = url or "https://www.instagram.com"
        try:
            res = self.verifier.verify_instagram(target_url)
            screenshot = res.get("screenshot")
            status_icon = "✅" if res["verified"] else "❌"
            msg = (
                f"{status_icon} <b>[AAOS Instagram 브라우저 DOM 검증 결과]</b>\n\n"
                f"• <b>URL:</b> {target_url}\n"
                f"• <b>검증 상태:</b> <b>{res['status']}</b>\n"
                f"• <b>판정 결과:</b> {'정상 접근 확인됨' if res['verified'] else '게시물 미발견 또는 오류'}\n"
                f"• <b>상세:</b> <i>{res['details']}</i>\n"
                f"• <b>캡처 스크린샷:</b> <code>{os.path.basename(screenshot) if screenshot else 'None'}</code>"
            )
            return msg, screenshot
        except Exception as e:
            return f"❌ <b>[Instagram 검증 실패]</b> {e}", None

    async def handle_retry_failed(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Finds failed or verification_failed jobs and triggers recovery.
        """
        try:
            failed_jobs = AAOSJobService.get_recent_failed_jobs(limit=10)
            if not failed_jobs:
                return "✅ <b>[재시도 대상 없음]</b>\n현재 실패 상태로 기록된 작업이 없습니다. 모든 시스템이 정상입니다!", None

            retried_count = 0
            for job in failed_jobs:
                # Increment retry and reset status to PENDING
                AAOSJobService.mark_in_progress(job["id"])
                retried_count += 1

            msg = (
                f"🔄 <b>[AAOS 실패 작업 복구 및 재시도 실행]</b>\n\n"
                f"총 <b>{retried_count}건</b>의 실패 작업을 복구 큐에 재등록했습니다.\n"
                f"자동 복구 에이전트(RecoveryAgent)가 재발행 및 실시간 검증을 진행합니다."
            )
            return msg, None
        except Exception as e:
            return f"❌ <b>[재시도 실패]</b> {e}", None

    async def handle_log(self, limit: int = 10) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Retrieves the last N execution and verification logs.
        """
        try:
            logs = AAOSJobService.get_recent_logs(limit=limit)
            if not logs:
                return "📋 <b>[AAOS 실행 로그]</b>\n기록된 실행 로그가 아직 없습니다.", None

            lines = [f"📋 <b>[AAOS 최근 실행 로그 (최신 {len(logs)}건)]</b>\n"]
            for log in logs:
                time_str = log.get("created_at", "")[:19].replace("T", " ")
                err_code = log.get("error_code") or "OK"
                dur = log.get("duration_ms", 0)
                msg = log.get("error_message") or "정상 완료"
                lines.append(
                    f"• <code>[{time_str}]</code> Job #{log['job_id']}\n"
                    f"  상태: <b>{err_code}</b> ({dur}ms) | 재시도: {log.get('retry_count', 0)}회\n"
                    f"  내용: <i>{msg[:50]}</i>"
                )

            return "\n".join(lines), None
        except Exception as e:
            return f"❌ <b>[로그 조회 실패]</b> {e}", None

    async def handle_sites(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Returns full list of 8 WordPress blog addresses and configurations.
        """
        try:
            msg = blog_healer.format_sites_telegram_message()
            return msg, None
        except Exception as e:
            logger.error(f"Error in handle_sites: {e}", exc_info=True)
            return f"❌ <b>[블로그 주소 조회 실패]</b> {e}", None

    async def handle_threads_all(self) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Returns full list of 7 Threads accounts and profile/bridge links.
        """
        try:
            msg = blog_healer.format_threads_telegram_message()
            return msg, None
        except Exception as e:
            logger.error(f"Error in handle_threads_all: {e}", exc_info=True)
            return f"❌ <b>[스레드 주소 조회 실패]</b> {e}", None

    async def handle_audit_blogs(self, limit_per_site: int = 10) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Runs full audit across all 8 blogs for missing photos, duplicate titles, and content anomalies.
        """
        try:
            # Run in thread pool to prevent blocking asyncio loop
            summary = await asyncio.to_thread(blog_healer.audit_all, limit_per_site)
            msg = blog_healer.format_audit_telegram_report(summary)
            return msg, None
        except Exception as e:
            logger.error(f"Error in handle_audit_blogs: {e}", exc_info=True)
            return f"❌ <b>[블로그 자체검수 실패]</b> {e}", None

    async def handle_heal_blogs(self, limit_per_site: int = 10) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Runs automated self-healing across all 8 blogs.
        """
        try:
            summary = await asyncio.to_thread(blog_healer.heal_all, limit_per_site)
            msg = blog_healer.format_heal_telegram_report(summary)
            return msg, None
        except Exception as e:
            logger.error(f"Error in handle_heal_blogs: {e}", exc_info=True)
            return f"❌ <b>[블로그 자가복구 실패]</b> {e}", None


control_center = TelegramControlCenter()
