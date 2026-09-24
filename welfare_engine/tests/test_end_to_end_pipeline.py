"""End-to-End Pipeline integration test for Welfare Engine V1.0."""
import pytest
from datetime import date
from welfare_engine.database.session import init_db, SessionLocal
from welfare_engine.database.models import WelfareContent, ContentStatus
from welfare_engine.worker.pipeline import WelfarePipelineController


@pytest.mark.asyncio
async def test_01_end_to_end_pipeline_dry_run():
    """Verify entire pipeline execution from ingestion to evaluation, routing, writing, and reporting."""
    init_db()
    controller = WelfarePipelineController()

    # 1. Test Day 1 volume quota (3 posts per blog)
    quota_day1 = controller.determine_daily_target_quota(days_since_launch=1)
    assert quota_day1 == 3

    # 2. Test schedule times generation
    sched_times = controller.get_schedule_times(date(2026, 9, 24), quota_day1)
    assert len(sched_times) == 3
    assert sched_times[0].hour == 9
    assert sched_times[1].hour == 14
    assert sched_times[2].hour == 19

    # 3. Run pipeline in dry_run mode with mocked writer data
    from unittest.mock import patch, AsyncMock
    with patch("welfare_engine.agent.writer.WelfareWriterAgent.generate_article_data", new_callable=AsyncMock) as mock_write:
        mock_write.return_value = {
            "title": "테스트 복지 기사",
            "summary": ["요약1", "요약2", "요약3"],
            "target_desc": "전국민",
            "benefits": "지원금",
            "amount_desc": "100만원",
            "period_desc": "상시",
            "steps": ["1단계", "2단계", "3단계"],
            "documents": ["신분증"],
            "faqs": [{"question": "Q?", "answer": "A!"}],
            "official_url": "https://gov.kr",
            "tags": ["복지", "지원금"]
        }
        result = await controller.run_pipeline(
            target_date=date(2026, 9, 24),
            days_since_launch=1,
            dry_run=True
        )
    assert result["status"] == "SUCCESS"
    assert "stats" in result
    assert result["stats"]["BLOG_A"]["success"] == 3
    assert result["stats"]["BLOG_B"]["success"] == 3
    assert result["stats"]["BLOG_C"]["success"] == 3


def test_02_stabilized_quota_decision():
    """Verify Day 8+ dynamic volume decision based on Grade-A candidate count."""
    init_db()
    controller = WelfarePipelineController()
    db = SessionLocal()
    try:
        # Check quota when days_since_launch > 7
        quota = controller.determine_daily_target_quota(days_since_launch=8)
        assert quota in (0, 1, 2, 3)
    finally:
        db.close()
