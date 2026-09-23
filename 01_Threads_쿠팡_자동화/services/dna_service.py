from typing import Optional
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Product, ProductDNA
from domain_types.schemas import ProductDNAResult
from integrations.factory import get_ai_provider
from integrations.providers.mock_ai_provider import MockAIProvider
from utils.logger import start_job_log, finish_job_log
from prompts.manager import PromptManager

class ProductDNAService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.ai_provider = get_ai_provider()

    def generate_dna(self, product_id: int, force_refresh: bool = False, prompt_version: str = "v1") -> ProductDNA:
        product = self.repo.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        existing = self.repo.get_product_dna(product_id)
        if existing and not force_refresh:
            return existing

        job = start_job_log(self.db, "PRODUCT_DNA_ANALYSIS", {
            "product_id": product_id,
            "force_refresh": force_refresh,
            "prompt_version": prompt_version
        })

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

            if isinstance(self.ai_provider, MockAIProvider):
                dna_result = self.ai_provider.extract_dna(prod_data)
            else:
                system_prompt = PromptManager.get_prompt("product_dna", prompt_version, self.db)
                prompt = f"""다음 쿠팡 상품을 분석하여 바이럴 마케팅용 상품 DNA를 작성하세요:
상품명: {product.name}
카테고리: {product.category}
가격: {product.price:,}원
평점: {product.rating} (리뷰 {product.review_count:,}건)
배송: {product.shipping_type}
설명: {product.description}"""
                dna_result = self.ai_provider.generate_structured(prompt, ProductDNAResult, system_prompt=system_prompt)

            saved_dna = self.repo.save_product_dna(product_id, dna_result)
            finish_job_log(self.db, job, "SUCCESS", {
                "dna_id": saved_dna.id,
                "target_person": saved_dna.target_person,
                "ai_summary": saved_dna.ai_summary
            })
            return saved_dna

        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def get_dna(self, product_id: int) -> Optional[ProductDNA]:
        return self.repo.get_product_dna(product_id)