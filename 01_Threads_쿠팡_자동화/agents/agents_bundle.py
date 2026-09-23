from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from agents.base_agent import BaseAgent
from services.product_service import ProductService
from services.scoring_service import ProductScoringService
from services.dna_service import ProductDNAService
from services.idea_service import ContentIdeaService
from services.threads_writer_service import ThreadsWriterService
from services.comment_service import CommentService
from services.review_service import ReviewService
from services.scheduler_service import SchedulerService
from services.analytics_service import AnalyticsService
from services.learning_service import LearningService
from services.account_service import AccountService
from domain_types.schemas import ProductScoreWeights

class ProductAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = ProductService(db)

    def search_and_collect(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20):
        return self.service.search_external_products(query=query, category=category, limit=limit)

    def save_product_to_system(self, product_data: dict):
        return self.service.save_product(product_data)

    def inspect_product(self, product_id: int):
        return self.service.get_product(product_id)

class ProductScoringAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = ProductScoringService(db)

    def evaluate_product(self, product_id: int, custom_weights: Optional[ProductScoreWeights] = None):
        return self.service.score_product(product_id, custom_weights=custom_weights)

class ProductDNAAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = ProductDNAService(db)

    def extract_dna(self, product_id: int, force_refresh: bool = False, prompt_version: str = "v1"):
        return self.service.generate_dna(product_id, force_refresh=force_refresh, prompt_version=prompt_version)

class ContentIdeaAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = ContentIdeaService(db)

    def brainstorm_ideas(self, product_id: int, project_id: Optional[int] = None):
        return self.service.generate_ideas_for_product(product_id, project_id=project_id)

    def select_idea(self, idea_id: int):
        return self.service.update_status(idea_id, "선택")

class ThreadsWriterAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = ThreadsWriterService(db)

    def compose_post(self, product_id: int, idea_id: Optional[int] = None, rewrite_mode: str = "default"):
        return self.service.generate_post(product_id, idea_id=idea_id, rewrite_mode=rewrite_mode)

class CommentAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = CommentService(db)

    def generate_replies(self, product_id: int, partner_link: Optional[str] = None, custom_disclosure: Optional[str] = None):
        return self.service.generate_comments(product_id, partner_link=partner_link, custom_disclosure=custom_disclosure)

    def finalize_content(self, product_id: int, title: str, body: str, comments: List[dict], idea_id: Optional[int] = None, status: str = "DRAFT"):
        return self.service.save_content_with_comments(
            product_id=product_id,
            title=title,
            body=body,
            idea_id=idea_id,
            status=status,
            comments=comments
        )

# ==================== Phase 4 & 5 Extended Agents ====================
class ReviewAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = ReviewService(db)

    def audit_content(self, content_id: int):
        return self.service.audit_content(content_id)

class SchedulerAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = SchedulerService(db)

    def schedule(self, content_id: int, scheduled_at: datetime):
        return self.service.schedule_content(content_id, scheduled_at)

    def publish_now(self, content_id: int):
        return self.service.publish_now(content_id)

class AnalyticsAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = AnalyticsService(db)

    def collect_metrics(self, content_id: int):
        return self.service.sync_metrics_from_provider(content_id)

    def get_dashboard_data(self):
        return self.service.get_summary_report()

class LearningAgent(BaseAgent):
    def __init__(self, db: Session):
        super().__init__(db)
        self.service = LearningService(db)

    def derive_insights(self, project_id: Optional[int] = None):
        return self.service.analyze_and_learn(project_id)

class MasterAgent(BaseAgent):
    """
    Master Orchestrator Agent (Phase 1 ~ 5):
    Coordinates complete autonomous cycle:
    Collection -> Scoring -> DNA -> Ideas -> Writing -> Comments -> Review -> Scheduling/Publishing -> Analytics -> Learning
    """
    def __init__(self, db: Session):
        super().__init__(db)
        self.product_agent = ProductAgent(db)
        self.scoring_agent = ProductScoringAgent(db)
        self.dna_agent = ProductDNAAgent(db)
        self.idea_agent = ContentIdeaAgent(db)
        self.writer_agent = ThreadsWriterAgent(db)
        self.comment_agent = CommentAgent(db)
        self.review_agent = ReviewAgent(db)
        self.scheduler_agent = SchedulerAgent(db)
        self.analytics_agent = AnalyticsAgent(db)
        self.learning_agent = LearningAgent(db)

    def execute_full_pipeline(
        self,
        product_data: dict,
        selected_angle_index: int = 0,
        partner_link: Optional[str] = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        # 1. Product
        product = self.product_agent.save_product_to_system(product_data)

        # 2. Scoring
        score = self.scoring_agent.evaluate_product(product.id)

        # 3. DNA
        dna = self.dna_agent.extract_dna(product.id)

        # 4. Ideas
        ideas = self.idea_agent.brainstorm_ideas(product.id)
        selected_idea = ideas[selected_angle_index] if ideas and selected_angle_index < len(ideas) else None
        if selected_idea:
            self.idea_agent.select_idea(selected_idea.id)

        # 5. Threads Post
        threads_post = self.writer_agent.compose_post(
            product_id=product.id,
            idea_id=selected_idea.id if selected_idea else None
        )

        # 6. Comments
        comments = self.comment_agent.generate_replies(
            product_id=product.id,
            partner_link=partner_link
        )

        # 7. Draft Content
        content = self.comment_agent.finalize_content(
            product_id=product.id,
            title=selected_idea.title if selected_idea else f"{product.name} 추천",
            body=threads_post.body,
            comments=[c.model_dump() for c in comments],
            idea_id=selected_idea.id if selected_idea else None,
            status="DRAFT"
        )

        # 8. Review AI (Audit Quality, Policy, Duplicates)
        review_result = self.review_agent.audit_content(content.id)

        # 9. Schedule or Immediate Publish if requested
        if schedule_time:
            self.scheduler_agent.schedule(content.id, schedule_time)

        # 10. Analytics & Learning Loop
        insights = self.learning_agent.derive_insights()

        return {
            "product": product,
            "score": score,
            "dna": dna,
            "ideas": ideas,
            "selected_idea": selected_idea,
            "threads_post": threads_post,
            "comments": comments,
            "content": content,
            "review": review_result,
            "learning_insights": insights
        }