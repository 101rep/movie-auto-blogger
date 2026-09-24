"""WordPress REST API Publisher for Trust Pages.
Deploys and updates pages (/about-us, /privacy-policy, /terms, etc.) across the 8 WordPress blogs.
"""
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
import aiohttp

from trust_page_generator.config import BLOG_REGISTRY
from trust_page_generator.database.models import TrustPage, BlogIdentity
from trust_page_generator.database.session import SessionLocal

logger = logging.getLogger("trust_page_generator.publisher")


class WordPressTrustPagePublisher:
    """Manages publishing of static Trust Pages to WordPress via REST API."""

    def __init__(self, blog_config: Dict[str, Any]):
        self.blog = blog_config
        self.site_id = blog_config["site_id"]
        self.domain = blog_config["url"].rstrip("/")
        self.api_url = f"{self.domain}/wp-json/wp/v2"
        self.auth_header = self._build_auth_header(blog_config["user"], blog_config["pass"])

    @staticmethod
    def _build_auth_header(username: str, app_pass: str) -> str:
        clean_pass = app_pass.replace(" ", "")
        token = f"{username}:{clean_pass}"
        encoded = base64.b64encode(token.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    async def find_existing_page(self, slug: str) -> Optional[int]:
        """Check if a page with the given slug already exists on WordPress."""
        url = f"{self.api_url}/pages?slug={slug}&context=edit"
        headers = {"Authorization": self.auth_header}
        try:
            timeout = aiohttp.ClientTimeout(total=12)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        pages = await resp.json()
                        if pages and isinstance(pages, list) and len(pages) > 0:
                            return pages[0].get("id")
        except Exception as e:
            logger.warning(f"[{self.blog['name']}] Failed checking slug '{slug}': {e}")
        return None

    async def deploy_page(
        self,
        title: str,
        slug: str,
        html_content: str,
        status: str = "publish"
    ) -> Tuple[bool, Optional[int], Optional[str], Optional[str]]:
        """Create or update a WordPress Trust Page via REST API."""
        existing_id = await self.find_existing_page(slug)
        headers = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json"
        }
        payload = {
            "title": title,
            "slug": slug,
            "content": html_content,
            "status": status
        }

        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if existing_id:
                    # Update existing page
                    update_url = f"{self.api_url}/pages/{existing_id}"
                    async with session.post(update_url, headers=headers, json=payload) as resp:
                        if resp.status in (200, 201):
                            data = await resp.json()
                            logger.info(f"[{self.blog['name']}] Page updated: {slug} (ID: {existing_id})")
                            return True, existing_id, data.get("link"), "UPDATED"
                        else:
                            err = await resp.text()
                            logger.error(f"[{self.blog['name']}] Page update failed ({resp.status}): {err[:150]}")
                            return False, existing_id, None, f"HTTP {resp.status}"
                else:
                    # Create new page
                    create_url = f"{self.api_url}/pages"
                    async with session.post(create_url, headers=headers, json=payload) as resp:
                        if resp.status in (200, 201):
                            data = await resp.json()
                            new_id = data.get("id")
                            logger.info(f"[{self.blog['name']}] Page created: {slug} (ID: {new_id})")
                            return True, new_id, data.get("link"), "CREATED"
                        else:
                            err = await resp.text()
                            logger.error(f"[{self.blog['name']}] Page create failed ({resp.status}): {err[:150]}")
                            return False, None, None, f"HTTP {resp.status}"
        except Exception as e:
            logger.error(f"[{self.blog['name']}] Exception deploying {slug}: {e}")
            return False, None, None, str(e)

    async def deploy_all_for_blog(self, dry_run: bool = False) -> Dict[str, Any]:
        """Deploy all 8 Trust Pages for this blog from the database."""
        db = SessionLocal()
        results: Dict[str, Any] = {
            "blog_name": self.blog["name"],
            "site_id": self.site_id,
            "domain": self.domain,
            "success_count": 0,
            "failed_count": 0,
            "details": []
        }

        try:
            pages = db.query(TrustPage).filter(TrustPage.blog_id == self.site_id).all()
            for p in pages:
                if dry_run:
                    results["details"].append({
                        "slug": p.slug,
                        "title": p.title,
                        "status": "DRY_RUN_OK",
                        "url": f"{self.domain}/{p.slug}/"
                    })
                    results["success_count"] += 1
                    continue

                success, page_id, permalink, action = await self.deploy_page(
                    title=p.title,
                    slug=p.slug,
                    html_content=p.content,
                    status="publish"
                )

                if success:
                    p.wp_page_id = page_id
                    p.status = "PUBLISHED"
                    results["success_count"] += 1
                    results["details"].append({
                        "slug": p.slug,
                        "title": p.title,
                        "page_id": page_id,
                        "action": action,
                        "url": permalink
                    })
                else:
                    p.status = "FAILED"
                    results["failed_count"] += 1
                    results["details"].append({
                        "slug": p.slug,
                        "title": p.title,
                        "error": action
                    })
            db.commit()
        finally:
            db.close()

        return results
