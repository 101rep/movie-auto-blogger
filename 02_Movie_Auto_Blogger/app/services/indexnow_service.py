"""Search Engine Indexing & IndexNow ping service."""
from typing import Dict, List, Optional
import httpx

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("indexnow_service")

INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://searchadvisor.naver.com/indexnow",
    "https://www.bing.com/indexnow"
]


class IndexNowService:
    """Service to notify search engines (Naver, Bing, Google, Yandex) about newly published URLs."""

    def __init__(self, host: Optional[str] = None, key: Optional[str] = None) -> None:
        settings = get_settings()
        raw_url = (host or settings.WORDPRESS_URL or "https://trendspot24.com").rstrip("/")
        self.host = raw_url.replace("https://", "").replace("http://", "").split("/")[0]
        self.key = key or getattr(settings, "INDEXNOW_KEY", None) or "trendspot24indexnowkey20260915"
        self.sitemap_url = f"{raw_url}/wp-sitemap.xml"

    async def submit_urls(self, url_list: List[str]) -> Dict[str, bool]:
        """Submit URLs to IndexNow search engine protocol endpoints."""
        if not url_list:
            return {}

        results: Dict[str, bool] = {}
        payload = {
            "host": self.host,
            "key": self.key,
            "keyLocation": f"https://{self.host}/{self.key}.txt",
            "urlList": url_list
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in INDEXNOW_ENDPOINTS:
                try:
                    res = await client.post(
                        endpoint,
                        json=payload,
                        headers={"Content-Type": "application/json; charset=utf-8"}
                    )
                    success = res.status_code in (200, 202)
                    results[endpoint] = success
                    if success:
                        logger.info("IndexNow submitted successfully to %s: %s", endpoint, url_list)
                    else:
                        logger.warning("IndexNow submission returned status %d from %s", res.status_code, endpoint)
                except Exception as e:
                    logger.warning("IndexNow submission failed to %s: %s", endpoint, str(e))
                    results[endpoint] = False

        return results

    async def ping_sitemaps(self) -> Dict[str, bool]:
        """Ping search engines with the updated sitemap URL."""
        ping_urls = [
            f"https://www.bing.com/ping?sitemap={self.sitemap_url}"
        ]
        results = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            for purl in ping_urls:
                try:
                    res = await client.get(purl)
                    results[purl] = (res.status_code == 200)
                except Exception as e:
                    logger.debug("Sitemap ping failed for %s: %s", purl, str(e))
                    results[purl] = False
        return results
