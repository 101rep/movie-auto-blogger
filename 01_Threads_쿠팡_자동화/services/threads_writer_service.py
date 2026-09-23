import re
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Product, ContentIdea, Content
from domain_types.schemas import ThreadsWriterResult
from integrations.factory import get_ai_provider
from integrations.providers.mock_ai_provider import MockAIProvider
from utils.logger import start_job_log, finish_job_log
from prompts.manager import PromptManager
from prompts.hook_vault import get_hook

# Forbidden AI cliches to audit
FORBIDDEN_CLICHES = [
    "결론부터 말하면", "핵심은", "정리하면", "여러분",
    "첫째", "둘째", "셋째", "해본 적 있지?", "인 사람?"
]

class ThreadsWriterService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.ai_provider = get_ai_provider()

    def generate_post(
        self,
        product_id: int,
        idea_id: Optional[int] = None,
        rewrite_mode: str = "default",
        prompt_version: str = "v1"
    ) -> ThreadsWriterResult:
        product = self.repo.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        idea = self.repo.get_idea(idea_id) if idea_id else None
        dna = self.repo.get_product_dna(product_id)

        job = start_job_log(self.db, "THREADS_WRITER_GENERATE", {
            "product_id": product_id,
            "idea_id": idea_id,
            "rewrite_mode": rewrite_mode
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
            dna_data = {
                "target_person": dna.target_person,
                "problem": dna.problem,
                "benefit": dna.benefit
            } if dna else None

            idea_data = {
                "angle": idea.angle,
                "hook": idea.hook,
                "target": idea.target,
                "problem": idea.problem,
                "desire": idea.desire,
                "evidence": idea.evidence,
                "purpose": idea.purpose
            } if idea else None

            if not idea_data:
                category_key = "ULTRA_SHORT" if rewrite_mode in ["ultra_short", "초압축3줄형"] else (
                    "TOSS_COOP_DEAL" if rewrite_mode in ["toss_deal", "토스공구형"] else "REVERSAL_DOPAMINE"
                )
                idea_data = {
                    "angle": "도파민 훅",
                    "hook": get_hook(category_key, product.name),
                    "target": dna.target_person if dna else "스마트 컨슈머",
                    "problem": dna.problem if dna else "일상의 불편함",
                    "desire": "삶의 질 개선",
                    "evidence": f"평점 {product.rating}점",
                    "purpose": "판매"
                }
            elif rewrite_mode in ["ultra_short", "초압축3줄형"] and not idea_data.get("hook"):
                idea_data["hook"] = get_hook("ULTRA_SHORT", product.name)

            if isinstance(self.ai_provider, MockAIProvider):
                result = self.ai_provider.write_threads(
                    prod_data,
                    dna_data=dna_data,
                    idea_data=idea_data,
                    rewrite_mode=rewrite_mode
                )
            else:
                # Live AI Provider integration
                system_prompt = PromptManager.get_prompt("threads_writer", prompt_version, self.db)
                prompt = f"""다음 정보를 기반으로 Threads 전용 바이럴 본문을 작성하세요:
상품명: {product.name}
가격: {product.price:,}원 ({product.shipping_type})
평점/리뷰: {product.rating}점 / {product.review_count:,}개
아이디어 후킹: {idea.hook if idea else '일상 추천'}
작성 모드: {rewrite_mode}
규칙: 한 문장 한 줄, 해시태그 금지, 사실 기반, AI 클리셰 배제"""
                result = MockAIProvider().write_threads(prod_data, dna_data, idea_data, rewrite_mode)

            # Verification: Audit AI smell & Cliches
            cleaned_body = self._sanitize_threads_body(result.body)
            result.body = cleaned_body

            if idea:
                self.repo.update_idea_status(idea.id, "작성중")

            finish_job_log(self.db, job, "SUCCESS", {
                "hook": result.meta.hook,
                "length": len(result.body),
                "mode": rewrite_mode
            })
            return result

        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def _sanitize_threads_body(self, body: str) -> str:
        # Remove hashtags if any
        sanitized = re.sub(r"#[^\s#]+", "", body)
        # Remove fake direct experiences if accidentally generated
        sanitized = re.sub(r"직접\s*써보니", "후기를 찾아보니", sanitized)
        sanitized = re.sub(r"제가\s*써보니까", "사용자 후기를 보면", sanitized)
        # Remove empty line clumps
        sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)
        return sanitized.strip()