import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database.repository import Repository
from services.idea_service import ContentIdeaService
from services.threads_writer_service import ThreadsWriterService
from services.comment_service import CommentService
from services.review_service import ReviewService
from services.scheduler_service import SchedulerService
from datetime import datetime, timedelta

class ABTestService:
    """
    A/B Testing Engine for Threads Content.
    Generates two distinct variants (Hook Angle / Writing Style) for the same product,
    schedules both at spaced intervals, and compares performance metrics to determine the winning copy.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.idea_svc = ContentIdeaService(db)
        self.writer_svc = ThreadsWriterService(db)
        self.comment_svc = CommentService(db)
        self.review_svc = ReviewService(db)
        self.sched_svc = SchedulerService(db)

    def create_ab_test_variants(
        self,
        product_id: int,
        variant_a_mode: str = "직장인 공감형",
        variant_b_mode: str = "짧은 호흡형",
        hours_apart: int = 6
    ) -> Dict[str, Any]:
        group_id = f"ab_{uuid.uuid4().hex[:8]}"
        ideas = self.idea_svc.generate_ideas_for_product(product_id)
        if len(ideas) < 2:
            raise ValueError("A/B 테스트를 위해 최소 2개 이상의 아이디어가 필요합니다.")

        idea_a = ideas[0]
        idea_b = ideas[1]

        # 1. Variant A
        writer_a = self.writer_svc.generate_post(product_id=product_id, idea_id=idea_a.id, rewrite_mode=variant_a_mode)
        comments_a = self.comment_svc.generate_comments(product_id)
        content_a = self.comment_svc.save_content_with_comments(
            product_id=product_id,
            idea_id=idea_a.id,
            title=f"[A/B - A안:{idea_a.angle}] {idea_a.hook[:25]}",
            body=writer_a.body,
            comments=[c.model_dump() for c in comments_a],
            status="APPROVED"
        )
        self.review_svc.audit_content(content_a.id)

        # 2. Variant B
        writer_b = self.writer_svc.generate_post(product_id=product_id, idea_id=idea_b.id, rewrite_mode=variant_b_mode)
        comments_b = self.comment_svc.generate_comments(product_id)
        content_b = self.comment_svc.save_content_with_comments(
            product_id=product_id,
            idea_id=idea_b.id,
            title=f"[A/B - B안:{idea_b.angle}] {idea_b.hook[:25]}",
            body=writer_b.body,
            comments=[c.model_dump() for c in comments_b],
            status="APPROVED"
        )
        self.review_svc.audit_content(content_b.id)

        # Schedule both with time separation
        time_a = datetime.utcnow() + timedelta(hours=2)
        time_b = time_a + timedelta(hours=hours_apart)

        self.sched_svc.schedule_content(content_a.id, time_a)
        self.sched_svc.schedule_content(content_b.id, time_b)

        return {
            "status": "SUCCESS",
            "group_id": group_id,
            "product_id": product_id,
            "variant_a": {
                "content_id": content_a.id,
                "angle": idea_a.angle,
                "mode": variant_a_mode,
                "title": content_a.title,
                "scheduled_at": time_a.isoformat()
            },
            "variant_b": {
                "content_id": content_b.id,
                "angle": idea_b.angle,
                "mode": variant_b_mode,
                "title": content_b.title,
                "scheduled_at": time_b.isoformat()
            }
        }

    def evaluate_ab_winner(self, content_id_a: int, content_id_b: int) -> Dict[str, Any]:
        c_a = self.repo.get_content(content_id_a)
        c_b = self.repo.get_content(content_id_b)
        if not c_a or not c_b:
            raise ValueError("콘텐츠를 찾을 수 없습니다.")

        clicks_a = sum(m.clicks for m in c_a.metrics) if c_a.metrics else 0
        clicks_b = sum(m.clicks for m in c_b.metrics) if c_b.metrics else 0

        conv_a = sum(m.conversions for m in c_a.metrics) if c_a.metrics else 0
        conv_b = sum(m.conversions for m in c_b.metrics) if c_b.metrics else 0

        if conv_a > conv_b or (conv_a == conv_b and clicks_a >= clicks_b):
            winner = "A"
            winner_id = c_a.id
            margin = f"전환수 {conv_a}건 vs {conv_b}건 (클릭 {clicks_a} vs {clicks_b})"
        else:
            winner = "B"
            winner_id = c_b.id
            margin = f"전환수 {conv_b}건 vs {conv_a}건 (클릭 {clicks_b} vs {clicks_a})"

        return {
            "winner": winner,
            "winner_content_id": winner_id,
            "comparison": margin,
            "variant_a_clicks": clicks_a,
            "variant_b_clicks": clicks_b
        }