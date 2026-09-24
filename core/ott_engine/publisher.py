# -*- coding: utf-8 -*-
"""
WordPress REST API Publisher for EnterPick24.
Handles featured media upload, category tagging, and idempotent post publishing.
"""

import logging
import os
from typing import Dict, Any, Optional
import httpx
from core.ott_engine.config import WP_URL, WP_USER, WP_PASS

logger = logging.getLogger("ott_publisher")


class OTTPublisher:
    """Publishes OTT magazine articles to EnterPick24 WordPress site."""

    def __init__(self, wp_url: str = WP_URL, user: str = WP_USER, password: str = WP_PASS):
        self.wp_url = wp_url.rstrip("/")
        self.auth = (user, password)
        self.posts_endpoint = f"{self.wp_url}/wp-json/wp/v2/posts"
        self.media_endpoint = f"{self.wp_url}/wp-json/wp/v2/media"

    def upload_featured_image(self, image_url: str, title: str) -> Optional[int]:
        """
        Downloads image from URL and uploads to WordPress media library.
        Returns the created media ID.
        """
        if not image_url:
            return None

        try:
            # Download image bytes
            with httpx.Client(timeout=15.0) as client:
                img_res = client.get(image_url)
                if img_res.status_code != 200:
                    logger.warning(f"Failed to download image from {image_url}")
                    return None
                img_bytes = img_res.content

            # Determine filename
            ext = "jpg"
            if ".png" in image_url.lower():
                ext = "png"
            elif ".webp" in image_url.lower():
                ext = "webp"
            filename = f"enterpick_{abs(hash(title)) % 100000}.{ext}"

            # Upload to WordPress
            headers = {
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": f"image/{'png' if ext == 'png' else 'jpeg'}"
            }
            with httpx.Client(timeout=25.0) as client:
                upload_res = client.post(
                    self.media_endpoint,
                    content=img_bytes,
                    headers=headers,
                    auth=self.auth
                )
                if upload_res.status_code in [200, 201]:
                    media_data = upload_res.json()
                    media_id = media_data.get("id")
                    logger.info(f"Uploaded featured media ID: {media_id}")
                    return media_id
                else:
                    logger.warning(f"Media upload failed: {upload_res.status_code} - {upload_res.text[:200]}")
                    return None
        except Exception as e:
            logger.error(f"Error uploading featured image: {e}")
            return None

    def publish_article(
        self,
        article_data: Dict[str, Any],
        status: str = "publish",
        categories: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Publishes article to EnterPick24 WordPress.
        """
        title = article_data.get("title")
        content = article_data.get("content")
        img_url = article_data.get("featured_image_url")

        # 1. Upload Featured Media
        media_id = self.upload_featured_image(img_url, title)

        # 2. Prepare payload
        payload = {
            "title": title,
            "content": content,
            "status": status,
        }
        if media_id:
            payload["featured_media"] = media_id
        if categories:
            payload["categories"] = categories

        # 3. Post to WordPress
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(self.posts_endpoint, json=payload, auth=self.auth)
                if res.status_code not in [200, 201]:
                    logger.error(f"Post publish failed: {res.status_code} - {res.text[:300]}")
                    return {
                        "success": False,
                        "status_code": res.status_code,
                        "error": res.text[:300]
                    }

                data = res.json()
                post_id = data.get("id")
                link = data.get("link")
                logger.info(f"Successfully published post #{post_id}: {link}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "link": link,
                    "status": data.get("status"),
                    "title": title,
                    "featured_media": media_id
                }
        except Exception as e:
            logger.error(f"Exception publishing to WordPress: {e}")
            return {
                "success": False,
                "error": str(e)
            }
