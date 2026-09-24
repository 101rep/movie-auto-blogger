"""Unit and integration tests for Entertainment & K-Culture vertical."""
import pytest
from app.collectors.entertainment import EntertainmentCollector, CORE_ENTERTAINMENT_CATALOG
from app.core.verticals import VerticalType, VerticalStatus, VERTICAL_METADATA
from app.modules.entertainment.module import EntertainmentModule
from app.database.session import SessionLocal


@pytest.mark.asyncio
async def test_entertainment_collector_catalog_and_discovery():
    """Verify EntertainmentCollector discovers topics and normalizes candidates."""
    collector = EntertainmentCollector(use_remote_feed=False)
    health = await collector.health_check()
    assert health["success"] is True
    assert health["catalog_count"] >= 4

    topics = await collector.discover_latest_news(limit=3)
    assert len(topics) == 3
    first = topics[0]
    assert first.topic_id.startswith("ENTER-")
    assert len(first.headline) > 5
    assert len(first.key_facts) > 0


@pytest.mark.asyncio
async def test_entertainment_module_contract_and_rendering():
    """Verify EntertainmentModule fulfills BaseContentModule contract and renders magazine layout."""
    module = EntertainmentModule()
    assert module.vertical == VerticalType.ENTERTAINMENT
    assert module.status == VerticalStatus.PRODUCTION
    assert VERTICAL_METADATA[VerticalType.ENTERTAINMENT]["name_ko"] == "연예 & K-컬처 매거진"

    # Test candidate collection
    db = SessionLocal()
    try:
        candidates = await module.collect_candidates(db, limit=2)
        assert len(candidates) >= 2
        cand = candidates[0]
        assert cand.vertical == VerticalType.ENTERTAINMENT
        assert cand.score > 0

        # Test enrichment
        enriched = await module.enrich_item(db, cand.external_id)
        assert "entertainment_item" in enriched
        assert enriched["entertainment_item"].topic_id == cand.external_id

        # Test content generation
        gen_data = await module.generate_content(db, enriched)
        assert "entertainment_article" in gen_data
        art = gen_data["entertainment_article"]
        assert art.title is not None
        assert len(art.timeline_events) > 0
        assert len(art.quick_summary_points) > 0

        # Test HTML rendering
        rendered_html = module.render_html(gen_data)
        assert "entertainment-article-wrap" in rendered_html
        assert "K-ENTERTAINMENT" in rendered_html
        assert "사건 전개 타임라인" in rendered_html
        assert "확인된 핵심 팩트" in rendered_html
        assert "https://schema.org" in rendered_html
        assert "NewsArticle" in rendered_html
        assert "FAQPage" in rendered_html
    finally:
        db.close()
