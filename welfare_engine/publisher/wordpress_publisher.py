"""WordPress REST API Publisher for Welfare Engine V1.0.
Dedicated publisher exclusively for the 3 welfare blogs (Site 5, Site 6, Site 7).
Handles media upload, taxonomy resolution, post scheduling, and atomic verification.
"""
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import aiohttp

from welfare_engine.config import WelfareBlogConfig
from welfare_engine.database.models import WelfarePublication

logger = logging.getLogger("welfare_engine.publisher")


class WordPressWelfarePublisher:
    """Publishes welfare articles and card news to designated WordPress sites."""

    def __init__(self, blog: WelfareBlogConfig):
        self.blog = blog
        self.base_url = blog.domain.rstrip("/")
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.auth_header = self._build_auth_header(blog.wp_user, blog.wp_pass)

    @staticmethod
    def _build_auth_header(username: str, app_pass: str) -> str:
        clean_pass = app_pass.replace(" ", "")
        token = f"{username}:{clean_pass}"
        encoded = base64.b64encode(token.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    async def upload_media(self, image_path: Path) -> Optional[int]:
        """Upload 1080x1080 thumbnail to WordPress media library."""
        if not image_path.exists():
            logger.error(f"Image file does not exist: {image_path}")
            return None

        url = f"{self.api_url}/media"
        filename = image_path.name
        headers = {
            "Authorization": self.auth_header,
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/png"
        }

        try:
            with open(image_path, "rb") as f:
                img_data = f.read()

            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, data=img_data) as resp:
                    if resp.status in (200, 201):
                        data = await resp.json()
                        media_id = data.get("id")
                        logger.info(f"[{self.blog.blog_key}] Media uploaded successfully: ID {media_id}")
                        return media_id
                    else:
                        err_text = await resp.text()
                        logger.warning(f"[{self.blog.blog_key}] Media upload failed ({resp.status}): {err_text[:200]}")
        except Exception as e:
            logger.error(f"[{self.blog.blog_key}] Exception during media upload: {e}")

        return None

    async def get_or_create_category(self, cat_name: str) -> Optional[int]:
        """Resolve or dynamically create a category ID."""
        headers = {"Authorization": self.auth_header}
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # 1. Search existing
                search_url = f"{self.api_url}/categories?search={cat_name}"
                async with session.get(search_url, headers=headers) as resp:
                    if resp.status == 200:
                        categories = await resp.json()
                        for c in categories:
                            if c.get("name") == cat_name:
                                return c.get("id")

                # 2. Create if not found
                create_url = f"{self.api_url}/categories"
                async with session.post(create_url, headers=headers, json={"name": cat_name}) as resp:
                    if resp.status in (200, 201):
                        data = await resp.json()
                        return data.get("id")
        except Exception as e:
            logger.warning(f"[{self.blog.blog_key}] Failed resolving category '{cat_name}': {e}")

        return None

    async def get_or_create_tags(self, tag_names: List[str]) -> List[int]:
        """Resolve or create tag IDs."""
        headers = {"Authorization": self.auth_header}
        tag_ids = []
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                for name in tag_names[:5]:
                    search_url = f"{self.api_url}/tags?search={name}"
                    async with session.get(search_url, headers=headers) as resp:
                        if resp.status == 200:
                            tags = await resp.json()
                            matched = next((t["id"] for t in tags if t.get("name") == name), None)
                            if matched:
                                tag_ids.append(matched)
                                continue

                    # Create
                    create_url = f"{self.api_url}/tags"
                    async with session.post(create_url, headers=headers, json={"name": name}) as resp:
                        if resp.status in (200, 201):
                            data = await resp.json()
                            tag_ids.append(data["id"])
        except Exception as e:
            logger.warning(f"[{self.blog.blog_key}] Failed resolving tags: {e}")

        return tag_ids

    async def publish_article(
        self,
        title: str,
        content_html: str,
        category_name: str,
        tags: List[str],
        image_path: Optional[Path] = None,
        scheduled_at: Optional[datetime] = None,
        is_immediate: bool = False
    ) -> Dict[str, Any]:
        """Publish or schedule post via WordPress REST API."""
        # 1. Upload thumbnail
        media_id = None
        if image_path:
            media_id = await self.upload_media(image_path)

        # 2. Resolve Category & Tags
        cat_id = await self.get_or_create_category(category_name)
        cat_ids = [cat_id] if cat_id else []
        tag_ids = await self.get_or_create_tags(tags)

        # 3. Post Payload
        status = "publish" if is_immediate else "future"
        payload: Dict[str, Any] = {
            "title": title,
            "content": content_html,
            "status": status,
            "categories": cat_ids,
            "tags": tag_ids
        }
        if media_id:
            payload["featured_media"] = media_id

        if not is_immediate and scheduled_at:
            payload["date"] = scheduled_at.strftime("%Y-%m-%dT%H:%M:%S")

        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }

        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"{self.api_url}/posts"
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status in (200, 201):
                        data = await resp.json()
                        post_id = data.get("id")
                        post_url = data.get("link")
                        post_status = data.get("status")
                        logger.info(f"[{self.blog.blog_key}] Post created: ID {post_id}, status: {post_status}, URL: {post_url}")
                        return {
                            "success": True,
                            "post_id": post_id,
                            "post_url": post_url,
                            "post_status": post_status,
                            "media_id": media_id,
                            "scheduled_at": scheduled_at
                        }
                    else:
                        err_text = await resp.text()
                        logger.error(f"[{self.blog.blog_key}] Post creation failed ({resp.status}): {err_text[:250]}")
                        return {
                            "success": False,
                            "error": f"HTTP {resp.status}: {err_text[:250]}"
                        }
        except Exception as e:
            logger.error(f"[{self.blog.blog_key}] Exception during post creation: {e}")
            return {"success": False, "error": str(e)}
