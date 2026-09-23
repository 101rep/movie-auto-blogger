import hmac
import hashlib
import time
import requests
from typing import List, Dict, Any, Optional
from config import settings
from domain_types.schemas import ProductDTO
from integrations.interfaces import ProductProvider
from utils.cache import app_cache

class CoupangPartnersAPI(ProductProvider):
    """
    Official Coupang Partners Open API Client.
    Uses HMAC-SHA256 signature authentication according to Coupang Partners developer docs.
    """
    BASE_URL = "https://api-gateway.coupang.com"

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.access_key = access_key or getattr(settings, "COUPANG_ACCESS_KEY", None)
        self.secret_key = secret_key or getattr(settings, "COUPANG_SECRET_KEY", None)

    def _generate_hmac(self, method: str, url: str) -> str:
        datetime_gmt = time.strftime('%y%m%d', time.gmtime()) + 'T' + time.strftime('%H%M%S', time.gmtime()) + 'Z'
        message = datetime_gmt + method + url.split("?")[0]
        if "?" in url:
            message += url[url.index("?"):]

        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f"CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={datetime_gmt}, signature={signature}"

    def search_products(self, query: Optional[str] = None, category: Optional[str] = None, page: int = 1, limit: int = 20) -> List[ProductDTO]:
        cache_key = f"coupang_search:{query or ''}:{category or ''}:{page}:{limit}"
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached

        keyword = query or category or "인기상품"
        if not self.access_key or not self.secret_key:
            # Fallback to mock provider
            from integrations.providers.mock_product_provider import MockProductProvider
            results = MockProductProvider().search_products(query=keyword, category=category, page=page, limit=limit)
            app_cache.set(cache_key, results, ttl=600)
            return results

        path = f"/v2/providers/affiliate_open_api/apis/openapi/products/search?keyword={keyword}&limit={limit}"
        auth_header = self._generate_hmac("GET", path)

        try:
            res = requests.get(
                self.BASE_URL + path,
                headers={"Authorization": auth_header, "Content-Type": "application/json"},
                timeout=10
            )
            res.raise_for_status()
            data = res.json()
            items = data.get("data", {}).get("productData", [])
            results = []
            for it in items:
                results.append(ProductDTO(
                    external_id=str(it.get("productId")),
                    name=it.get("productName", ""),
                    url=it.get("productUrl", ""),
                    image_url=it.get("productImage", ""),
                    category=it.get("categoryName", "일반"),
                    price=int(it.get("productPrice", 0)),
                    original_price=it.get("originalPrice"),
                    rating=float(it.get("rating", 4.5)),
                    review_count=int(it.get("reviewCount", 0)),
                    shipping_type="로켓배송" if it.get("isRocket") else "일반배송",
                    description=it.get("productName", ""),
                    source="coupang_api"
                ))
            app_cache.set(cache_key, results, ttl=600)
            return results
        except Exception as e:
            print(f"[CoupangAPI] Error fetching live products: {e}. Falling back to mock data.")
            from integrations.providers.mock_product_provider import MockProductProvider
            results = MockProductProvider().search_products(query=keyword, category=category, page=page, limit=limit)
            app_cache.set(cache_key, results, ttl=600)
            return results

    def get_product_detail(self, external_id: str) -> Optional[ProductDTO]:
        cache_key = f"coupang_detail:{external_id}"
        cached = app_cache.get(cache_key)
        if cached is not None:
            return cached

        from integrations.providers.mock_product_provider import MockProductProvider
        res = MockProductProvider().get_product_detail(external_id)
        if res:
            app_cache.set(cache_key, res, ttl=1800)
        return res

    def generate_deeplink(self, coupang_urls: List[str]) -> List[Dict[str, str]]:
        if not self.access_key or not self.secret_key:
            return [{"original": u, "shorten": f"https://link.coupang.com/a/mock_{abs(hash(u))%100000}"} for u in coupang_urls]

        path = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
        auth_header = self._generate_hmac("POST", path)
        try:
            res = requests.post(
                self.BASE_URL + path,
                headers={"Authorization": auth_header, "Content-Type": "application/json"},
                json={"coupangUrls": coupang_urls},
                timeout=10
            )
            res.raise_for_status()
            data = res.json()
            return data.get("data", [])
        except Exception as e:
            print(f"[CoupangAPI] Deeplink error: {e}")
            return [{"original": u, "shorten": f"https://link.coupang.com/a/mock_{abs(hash(u))%100000}"} for u in coupang_urls]