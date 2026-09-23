from typing import Optional
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Product, ProductScore
from domain_types.schemas import ProductScoreResult, ProductScoreWeights
from integrations.factory import get_ai_provider
from integrations.providers.mock_ai_provider import MockAIProvider
from utils.logger import start_job_log, finish_job_log

class ProductScoringService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.ai_provider = get_ai_provider()

    def score_product(self, product_id: int, custom_weights: Optional[ProductScoreWeights] = None) -> ProductScore:
        product = self.repo.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        job = start_job_log(self.db, "PRODUCT_SCORING", {"product_id": product_id})

        try:
            prod_data = {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "rating": product.rating,
                "review_count": product.review_count,
                "shipping_type": product.shipping_type,
                "description": product.description
            }

            # If mock provider, use weighted evaluation directly
            if isinstance(self.ai_provider, MockAIProvider):
                score_result = self.ai_provider.score_product_with_weights(prod_data, weights=custom_weights)
            else:
                prompt = f"""다음 쿠팡 상품을 평가 기준에 따라 점수화하고 이유를 작성하세요:
상품명: {product.name}
카테고리: {product.category}
가격: {product.price:,}원
평점: {product.rating}
리뷰수: {product.review_count:,}개
배송: {product.shipping_type}
설명: {product.description}"""
                score_result = self.ai_provider.generate_structured(prompt, ProductScoreResult)

            saved_score = self.repo.save_product_score(product_id, score_result)
            finish_job_log(self.db, job, "SUCCESS", {
                "score_id": saved_score.id,
                "total_score": saved_score.total_score,
                "reason": saved_score.reason
            })
            return saved_score

        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def get_latest_score(self, product_id: int) -> Optional[ProductScore]:
        return self.repo.get_latest_product_score(product_id)