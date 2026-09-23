from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from config import settings
from database.repository import Repository
from database.models import Product, Content, Comment
from domain_types.schemas import CommentItem, ContentCreateRequest
from integrations.factory import get_ai_provider
from integrations.providers.mock_ai_provider import MockAIProvider
from utils.logger import start_job_log, finish_job_log

class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.ai_provider = get_ai_provider()

    def generate_comments(
        self,
        product_id: int,
        partner_link: Optional[str] = None,
        custom_disclosure: Optional[str] = None,
        strategy: str = "TIMED_COMMENT",
        affiliate_platform: str = "COUPANG"
    ) -> List[CommentItem]:
        product = self.repo.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")

        disclosure = custom_disclosure or settings.PARTNERS_DISCLOSURE

        job = start_job_log(self.db, "COMMENT_GENERATION", {
            "product_id": product_id,
            "has_link": bool(partner_link),
            "strategy": strategy,
            "affiliate_platform": affiliate_platform
        })

        try:
            prod_data = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "shipping_type": product.shipping_type
            }

            if isinstance(self.ai_provider, MockAIProvider):
                comments = self.ai_provider.write_comments(
                    product_data=prod_data,
                    partners_notice=disclosure,
                    partner_link=partner_link,
                    strategy=strategy,
                    affiliate_platform=affiliate_platform
                )
            else:
                comments = MockAIProvider().write_comments(
                    product_data=prod_data,
                    partners_notice=disclosure,
                    partner_link=partner_link,
                    strategy=strategy,
                    affiliate_platform=affiliate_platform
                )

            finish_job_log(self.db, job, "SUCCESS", {
                "count": len(comments)
            })
            return comments

        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def save_content_with_comments(
        self,
        product_id: int,
        title: str,
        body: str,
        project_id: Optional[int] = None,
        idea_id: Optional[int] = None,
        account_id: Optional[int] = None,
        status: str = "DRAFT",
        comments: Optional[List[dict]] = None,
        post_type: str = "MONEY_POST",
        hook_style: str = "LOSS_AVERSION",
        comment_strategy: str = "TIMED_COMMENT",
        affiliate_platform: str = "COUPANG"
    ) -> Content:
        valid_statuses = ["DRAFT", "REVIEW", "APPROVED", "SCHEDULED", "PUBLISHED", "REJECTED"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid content status: {status}")

        content = self.repo.create_content(
            product_id=product_id,
            title=title,
            body=body,
            project_id=project_id,
            idea_id=idea_id,
            account_id=account_id,
            status=status,
            comments=comments,
            post_type=post_type,
            hook_style=hook_style,
            comment_strategy=comment_strategy,
            affiliate_platform=affiliate_platform
        )

        if idea_id:
            self.repo.update_idea_status(idea_id, "완료")

        return content

    def update_comment_text(self, comment_id: int, body: str, link: Optional[str] = None) -> Optional[Comment]:
        return self.repo.update_comment(comment_id, body=body, link=link)

    def update_content_status(self, content_id: int, status: str) -> Optional[Content]:
        valid_statuses = ["DRAFT", "REVIEW", "APPROVED", "SCHEDULED", "PUBLISHED", "REJECTED"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid content status: {status}")
        return self.repo.update_content_status(content_id, status)