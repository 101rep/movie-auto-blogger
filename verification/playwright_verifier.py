"""
AAOS Playwright Browser Verification Layer
Validates live rendered DOM on Threads, Instagram, and WordPress.
Captures timestamped screenshots on success and failure.
Uses isolated ThreadPoolExecutor to prevent event-loop collisions in asyncio environments.
"""

import os
import sys
import time
import logging
import asyncio
import concurrent.futures
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from verification.config import SCREENSHOTS_DIR, DEFAULT_TIMEOUT_MS, HEADLESS, VIEWPORT, USER_AGENT

logger = logging.getLogger("AAOSPlaywrightVerifier")

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="aaos_playwright")

class PlaywrightVerifier:
    def __init__(self, headless: bool = HEADLESS, timeout_ms: int = DEFAULT_TIMEOUT_MS):
        self.headless = headless
        self.timeout_ms = timeout_ms

    def _generate_screenshot_path(self, platform: str, status: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_{status}_{timestamp}.png"
        return str(SCREENSHOTS_DIR / filename)

    # ── Thread-isolated Synchronous Implementation ────────────────────────────

    def _verify_threads_impl(self, url: str, expected_snippet: Optional[str] = None) -> Dict[str, Any]:
        screenshot_path = ""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    viewport=VIEWPORT,
                    user_agent=USER_AGENT,
                    locale="ko-KR"
                )
                page = context.new_page()
                page.route("**/*.{mp4,webm,ogg,wav,mp3}", lambda route: route.abort())

                logger.info(f"Navigating to Threads URL: {url}")
                response = page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)

                if response and response.status in [404, 410, 500]:
                    screenshot_path = self._generate_screenshot_path("threads", "http_error")
                    page.screenshot(path=screenshot_path)
                    browser.close()
                    return {
                        "verified": False,
                        "status": f"HTTP_{response.status}",
                        "url": url,
                        "screenshot": screenshot_path,
                        "details": f"Server returned error code {response.status}"
                    }

                page_text = page.content().lower()
                error_indicators = [
                    "죄송합니다. 페이지를 사용할 수 없습니다",
                    "page not found",
                    "content not available",
                    "this page isn't available",
                    "삭제된 게시물"
                ]

                for indicator in error_indicators:
                    if indicator in page_text:
                        screenshot_path = self._generate_screenshot_path("threads", "not_found")
                        page.screenshot(path=screenshot_path)
                        browser.close()
                        return {
                            "verified": False,
                            "status": "NOT_FOUND",
                            "url": url,
                            "screenshot": screenshot_path,
                            "details": f"Detected error marker: '{indicator}'"
                        }

                if expected_snippet:
                    clean_snippet = expected_snippet.strip().lower()
                    if clean_snippet not in page_text:
                        screenshot_path = self._generate_screenshot_path("threads", "snippet_mismatch")
                        page.screenshot(path=screenshot_path)
                        browser.close()
                        return {
                            "verified": False,
                            "status": "CONTENT_MISMATCH",
                            "url": url,
                            "screenshot": screenshot_path,
                            "details": f"Expected snippet '{expected_snippet[:50]}...' not found in page DOM"
                        }

                screenshot_path = self._generate_screenshot_path("threads", "success")
                page.screenshot(path=screenshot_path)
                browser.close()
                return {
                    "verified": True,
                    "status": "SUCCESS",
                    "url": url,
                    "screenshot": screenshot_path,
                    "details": "Threads post rendered and confirmed live in DOM"
                }

        except PlaywrightTimeoutError:
            return {
                "verified": False,
                "status": "TIMEOUT",
                "url": url,
                "screenshot": screenshot_path,
                "details": f"Timed out after {self.timeout_ms}ms waiting for Threads page"
            }
        except Exception as e:
            logger.error(f"Error verifying Threads post: {e}", exc_info=True)
            return {
                "verified": False,
                "status": "ERROR",
                "url": url,
                "screenshot": screenshot_path,
                "details": str(e)
            }

    def _verify_wordpress_impl(self, url: str, expected_title: Optional[str] = None) -> Dict[str, Any]:
        screenshot_path = ""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(viewport=VIEWPORT, user_agent=USER_AGENT)
                page = context.new_page()

                logger.info(f"Navigating to WordPress URL: {url}")
                response = page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")
                page.wait_for_timeout(1500)

                status_code = response.status if response else 0
                if status_code in [404, 403, 500, 502, 503]:
                    screenshot_path = self._generate_screenshot_path("wordpress", f"http_{status_code}")
                    page.screenshot(path=screenshot_path)
                    browser.close()
                    return {
                        "verified": False,
                        "status": f"HTTP_{status_code}",
                        "url": url,
                        "screenshot": screenshot_path,
                        "details": f"WordPress server returned {status_code}"
                    }

                title_el = page.query_selector("h1, .entry-title, .post-title, title")
                rendered_title = title_el.inner_text().strip() if title_el else ""

                if not rendered_title:
                    screenshot_path = self._generate_screenshot_path("wordpress", "no_title")
                    page.screenshot(path=screenshot_path)
                    browser.close()
                    return {
                        "verified": False,
                        "status": "NO_TITLE",
                        "url": url,
                        "screenshot": screenshot_path,
                        "details": "No heading or post title found in DOM"
                    }

                if expected_title:
                    if expected_title.strip().lower() not in rendered_title.lower():
                        screenshot_path = self._generate_screenshot_path("wordpress", "title_mismatch")
                        page.screenshot(path=screenshot_path)
                        browser.close()
                        return {
                            "verified": False,
                            "status": "TITLE_MISMATCH",
                            "url": url,
                            "screenshot": screenshot_path,
                            "details": f"Expected title '{expected_title}' does not match '{rendered_title}'"
                        }

                images = page.query_selector_all("article img, .entry-content img, .post-thumbnail img, img")
                image_count = len(images)

                screenshot_path = self._generate_screenshot_path("wordpress", "success")
                page.screenshot(path=screenshot_path)
                browser.close()
                return {
                    "verified": True,
                    "status": "SUCCESS",
                    "url": url,
                    "screenshot": screenshot_path,
                    "rendered_title": rendered_title,
                    "images_found": image_count,
                    "details": f"Post verified successfully. Title: '{rendered_title}', Images: {image_count}"
                }

        except PlaywrightTimeoutError:
            return {
                "verified": False,
                "status": "TIMEOUT",
                "url": url,
                "screenshot": screenshot_path,
                "details": f"Timed out after {self.timeout_ms}ms loading WordPress post"
            }
        except Exception as e:
            logger.error(f"Error verifying WordPress post: {e}", exc_info=True)
            return {
                "verified": False,
                "status": "ERROR",
                "url": url,
                "screenshot": screenshot_path,
                "details": str(e)
            }

    def _verify_instagram_impl(self, url: str) -> Dict[str, Any]:
        screenshot_path = ""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(viewport=VIEWPORT, user_agent=USER_AGENT)
                page = context.new_page()

                logger.info(f"Navigating to Instagram URL: {url}")
                response = page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)

                page_text = page.content().lower()
                error_indicators = [
                    "죄송합니다. 페이지를 사용할 수 없습니다",
                    "sorry, this page isn't available",
                    "the link you followed may be broken",
                    "페이지가 삭제되었거나"
                ]

                for indicator in error_indicators:
                    if indicator in page_text:
                        screenshot_path = self._generate_screenshot_path("instagram", "not_found")
                        page.screenshot(path=screenshot_path)
                        browser.close()
                        return {
                            "verified": False,
                            "status": "NOT_FOUND",
                            "url": url,
                            "screenshot": screenshot_path,
                            "details": f"Detected error marker: '{indicator}'"
                        }

                screenshot_path = self._generate_screenshot_path("instagram", "success")
                page.screenshot(path=screenshot_path)
                browser.close()
                return {
                    "verified": True,
                    "status": "SUCCESS",
                    "url": url,
                    "screenshot": screenshot_path,
                    "details": "Instagram post verified accessible"
                }

        except PlaywrightTimeoutError:
            return {
                "verified": False,
                "status": "TIMEOUT",
                "url": url,
                "screenshot": screenshot_path,
                "details": f"Timed out after {self.timeout_ms}ms loading Instagram post"
            }
        except Exception as e:
            logger.error(f"Error verifying Instagram post: {e}", exc_info=True)
            return {
                "verified": False,
                "status": "ERROR",
                "url": url,
                "screenshot": screenshot_path,
                "details": str(e)
            }

    # ── Safe Universal Public API (Sync & Async) ──────────────────────────────

    def verify_threads(self, url: str, expected_snippet: Optional[str] = None) -> Dict[str, Any]:
        future = _executor.submit(self._verify_threads_impl, url, expected_snippet)
        return future.result()

    def verify_wordpress(self, url: str, expected_title: Optional[str] = None) -> Dict[str, Any]:
        future = _executor.submit(self._verify_wordpress_impl, url, expected_title)
        return future.result()

    def verify_instagram(self, url: str) -> Dict[str, Any]:
        future = _executor.submit(self._verify_instagram_impl, url)
        return future.result()

    async def async_verify_threads(self, url: str, expected_snippet: Optional[str] = None) -> Dict[str, Any]:
        return await asyncio.to_thread(self._verify_threads_impl, url, expected_snippet)

    async def async_verify_wordpress(self, url: str, expected_title: Optional[str] = None) -> Dict[str, Any]:
        return await asyncio.to_thread(self._verify_wordpress_impl, url, expected_title)

    async def async_verify_instagram(self, url: str) -> Dict[str, Any]:
        return await asyncio.to_thread(self._verify_instagram_impl, url)
