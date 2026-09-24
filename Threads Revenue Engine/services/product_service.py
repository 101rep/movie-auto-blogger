from typing import Optional, List, Dict, Any
from integrations.affiliate.base import AffiliateProvider
from integrations.affiliate.mock_provider import MockAffiliateProvider
from integrations.affiliate.coupang_provider import CoupangProvider
from integrations.affiliate.schemas import ProductItem, AffiliateReport
from integrations.affiliate.exceptions import AffiliateException, DeeplinkError

class ProductService:
    """
    Product Service Layer for Affiliate Operations.
    Mediates all product searching, scoring, and deeplinking through AffiliateProvider.
    Never calls external APIs directly.
    """
    def __init__(self, provider: Optional[AffiliateProvider] = None, access_key: Optional[str] = None, secret_key: Optional[str] = None, mode: str = "mock"):
        if provider:
            self.provider = provider
        elif mode == "real" and access_key and secret_key:
            self.provider = CoupangProvider(access_key=access_key, secret_key=secret_key)
        else:
            self.provider = MockAffiliateProvider()

    def search_products(self, keyword: str, limit: int = 20) -> List[ProductItem]:
        return self.provider.search_products(keyword=keyword, limit=limit)

    def calculate_product_score(
        self,
        product: ProductItem,
        account_category: Optional[str] = None,
        persona: Optional[Any] = None,
        recent_product_ids: Optional[List[str]] = None
    ) -> float:
        """
        Product Scoring Engine (0 to 100 score).
        Evaluates price suitability, reviews, ratings, delivery type, category/DNA fit, and cooldown.
        """
        score = 0.0

        # 1. Cooldown Penalty (Default 14 days check)
        if recent_product_ids and (str(product.product_id) in recent_product_ids or product.original_url in recent_product_ids):
            return 0.0  # Immediate zero score if within cooldown period

        # 2. Price Fit (15,000 ~ 50,000 KRW is ideal impulsive buying zone on Threads)
        price = product.price
        if 15000 <= price <= 50000:
            score += 25.0
        elif 10000 <= price < 15000 or 50000 < price <= 80000:
            score += 15.0
        elif price < 10000:
            score += 8.0
        else:
            score += 5.0

        # 3. Rating (High social proof)
        if product.rating >= 4.8:
            score += 20.0
        elif product.rating >= 4.5:
            score += 15.0
        elif product.rating >= 4.0:
            score += 10.0
        else:
            score += 2.0

        # 4. Review Trust (Confidence factor)
        if product.review_count >= 500:
            score += 20.0
        elif product.review_count >= 100:
            score += 15.0
        elif product.review_count >= 30:
            score += 10.0
        else:
            score += 4.0

        # 5. Shipping Type (Rocket delivery preference in Korea)
        if product.shipping_type == "로켓배송":
            score += 15.0
        else:
            score += 5.0

        # 6. Category Fit
        if account_category and (account_category.lower() in product.category.lower() or account_category.lower() in product.name.lower()):
            score += 10.0
        else:
            score += 5.0

        # 7. Persona DNA Alignment
        if persona:
            # Check blocked products
            blocked = getattr(persona, "blocked_products", []) or getattr(persona, "prohibited_styles", []) or []
            if any(b.lower() in product.name.lower() for b in blocked if isinstance(b, str)):
                return 0.0

            # Check preferred products
            preferred = getattr(persona, "preferred_products", []) or getattr(persona, "hook_preferences", []) or []
            if any(p.lower() in product.name.lower() for p in preferred if isinstance(p, str)):
                score += 10.0

        return min(100.0, round(score, 1))

    def select_best_product(
        self,
        keyword: str,
        account_category: Optional[str] = None,
        persona: Optional[Any] = None,
        recent_product_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> Optional[ProductItem]:
        """
        Executes search, scores all items, and returns the highest-scoring candidate.
        """
        products = self.search_products(keyword=keyword, limit=limit)
        if not products:
            return None

        scored_products = []
        for p in products:
            p.score = self.calculate_product_score(
                p,
                account_category=account_category,
                persona=persona,
                recent_product_ids=recent_product_ids
            )
            if p.score > 0:
                scored_products.append(p)

        if not scored_products:
            # Fallback to first product if all were filtered by minor rules
            p = products[0]
            p.score = 50.0
            return p

        scored_products.sort(key=lambda x: x.score, reverse=True)
        return scored_products[0]

    def create_deeplink(self, url: str) -> str:
        return self.provider.create_deeplink(url)

    def validate_affiliate_compliance(self, text: str, replies: List[str], required_disclosure: str) -> Dict[str, Any]:
        """
        Enforces STEP 11:
        Validates that disclosure and link exist in thread/replies before publishing.
        """
        full_content = text + " " + " ".join(replies)
        has_disclosure = required_disclosure in full_content or "쿠팡 파트너스" in full_content or "수수료" in full_content
        has_link = "http://" in full_content or "https://" in full_content or "coupang.com" in full_content

        errors = []
        if not has_disclosure:
            errors.append("DISCLOSURE_MISSING")
        if not has_link:
            errors.append("AFFILIATE_LINK_MISSING")

        return {
            "compliant": len(errors) == 0,
            "errors": errors
        }
