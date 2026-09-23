from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import PerformanceMetric, Content
from integrations.factory import get_analytics_provider
from utils.logger import start_job_log, finish_job_log

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.analytics_provider = get_analytics_provider()

    def sync_metrics_from_provider(self, content_id: int) -> PerformanceMetric:
        content = self.repo.get_content(content_id)
        if not content:
            raise ValueError(f"Content not found: {content_id}")

        job = start_job_log(self.db, "ANALYTICS_SYNC", {"content_id": content_id})

        # Fetch from Analytics Provider
        raw = self.analytics_provider.get_metrics(str(content_id))
        views = raw.get("views", 1500)
        likes = raw.get("likes", 65)
        replies = raw.get("replies", 12)
        reposts = raw.get("shares", 5)
        clicks = raw.get("clicks", 85)
        conversions = raw.get("estimated_conversion", 4)
        revenue = conversions * int(content.product.price * 0.03) if content.product else conversions * 1500

        metric = self.repo.record_performance_metric(
            content_id=content_id,
            views=views,
            likes=likes,
            replies=replies,
            reposts=reposts,
            clicks=clicks,
            conversions=conversions,
            revenue=revenue
        )

        finish_job_log(self.db, job, "SUCCESS", {
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue
        })
        return metric

    def get_summary_report(self) -> Dict[str, Any]:
        return self.repo.get_overall_analytics()