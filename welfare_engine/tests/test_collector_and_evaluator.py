"""Tests for Data Collector and 100-Point Evaluator Agent."""
import pytest
from datetime import date, timedelta
from welfare_engine.agent.collector import WelfareDataCollector, CORE_BASELINE_CATALOG
from welfare_engine.agent.evaluator import WelfareEvaluator
from welfare_engine.database.models import WelfareContent, ContentStatus, PriorityLevel


@pytest.mark.asyncio
async def test_01_collector_schema_and_normalization():
    """Verify collected items follow the strict 13-field normalized schema."""
    collector = WelfareDataCollector()
    items = await collector.collect_all(limit=5)
    assert len(items) >= 3

    required_keys = [
        "title", "source", "category", "target", "age", "region",
        "income_condition", "amount", "deadline", "apply_method",
        "documents", "url", "created_date"
    ]
    for item in items:
        for k in required_keys:
            assert k in item, f"Missing required field: {k}"
            assert item[k] is not None


def test_02_evaluator_scoring_breakdown_and_d_day():
    """Verify 100-point scoring model, D-Day urgency, and priority levels."""
    fixed_today = date(2026, 9, 24)
    evaluator = WelfareEvaluator(target_date=fixed_today)

    # 1. High-value policy with imminent deadline (D-3) and September Chuseok seasonality
    imminent_deadline = (fixed_today + timedelta(days=2)).strftime("%Y-%m-%d")
    item1 = WelfareContent(
        id=101,
        title="2026 추석 명절맞이 소상공인 정책자금 긴급지원 (최대 7,000만원)",
        source="중소벤처기업부",
        category="정책자금",
        target="상시근로자 5인 미만 소상공인 및 자영업자",
        amount="업체당 최대 7,000만원 한도 목돈 지원",
        deadline=imminent_deadline,
        region="서울"
    )

    total, level, breakdown = evaluator.evaluate_content(item1)
    # Scale: 25, Search: 25 (소상공인/정책자금), Audience: 17, Urgency: 15 (D-2), Season: 15 (9월 추석명절+서울)
    assert total >= 90
    assert level == PriorityLevel.IMMEDIATE.value
    assert "D-2" in breakdown["urgency_note"]
    assert "9월 시즈널" in breakdown["season_note"]

    # 2. Medium policy (D-20, standard scale)
    medium_deadline = (fixed_today + timedelta(days=20)).strftime("%Y-%m-%d")
    item2 = WelfareContent(
        id=102,
        title="일반 문화예술 바우처 지원 안내",
        source="문체부",
        category="문화바우처",
        target="저소득 취약계층",
        amount="연 10만원 지원",
        deadline=medium_deadline,
        region="전국"
    )
    total2, level2, breakdown2 = evaluator.evaluate_content(item2)
    assert 50 <= total2 < 90
    assert "D-20" in breakdown2["urgency_note"]

    # 3. Low-priority policy (expired deadline or tiny scope)
    expired_deadline = (fixed_today - timedelta(days=5)).strftime("%Y-%m-%d")
    item3 = WelfareContent(
        id=103,
        title="기타 소규모 정보안내",
        source="기타",
        category="단순안내",
        target="소수 특정인",
        amount="상담",
        deadline=expired_deadline,
        region="소도시"
    )
    total3, level3, breakdown3 = evaluator.evaluate_content(item3)
    assert total3 <= 50
    assert level3 == PriorityLevel.HOLD.value
    assert breakdown3["urgency_score"] == 0
