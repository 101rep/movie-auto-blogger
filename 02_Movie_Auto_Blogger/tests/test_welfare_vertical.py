"""Unit and integration tests for the Welfare & Government Support vertical."""
import pytest
from app.collectors.welfare import WelfareCollector, CORE_WELFARE_CATALOG
from app.core.verticals import VerticalType, VerticalStatus, VERTICAL_METADATA
from app.modules.welfare.module import WelfareModule
from app.database.session import SessionLocal


@pytest.mark.asyncio
async def test_welfare_collector_catalog_and_discovery():
    """Verify WelfareCollector exposes high-demand Korean welfare programs."""
    collector = WelfareCollector(use_remote_feed=False)
    health = await collector.health_check()
    assert health["success"] is True
    assert health["catalog_count"] >= 5

    candidates = await collector.discover_latest_policies(limit=3)
    assert len(candidates) == 3
    # Verify core Korean welfare items are normalized
    titles = [c.service_name for c in candidates]
    assert any("청년" in t or "근로장려금" in t or "부모급여" in t for t in titles)

    first = candidates[0]
    assert first.service_id.startswith("WELFARE-")
    assert first.apply_url.startswith("http")
    assert len(first.eligibility_checklist) > 0
    assert len(first.application_steps) > 0


@pytest.mark.asyncio
async def test_welfare_module_contract_and_rendering():
    """Verify WelfareModule fulfills BaseContentModule contract and renders valid E-E-A-T HTML."""
    module = WelfareModule()
    assert module.vertical == VerticalType.WELFARE
    assert module.status == VerticalStatus.PRODUCTION
    assert VERTICAL_METADATA[VerticalType.WELFARE]["name_ko"] == "복지 & 지원금 포털"

    # Test candidate collection
    db = SessionLocal()
    try:
        candidates = await module.collect_candidates(db, limit=2)
        assert len(candidates) >= 2
        cand = candidates[0]
        assert cand.vertical == VerticalType.WELFARE
        assert cand.score > 0

        # Test enrichment
        enriched = await module.enrich_item(db, cand.external_id)
        assert "welfare_item" in enriched
        assert enriched["welfare_item"].service_id == cand.external_id

        # Test content generation
        gen_data = await module.generate_content(db, enriched)
        assert "welfare_article" in gen_data
        art = gen_data["welfare_article"]
        assert art.title is not None
        assert len(art.eligibility_checklist) > 0
        assert len(art.required_documents) > 0

        # Test HTML rendering
        rendered_html = module.render_html(gen_data)
        assert "welfare-article-wrap" in rendered_html
        assert "대한민국 정부 복지" in rendered_html
        assert "누가 지원받을 수 있나요?" in rendered_html
        assert "공식 신청 홈페이지 바로가기" in rendered_html
        assert "https://schema.org" in rendered_html
        assert "GovernmentService" in rendered_html
        assert "FAQPage" in rendered_html
    finally:
        db.close()
