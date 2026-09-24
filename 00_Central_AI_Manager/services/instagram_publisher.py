# -*- coding: utf-8 -*-
"""
Meta Official Instagram Graph API Publisher
- Multi-Image Carousel (4:5 Aspect Ratio) 2-Step Publishing:
    1. Create item containers for each slide: POST /{ig_user_id}/media (is_carousel_item=true)
    2. Create carousel parent container: POST /{ig_user_id}/media (media_type=CAROUSEL, children=...)
    3. Publish container: POST /{ig_user_id}/media_publish (creation_id=...)
- Public Image Hosting Integration (via WordPress media or static web bridge)
- Token & Account Verification
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import httpx

logger = logging.getLogger("InstagramPublisher")

GRAPH_API_VERSION = "v20.0"
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class InstagramPublisher:
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "").strip()
        self.account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()

    def is_configured(self) -> Tuple[bool, str]:
        if not self.access_token or not self.account_id:
            return False, "INSTAGRAM_ACCESS_TOKEN 또는 INSTAGRAM_ACCOUNT_ID가 .env에 설정되지 않았습니다."
        return True, "OK"

    async def verify_account(self) -> Dict[str, Any]:
        """Check Instagram account connection & token validity."""
        ok, msg = self.is_configured()
        if not ok:
            return {"status": "NOT_CONFIGURED", "message": msg}

        url = f"{GRAPH_BASE_URL}/{self.account_id}"
        params = {
            "fields": "id,username,name,profile_picture_url,followers_count",
            "access_token": self.access_token
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "status": "SUCCESS",
                        "account_id": data.get("id"),
                        "username": data.get("username"),
                        "name": data.get("name"),
                        "followers": data.get("followers_count", 0)
                    }
                else:
                    return {
                        "status": "ERROR",
                        "code": res.status_code,
                        "message": res.text[:250]
                    }
            except Exception as e:
                return {"status": "ERROR", "message": str(e)}

    async def upload_image_to_public_host(self, local_img_path: str) -> Optional[str]:
        """
        Upload local image to WordPress Media Library so Instagram Graph API can access public URL.
        """
        from config import settings
        wp_url = "https://item.travelpick24.com/wp-json/wp/v2/media"
        wp_user = "ktaehoon80@gmail.com"
        wp_app_pass = "UWhDnkd8OLpGQ91f8dSx0avk"

        import base64
        auth = "Basic " + base64.b64encode(f"{wp_user}:{wp_app_pass}".encode()).decode()
        headers = {
            "Authorization": auth,
            "Content-Disposition": f'attachment; filename="{os.path.basename(local_img_path)}"',
            "Content-Type": "image/png"
        }

        try:
            with open(local_img_path, "rb") as f:
                img_data = f.read()

            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(wp_url, headers=headers, content=img_data)
                if res.status_code in (200, 201):
                    data = res.json()
                    public_url = data.get("source_url") or data.get("guid", {}).get("rendered")
                    logger.info(f"Image uploaded to public WP media: {public_url}")
                    return public_url
                else:
                    logger.error(f"Failed to upload image to WP media: {res.status_code} - {res.text[:200]}")
        except Exception as e:
            logger.error(f"Image upload exception: {e}")
        return None

    async def publish_carousel(self, image_paths: List[str], caption: str) -> Dict[str, Any]:
        """
        Complete Meta Graph API Carousel Publish Workflow:
        1. Upload images to public URLs (WordPress Media Bridge)
        2. Create child media containers for each image (is_carousel_item=true)
        3. Create parent carousel container with caption
        4. Publish container to Instagram Feed
        """
        ok, msg = self.is_configured()
        if not ok:
            return {"status": "NOT_CONFIGURED", "message": msg}

        if len(image_paths) < 2 or len(image_paths) > 10:
            return {"status": "ERROR", "message": "캐러셀은 최소 2장, 최대 10장의 이미지가 필요합니다."}

        # Step 1: Upload images to public hosting
        logger.info(f"Uploading {len(image_paths)} images to public hosting...")
        public_urls = []
        for p in image_paths:
            pub_url = await self.upload_image_to_public_host(p)
            if pub_url:
                public_urls.append(pub_url)
            else:
                return {"status": "ERROR", "message": f"이미지 호스팅 업로드 실패: {os.path.basename(p)}"}

        async with httpx.AsyncClient(timeout=45.0) as client:
            # Step 2: Create child containers
            child_ids = []
            for idx, img_url in enumerate(public_urls, 1):
                child_url = f"{GRAPH_BASE_URL}/{self.account_id}/media"
                child_payload = {
                    "image_url": img_url,
                    "is_carousel_item": "true",
                    "access_token": self.access_token
                }
                res = await client.post(child_url, params=child_payload)
                if res.status_code == 200:
                    child_id = res.json().get("id")
                    child_ids.append(child_id)
                    logger.info(f"Child container [{idx}/{len(public_urls)}] created: {child_id}")
                else:
                    return {"status": "ERROR", "message": f"하위 컨테이너 생성 실패: {res.text[:250]}"}
                await asyncio.sleep(1)  # Rate-limit safety

            # Step 3: Create parent carousel container
            parent_url = f"{GRAPH_BASE_URL}/{self.account_id}/media"
            parent_payload = {
                "media_type": "CAROUSEL",
                "children": ",".join(child_ids),
                "caption": caption,
                "access_token": self.access_token
            }
            res_parent = await client.post(parent_url, params=parent_payload)
            if res_parent.status_code != 200:
                return {"status": "ERROR", "message": f"캐러셀 부모 컨테이너 생성 실패: {res_parent.text[:250]}"}

            creation_id = res_parent.json().get("id")
            logger.info(f"Parent carousel container created: {creation_id}")

            # Wait for media processing
            await asyncio.sleep(5)

            # Step 4: Publish to Instagram
            publish_url = f"{GRAPH_BASE_URL}/{self.account_id}/media_publish"
            pub_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            res_pub = await client.post(publish_url, params=pub_payload)
            if res_pub.status_code == 200:
                post_data = res_pub.json()
                post_id = post_data.get("id")
                logger.info(f"Instagram Carousel PUBLISHED successfully! Post ID: {post_id}")
                return {
                    "status": "SUCCESS",
                    "post_id": post_id,
                    "slides_count": len(image_paths),
                    "permalink": f"https://www.instagram.com/p/{post_id}/" if post_id else "https://www.instagram.com"
                }
            else:
                return {"status": "ERROR", "message": f"최종 퍼블리시 실패: {res_pub.text[:250]}"}


instagram_publisher = InstagramPublisher()
