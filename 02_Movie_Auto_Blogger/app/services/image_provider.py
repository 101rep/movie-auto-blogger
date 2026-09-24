"""Universal Multi-Source Image Provider Service.

Provides high-resolution, copyright-safe, contextual imagery across all blog verticals:
1. Kakao Daum Image Search API (for Korean commerce products, models, real news, institutions)
2. Pexels API (for aesthetic desk setups, lifestyle, business, tech photography)
3. Pixabay API (for editorial finance, transit, real estate, asian lifestyle)
"""
import re
import urllib.parse
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("image_provider")


class ImageResult(BaseModel):
    url: str
    thumb_url: Optional[str] = None
    alt: str
    source: str
    width: Optional[int] = None
    height: Optional[int] = None


class ImageProviderService:
    """Unified image sourcing engine integrating Kakao, Pexels, and Pixabay."""

    def __init__(self):
        self.settings = get_settings()
        self.kakao_key = self.settings.KAKAO_REST_API_KEY
        self.pexels_key = self.settings.PEXELS_API_KEY
        self.pixabay_key = self.settings.PIXABAY_API_KEY

    async def search_kakao_image(self, query: str) -> Optional[ImageResult]:
        """Search Daum/Kakao Image API for Korean commercial products and news."""
        if not self.kakao_key:
            return None

        clean_query = re.sub(r"[^\w\s가-힣0-9a-zA-Z]", " ", query).strip()
        url = "https://dapi.kakao.com/v2/search/image"
        headers = {"Authorization": f"KakaoAK {self.kakao_key}"}
        params = {"query": clean_query, "size": 10, "sort": "accuracy"}

        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    docs = data.get("documents", [])
                    # Pick an image with good dimensions (width >= 500)
                    for doc in docs:
                        w = doc.get("width", 0)
                        h = doc.get("height", 0)
                        img_url = doc.get("image_url", "")
                        if img_url and img_url.startswith("http") and not img_url.endswith(".gif"):
                            if w >= 400 or w == 0:
                                return ImageResult(
                                    url=img_url,
                                    thumb_url=doc.get("thumbnail_url"),
                                    alt=f"{clean_query} 실물 이미지",
                                    source="Kakao",
                                    width=w,
                                    height=h
                                )
                    if docs:
                        return ImageResult(
                            url=docs[0]["image_url"],
                            thumb_url=docs[0].get("thumbnail_url"),
                            alt=f"{clean_query} 이미지",
                            source="Kakao"
                        )
        except Exception as e:
            logger.warning("Kakao image search failed for '%s': %s", query, e)

        return None

    async def search_pexels_image(self, english_query: str) -> Optional[ImageResult]:
        """Search Pexels API for lifestyle and editorial photography."""
        if not self.pexels_key:
            return None

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_key}
        params = {"query": english_query, "per_page": 10, "orientation": "landscape"}

        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                res = await client.get(url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    photos = data.get("photos", [])
                    if photos:
                        p = photos[0]
                        src = p.get("src", {})
                        best_url = src.get("large2x") or src.get("large") or src.get("original")
                        return ImageResult(
                            url=best_url,
                            thumb_url=src.get("medium"),
                            alt=p.get("alt") or english_query,
                            source="Pexels",
                            width=p.get("width"),
                            height=p.get("height")
                        )
        except Exception as e:
            logger.warning("Pexels image search failed for '%s': %s", english_query, e)

        return None

    async def search_pixabay_image(self, query: str) -> Optional[ImageResult]:
        """Search Pixabay API for royalty-free stock imagery."""
        if not self.pixabay_key:
            return None

        url = "https://pixabay.com/api/"
        params = {
            "key": self.pixabay_key,
            "q": urllib.parse.quote(query),
            "image_type": "photo",
            "orientation": "horizontal",
            "per_page": 10,
            "safesearch": "true"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    hits = data.get("hits", [])
                    if hits:
                        h = hits[0]
                        return ImageResult(
                            url=h.get("largeImageURL") or h.get("webformatURL"),
                            thumb_url=h.get("previewURL"),
                            alt=h.get("tags") or query,
                            source="Pixabay",
                            width=h.get("imageWidth"),
                            height=h.get("imageHeight")
                        )
        except Exception as e:
            logger.warning("Pixabay image search failed for '%s': %s", query, e)

        return None

    async def get_product_image(self, product_name: str, category: str = "") -> Optional[str]:
        """Get authentic product picture via Kakao, falling back to Pexels desk setup."""
        # 1. Try Kakao for exact Korean product
        kakao_res = await self.search_kakao_image(f"{product_name} 실물")
        if not kakao_res:
            kakao_res = await self.search_kakao_image(product_name)

        if kakao_res and kakao_res.url:
            return kakao_res.url

        # 2. Fallback to English Pexels/Pixabay lifestyle
        query_map = {
            "마우스": "ergonomic mouse computer desk setup",
            "타이머": "pomodoro desk timer study productivity",
            "조명": "monitor light bar desk workspace",
            "청소기": "robot vacuum cleaner modern home",
            "스피커": "bluetooth speaker modern desk audio",
            "가습기": "ultrasonic humidifier cozy bedroom",
            "이어폰": "wireless earbuds audio music tech",
            "키보드": "mechanical keyboard workstation desk"
        }
        eng_q = "desk setup gadget tech productivity"
        for kw, q in query_map.items():
            if kw in product_name:
                eng_q = q
                break

        pex_res = await self.search_pexels_image(eng_q)
        if pex_res and pex_res.url:
            return pex_res.url

        pix_res = await self.search_pixabay_image(eng_q)
        if pix_res and pix_res.url:
            return pix_res.url

        return None

    async def get_news_image(self, title: str, category: str = "") -> Optional[str]:
        """Get editorial news image (finance, real estate, tech, society)."""
        cat_lower = category.lower() if category else ""
        eng_q = "korea economy financial market business news"

        if "금융" in category or any(k in title for k in ["금리", "환율", "은행", "주식", "대출", "증시"]):
            eng_q = "bank interest rate financial charts money economy"
        elif "부동산" in category or any(k in title for k in ["청약", "아파트", "전세", "주택", "재건축", "분양"]):
            eng_q = "modern apartment buildings architecture real estate Seoul"
        elif "테크" in category or any(k in title for k in ["AI", "인공지능", "반도체", "로봇", "소프트웨어", "칩"]):
            eng_q = "artificial intelligence microchip data technology future"
        elif "사회" in category or any(k in title for k in ["세금", "연말정산", "건강보험", "국민연금", "일자리"]):
            eng_q = "business people office document statistics meeting"

        # 1. Pexels high-res editorial
        pex_res = await self.search_pexels_image(eng_q)
        if pex_res and pex_res.url:
            return pex_res.url

        # 2. Pixabay fallback
        pix_res = await self.search_pixabay_image(eng_q)
        if pix_res and pix_res.url:
            return pix_res.url

        # 3. Kakao fallback
        kakao_res = await self.search_kakao_image(f"{title[:20]} 보도")
        if kakao_res and kakao_res.url:
            return kakao_res.url

        return None

    async def get_welfare_image(self, title: str, category: str = "") -> Optional[str]:
        """Get empathetic persona lifestyle image for welfare policy guides."""
        eng_q = "Korean lifestyle happy people family community"

        if any(k in title for k in ["청년", "월세", "자취", "원룸", "장학금", "취업"]):
            eng_q = "young adult student studying laptop room apartment"
        elif any(k in title for k in ["시니어", "어르신", "노인", "일자리", "기초연금", "소상공인"]):
            eng_q = "active senior citizen smiling happy community"
        elif any(k in title for k in ["교통", "패스", "K-패스", "지하철", "버스", "환급"]):
            eng_q = "city subway train transit commuter bus commute"
        elif any(k in title for k in ["아이", "출산", "육아", "부모", "양육", "돌봄"]):
            eng_q = "family mother father child smiling together cozy home"

        pex_res = await self.search_pexels_image(eng_q)
        if pex_res and pex_res.url:
            return pex_res.url

        pix_res = await self.search_pixabay_image(eng_q)
        if pix_res and pix_res.url:
            return pix_res.url

        return None

    async def get_entertainment_image(self, title: str) -> Optional[str]:
        """Get entertainment / K-culture image."""
        kakao_res = await self.search_kakao_image(f"{title} 방송")
        if kakao_res and kakao_res.url:
            return kakao_res.url

        pex_res = await self.search_pexels_image("concert stage lights kpop music performance")
        if pex_res and pex_res.url:
            return pex_res.url

        return None


image_provider = ImageProviderService()
