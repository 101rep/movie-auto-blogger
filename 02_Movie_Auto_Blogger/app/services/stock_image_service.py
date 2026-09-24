"""Stock photo service integrating Pexels and Pixabay APIs for high-resolution images."""
from typing import Dict, List, Optional
import httpx
from pydantic import BaseModel

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("stock_image_service")


class StockImage(BaseModel):
    """Normalized stock image structure."""
    url: str
    thumb_url: Optional[str] = None
    alt: str
    photographer: Optional[str] = None
    source: str  # "Pexels" or "Pixabay"


class StockImageService:
    """Service to discover and fetch licensed high-quality photos using Pexels & Pixabay."""

    def __init__(self, pexels_key: Optional[str] = None, pixabay_key: Optional[str] = None):
        settings = get_settings()
        self.pexels_key = pexels_key or settings.PEXELS_API_KEY
        self.pixabay_key = pixabay_key or settings.PIXABAY_API_KEY

    @staticmethod
    def extract_image_id(url: str) -> Optional[str]:
        """Extract unique photo ID from Pexels, Pixabay, or Unsplash URL."""
        if not url:
            return None
        import re
        # Pexels: /photos/31851458/ or pexels-photo-31851458
        m_pex = re.search(r'(?:photos/|pexels-photo-)(\d+)', url)
        if m_pex:
            return f"pexels_{m_pex.group(1)}"
        # Pixabay: /get/xxx_640.jpg or photo/2016/01/... or id in URL
        m_pix = re.search(r'pixabay\.com/.*?([0-9]{5,10})', url)
        if m_pix:
            return f"pixabay_{m_pix.group(1)}"
        # Unsplash: photo-1503899036084-c55cdd92da26
        m_uns = re.search(r'photo-([a-zA-Z0-9_-]{10,40})', url)
        if m_uns:
            return f"unsplash_{m_uns.group(1)}"
        return url.split("?")[0]

    async def search_image(
        self,
        query: str,
        orientation: str = "landscape",
        exclude_urls: Optional[List[str]] = None,
        prefer_page: int = 1,
        preferred_source: Optional[str] = None
    ) -> Optional[StockImage]:
        """Search for a single best-matching image with intelligent balancing between Pexels and Pixabay.
        Enforces strict deduplication by URL and Photo ID: will not return any already used image.
        """
        exclude_raw = exclude_urls or []
        exclude_ids = set()
        exclude_urls_clean = set()

        for u in exclude_raw:
            if not u:
                continue
            exclude_urls_clean.add(u.split("?")[0])
            img_id = self.extract_image_id(u)
            if img_id:
                exclude_ids.add(img_id)

        # Decide source order based on preferred_source
        # If preferred_source is "Pixabay", try Pixabay first, then Pexels
        # If preferred_source is "Pexels", try Pexels first, then Pixabay
        # If None, default to balanced order (or Pixabay first if query involves Asian travel)
        sources = ["Pexels", "Pixabay"]
        if preferred_source == "Pixabay":
            sources = ["Pixabay", "Pexels"]
        elif preferred_source == "Pexels":
            sources = ["Pexels", "Pixabay"]
        else:
            # Check if query matches Asian destinations where Pixabay has superior coverage
            asian_terms = ["thailand", "bangkok", "vietnam", "danang", "hoian", "japan", "osaka", "tokyo", "fukuoka", "korea", "jeju", "busan", "taipei", "taiwan", "asia"]
            if any(term in query.lower() for term in asian_terms):
                sources = ["Pixabay", "Pexels"]

        for source in sources:
            if source == "Pexels" and self.pexels_key:
                for pg in (prefer_page, 2 if prefer_page == 1 else 1, 3):
                    pexels_img = await self._search_pexels(
                        query,
                        orientation=orientation,
                        exclude_urls=exclude_urls_clean,
                        exclude_ids=exclude_ids,
                        page=pg,
                        per_page=20
                    )
                    if pexels_img:
                        return pexels_img

            elif source == "Pixabay" and self.pixabay_key:
                for pg in (prefer_page, 2, 3):
                    pixabay_img = await self._search_pixabay(
                        query,
                        exclude_urls=exclude_urls_clean,
                        exclude_ids=exclude_ids,
                        page=pg,
                        per_page=20
                    )
                    if pixabay_img:
                        return pixabay_img

        logger.info("StockImageService: No new unique image found for '%s' (strict duplicate prevented across both Pexels and Pixabay).", query)
        return None

    async def _search_pexels(
        self,
        query: str,
        orientation: str = "landscape",
        exclude_urls: Optional[set] = None,
        exclude_ids: Optional[set] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Optional[StockImage]:
        """Fetch image via Pexels API with strict deduplication filtering."""
        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query,
            "per_page": per_page,
            "page": page,
            "orientation": orientation
        }
        ex_urls = exclude_urls or set()
        ex_ids = exclude_ids or set()
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    photos = data.get("photos", [])
                    for p in photos:
                        p_id_str = f"pexels_{p.get('id')}"
                        src = p.get("src", {})
                        img_url = src.get("large2x") or src.get("large") or src.get("medium")
                        if not img_url:
                            continue
                        clean_url = img_url.split("?")[0]
                        # Check both direct URL and Photo ID
                        if clean_url in ex_urls or p_id_str in ex_ids:
                            continue

                        return StockImage(
                            url=img_url,
                            thumb_url=src.get("medium"),
                            alt=p.get("alt") or f"{query} 명소 사진",
                            photographer=p.get("photographer", "Pexels Creator"),
                            source="Pexels"
                        )
        except Exception as e:
            logger.warning("Pexels image search failed for '%s' (p.%d): %s", query, page, str(e))
        return None

    async def _search_pixabay(
        self,
        query: str,
        exclude_urls: Optional[set] = None,
        exclude_ids: Optional[set] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Optional[StockImage]:
        """Fetch image via Pixabay API with deduplication filtering."""
        url = "https://pixabay.com/api/"
        params = {
            "key": self.pixabay_key,
            "q": query,
            "image_type": "photo",
            "orientation": "horizontal",
            "page": page,
            "per_page": per_page,
            "safesearch": "true"
        }
        ex_urls = exclude_urls or set()
        ex_ids = exclude_ids or set()
        try:
            async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    hits = data.get("hits", [])
                    for hit in hits:
                        hit_id_str = f"pixabay_{hit.get('id')}"
                        img_url = hit.get("largeImageURL") or hit.get("webformatURL")
                        if not img_url:
                            continue
                        clean_url = img_url.split("?")[0]
                        if clean_url in ex_urls or hit_id_str in ex_ids:
                            continue

                        return StockImage(
                            url=img_url,
                            thumb_url=hit.get("webformatURL"),
                            alt=hit.get("tags") or f"{query} 풍경",
                            photographer=hit.get("user", "Pixabay Creator"),
                            source="Pixabay"
                        )
        except Exception as e:
            logger.warning("Pixabay image search failed for '%s' (p.%d): %s", query, page, str(e))
        return None
