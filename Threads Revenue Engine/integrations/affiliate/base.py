from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from .schemas import ProductItem, DeeplinkResult, AffiliateReport

class AffiliateProvider(ABC):
    """Abstract base provider for affiliate networks (Coupang Partners, etc.)."""

    @abstractmethod
    def search_products(self, keyword: str, limit: int = 20) -> List[ProductItem]:
        """Search products by keyword or category."""
        pass

    @abstractmethod
    def get_product_detail(self, product_id: str) -> Optional[ProductItem]:
        """Fetch individual product specifications."""
        pass

    @abstractmethod
    def create_deeplink(self, url: str) -> str:
        """Convert a standard product URL into a tracking affiliate deeplink."""
        pass

    @abstractmethod
    def get_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AffiliateReport:
        """Fetch affiliate commission and conversion stats."""
        pass

    # Compatibility methods
    def get_reports(self) -> dict:
        r = self.get_report()
        return r.model_dump()

    def validate_product(self, product) -> bool:
        if isinstance(product, dict):
            return bool(product.get("affiliate_url") or product.get("url"))
        return bool(getattr(product, "affiliate_url", None) or getattr(product, "url", None))
