import hmac
import hashlib
import time
import requests
from typing import Optional, List, Dict, Any
from .base import AffiliateProvider
from .schemas import ProductItem, AffiliateReport
from .exceptions import AffiliateException, AffiliateAuthError, AffiliateRateLimitError, DeeplinkError

class CoupangProvider(AffiliateProvider):
    """
    Official Coupang Partners Open API Provider.
    Implements HMAC-SHA256 authentication according to Coupang Partners Developer Specification.
    """
    BASE_URL = "https://api-gateway.coupang.com"

    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.access_key = access_key
        self.secret_key = secret_key

    def _generate_hmac(self, method: str, url: str) -> str:
        if not self.access_key or not self.secret_key:
            raise AffiliateAuthError("COUPANG_ACCESS_KEY or COUPANG_SECRET_KEY is missing")

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

    def search_products(self, keyword: str, limit: int = 20) -> List[ProductItem]:
        if not self.access_key or not self.secret_key:
            raise AffiliateAuthError("Coupang API keys are not configured")

        path = f"/v2/providers/affiliate_open_api/apis/openapi/products/search?keyword={requests.utils.quote(keyword)}&limit={limit}"
        auth_header = self._generate_hmac("GET", path)

        try:
            res = requests.get(
                self.BASE_URL + path,
                headers={"Authorization": auth_header, "Content-Type": "application/json"},
                timeout=12
            )
            if res.status_code in [401, 403]:
                raise AffiliateAuthError(res.text)
            if res.status_code == 429:
                raise AffiliateRateLimitError(res.text)
            res.raise_for_status()

            data = res.json()
            items = data.get("data", {}).get("productData", [])
            results = []
            for it in items:
                results.append(ProductItem(
                    product_id=str(it.get("productId")),
                    name=it.get("productName", ""),
                    category=it.get("categoryName", "일반"),
                    original_url=it.get("productUrl", ""),
                    affiliate_url=it.get("productUrl", ""),  # will be deeplinked
                    price=int(it.get("productPrice", 0)),
                    original_price=it.get("originalPrice"),
                    image_url=it.get("productImage", ""),
                    rating=float(it.get("rating", 4.5)),
                    review_count=int(it.get("reviewCount", 0)),
                    shipping_type="로켓배송" if it.get("isRocket") else "일반배송",
                    description=it.get("productName", ""),
                    source="coupang"
                ))
            return results
        except (AffiliateException, requests.exceptions.RequestException) as e:
            if isinstance(e, AffiliateException):
                raise
            raise AffiliateException(f"Coupang search failed: {e}")

    def get_product_detail(self, product_id: str) -> Optional[ProductItem]:
        # Search by product ID or keyword fallback
        products = self.search_products(keyword=str(product_id), limit=1)
        return products[0] if products else None

    def create_deeplink(self, url: str) -> str:
        if not self.access_key or not self.secret_key:
            raise AffiliateAuthError("Coupang API keys are not configured")

        path = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
        auth_header = self._generate_hmac("POST", path)

        try:
            res = requests.post(
                self.BASE_URL + path,
                headers={"Authorization": auth_header, "Content-Type": "application/json"},
                json={"coupangUrls": [url]},
                timeout=10
            )
            if res.status_code in [401, 403]:
                raise AffiliateAuthError(res.text)
            res.raise_for_status()

            data = res.json().get("data", [])
            if data and "shortenUrl" in data[0]:
                return data[0]["shortenUrl"]
            raise DeeplinkError("No shortenUrl in Coupang response")
        except Exception as e:
            if isinstance(e, AffiliateException):
                raise
            raise DeeplinkError(f"Coupang deeplink failed: {e}")

    def get_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AffiliateReport:
        if not self.access_key or not self.secret_key:
            raise AffiliateAuthError("Coupang API keys are not configured")
        # Returns current daily report or basic structure
        return AffiliateReport(clicks=0, orders=0, commission=0)
