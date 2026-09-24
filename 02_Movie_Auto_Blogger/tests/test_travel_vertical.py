"""Unit and integration tests for the Travel vertical."""
import pytest
from app.collectors.travel import TravelCollector, CORE_TRAVEL_CATALOG
from app.core.verticals import VerticalType, VerticalStatus, VERTICAL_METADATA
from app.modules.travel.module import TravelModule
from app.database.session import SessionLocal


@pytest.mark.asyncio
async def test_travel_collector_catalog_and_discovery():
    """Verify TravelCollector discovers popular domestic and global destinations."""
    collector = TravelCollector()
    health = await collector.health_check()
    assert health["success"] is True
    assert health["catalog_count"] >= 5

    destinations = await collector.discover_popular_destinations(limit=4)
    assert len(destinations) == 4
    
    names = [d.destination for d in destinations]
    assert any("오사카" in n or "후쿠오카" in n or "다낭" in n for n in names)

    first = destinations[0]
    assert first.destination_id.startswith("TRAVEL-")
    assert len(first.highlights) > 0
    assert len(first.spots) > 0
    assert "원" in first.budget_guide or "예산" in first.budget_guide


@pytest.mark.asyncio
async def test_travel_module_contract_and_rendering():
    """Verify TravelModule fulfills BaseContentModule contract and renders valid rich HTML."""
    module = TravelModule()
    assert module.vertical == VerticalType.TRAVEL
    assert module.status == VerticalStatus.PRODUCTION
    assert VERTICAL_METADATA[VerticalType.TRAVEL]["name_ko"] == "여행 & 명소 가이드"

    # Test candidate collection
    db = SessionLocal()
    try:
        candidates = await module.collect_candidates(db, limit=2)
        assert len(candidates) >= 2
        cand = candidates[0]
        assert cand.vertical == VerticalType.TRAVEL
        assert cand.score > 0

        # Test enrichment
        enriched = await module.enrich_item(db, cand.external_id)
        assert "travel_item" in enriched
        assert enriched["travel_item"].destination_id == cand.external_id

        # Test content generation
        gen_data = await module.generate_content(db, enriched)
        assert "travel_article" in gen_data
        art = gen_data["travel_article"]
        assert art.title is not None
        assert len(art.itinerary_days) > 0
        assert len(art.must_visit_spots) > 0

        # Test HTML rendering
        html = module.render_html(gen_data)
        assert "travel-guide-article" in html
        assert "Day 1" in html
        assert "아고다" in html or "agoda" in html
        assert "TouristDestination" in html
        assert "FAQPage" in html
    finally:
        db.close()
