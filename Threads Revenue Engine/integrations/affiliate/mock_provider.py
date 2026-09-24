from typing import Optional, List, Dict, Any
from .base import AffiliateProvider
from .schemas import ProductItem, AffiliateReport

class MockAffiliateProvider(AffiliateProvider):
    """
    Mock Affiliate Provider for offline development and testing.
    """
    SAMPLE_PRODUCTS = [
        {
            "product_id": "1",
            "name": "멀티 데스크 오거나이저 3단 서랍형",
            "category": "IT",
            "original_url": "https://www.coupang.com/vp/products/10001",
            "affiliate_url": "https://link.coupang.com/a/mock_desk1",
            "price": 28900,
            "original_price": 35000,
            "rating": 4.8,
            "review_count": 420,
            "shipping_type": "로켓배송",
            "description": "깔끔한 데스크 정리를 위한 모던 3단 서랍함"
        },
        {
            "product_id": "2",
            "name": "초경량 알루미늄 캠핑 폴딩 체어",
            "category": "여행",
            "original_url": "https://www.coupang.com/vp/products/10002",
            "affiliate_url": "https://link.coupang.com/a/mock_chair2",
            "price": 34500,
            "original_price": 42000,
            "rating": 4.7,
            "review_count": 890,
            "shipping_type": "로켓배송",
            "description": "접이식 휴대용 가벼운 릴렉스 체어"
        },
        {
            "product_id": "3",
            "name": "진정 시카 히알루론산 수분 크림 100ml",
            "category": "뷰티",
            "original_url": "https://www.coupang.com/vp/products/10003",
            "affiliate_url": "https://link.coupang.com/a/mock_cream3",
            "price": 19800,
            "original_price": 25000,
            "rating": 4.9,
            "review_count": 1250,
            "shipping_type": "로켓배송",
            "description": "자극 없이 촉촉한 데일리 수분 진정 크림"
        }
    ]

    def search_products(self, keyword: str, limit: int = 20) -> List[ProductItem]:
        results = []
        kw = (keyword or "").lower()
        for p in self.SAMPLE_PRODUCTS:
            if not kw or kw in p["name"].lower() or kw in p["category"].lower() or kw in p.get("description", "").lower():
                results.append(ProductItem(**p))
        if not results:
            # Generate deterministic mock item for keyword
            h = abs(hash(keyword)) % 90000 + 10000
            results.append(ProductItem(
                product_id=str(h),
                name=f"{keyword} 추천 베스트 상품",
                category="추천",
                original_url=f"https://www.coupang.com/vp/products/{h}",
                affiliate_url=f"https://link.coupang.com/a/mock_{h}",
                price=24900,
                rating=4.8,
                review_count=350,
                shipping_type="로켓배송",
                description=f"{keyword} 실사용 만족도 높은 가성비 제품"
            ))
        return results[:limit]

    def get_product_detail(self, product_id: str) -> Optional[ProductItem]:
        for p in self.SAMPLE_PRODUCTS:
            if p["product_id"] == str(product_id):
                return ProductItem(**p)
        return ProductItem(
            product_id=str(product_id),
            name=f"상품 {product_id}",
            category="일반",
            original_url=f"https://www.coupang.com/vp/products/{product_id}",
            affiliate_url=f"https://link.coupang.com/a/mock_{product_id}",
            price=25000,
            rating=4.5,
            review_count=100
        )

    def create_deeplink(self, url: str) -> str:
        h = abs(hash(url)) % 100000
        return f"https://link.coupang.com/a/mock_{h}"

    def get_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AffiliateReport:
        return AffiliateReport(clicks=140, orders=6, commission=18500)
