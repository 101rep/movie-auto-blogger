from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Product
from domain_types.schemas import ProductDTO, ProductFilterParams
from integrations.factory import get_product_provider
from utils.logger import start_job_log, finish_job_log

class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.provider = get_product_provider()

    def search_external_products(self, query: Optional[str] = None, category: Optional[str] = None, page: int = 1, limit: int = 20) -> List[ProductDTO]:
        return self.provider.search_products(query=query, category=category, page=page, limit=limit)

    def get_external_product_detail(self, external_id: str) -> Optional[ProductDTO]:
        return self.provider.get_product_detail(external_id)

    def find_duplicate(self, external_id: str, url: Optional[str] = None) -> Optional[Product]:
        return self.repo.find_duplicate_product(external_id=external_id, url=url)

    def save_product(self, product_data: dict) -> Product:
        # Prevent duplication: check by external_id or url
        existing = self.find_duplicate(
            external_id=product_data["external_id"],
            url=product_data.get("url")
        )
        if existing:
            # Update existing product with latest prices/reviews
            updates = {
                "price": product_data.get("price", existing.price),
                "original_price": product_data.get("original_price", existing.original_price),
                "rating": product_data.get("rating", existing.rating),
                "review_count": product_data.get("review_count", existing.review_count),
                "shipping_type": product_data.get("shipping_type", existing.shipping_type),
            }
            return self.repo.update_product(existing.id, updates)

        job = start_job_log(self.db, "PRODUCT_SAVE", {"external_id": product_data["external_id"]})
        try:
            prod = self.repo.create_product(product_data)
            finish_job_log(self.db, job, "SUCCESS", {"product_id": prod.id})
            return prod
        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.repo.get_product(product_id)

    def list_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "recent",
        skip: int = 0,
        limit: int = 50
    ) -> List[Product]:
        return self.repo.list_products(
            query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            sort_by=sort_by,
            skip=skip,
            limit=limit
        )

    def update_product(self, product_id: int, updates: dict) -> Optional[Product]:
        return self.repo.update_product(product_id, updates)

    def delete_product(self, product_id: int) -> bool:
        return self.repo.delete_product(product_id)