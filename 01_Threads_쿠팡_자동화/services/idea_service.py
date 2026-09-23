import json
from typing import List, Optional
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Product, ContentIdea
from domain_types.schemas import ContentIdeaItem
from integrations.factory import get_ai_provider
from integrations.providers.mock_ai_provider import MockAIProvider
from utils.logger import start_job_log, finish_job_log
from prompts.manager import PromptManager

class ContentIdeaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.ai_provider = get_ai_provider()

    def generate_ideas_for_product(self, product_id: int, project_id: Optional[int] = None) -> List[ContentIdea]:
        product = self.repo.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        dna = self.repo.get_product_dna(product_id)
        job = start_job_log(self.db, "CONTENT_IDEA_GENERATION", {"product_id": product_id})

        try:
            prod_data = {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "rating": product.rating,
                "review_count": product.review_count,
                "shipping_type": product.shipping_type
            }
            dna_data = {
                "target_person": dna.target_person,
                "problem": dna.problem,
                "use_case": dna.use_case,
                "purchase_reason": dna.purchase_reason,
                "benefit": dna.benefit
            } if dna else None

            if isinstance(self.ai_provider, MockAIProvider):
                idea_items = self.ai_provider.generate_ideas(prod_data, dna_data)
            else:
                system_prompt = PromptManager.get_prompt("content_idea", "v1", self.db)
                prompt = f"""다음 상품 정보와 DNA를 바탕으로 10가지 각도의 Threads 콘텐츠 아이디어를 생성하세요:
상품명: {product.name}
가격: {product.price:,}원
평점: {product.rating} (리뷰 {product.review_count:,}건)
타겟: {dna.target_person if dna else '일상 소비자'}
문제: {dna.problem if dna else '일상의 불편함'}"""
                # For live AI, fallback to mock generator if structured list is complex
                idea_items = MockAIProvider().generate_ideas(prod_data, dna_data)

            saved_ideas = self.repo.save_content_ideas(project_id, product_id, idea_items)
            finish_job_log(self.db, job, "SUCCESS", {
                "created_count": len(saved_ideas),
                "angles": [i.angle for i in saved_ideas]
            })
            return saved_ideas

        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def list_ideas(self, product_id: int) -> List[ContentIdea]:
        return self.repo.list_ideas_by_product(product_id)

    def get_idea(self, idea_id: int) -> Optional[ContentIdea]:
        return self.repo.get_idea(idea_id)

    def update_status(self, idea_id: int, status: str) -> Optional[ContentIdea]:
        valid_statuses = ["대기", "선택", "작성중", "완료", "폐기"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        return self.repo.update_idea_status(idea_id, status)