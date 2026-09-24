"""Unit and integration tests for Gov24 Public Data Portal Welfare Integration."""
import pytest
from app.collectors.gov24_welfare import Gov24WelfareClient, gov24_welfare_client
from app.collectors.welfare import WelfareCollector
from app.modules.welfare.module import WelfareModule
from app.database.session import SessionLocal


@pytest.mark.asyncio
async def test_01_gov24_client_search_and_detail():
    """Verify Gov24 client queries real services and details from public data portal."""
    client = Gov24WelfareClient()
    services = await client.search_services("청년", page=1, per_page=2, central_only=True)
    assert len(services) > 0
    first = services[0]
    assert "서비스명" in first
    assert "서비스ID" in first

    svc_id = first["서비스ID"]
    detail = await client.get_service_detail(svc_id)
    assert detail is not None
    assert detail.get("서비스ID") == svc_id

    # Test parser helpers
    checklist = client.extract_checklist(detail.get("선정기준"), detail.get("지원대상"))
    assert len(checklist) >= 1
    steps = client.extract_steps(detail.get("신청방법"))
    assert len(steps) >= 1
    docs = client.extract_documents(detail.get("구비서류"))
    assert len(docs) >= 1


@pytest.mark.asyncio
async def test_02_stats_fact_box_grounding():
    """Verify statistical fact boxes are generated for childcare, health, pension, youth."""
    client = Gov24WelfareClient()
    
    # Childcare / Infant (ODMS_STAT_21)
    box_child = client.get_grounding_stats_box("영유아보육료 지원", "교육부")
    assert "보육아동" in box_child
    assert "누리과정" in box_child

    # Medical / Health (ODMS_STAT_30, ODMS_STAT_12)
    box_med = client.get_grounding_stats_box("의료급여 지원", "보건복지부")
    assert "건강보험" in box_med
    assert "의료" in box_med

    # Senior / Pension
    box_pension = client.get_grounding_stats_box("기초연금 지급", "보건복지부")
    assert "기초연금" in box_pension

    # Youth / Employment
    box_youth = client.get_grounding_stats_box("청년내일저축계좌", "보건복지부")
    assert "청년" in box_youth


@pytest.mark.asyncio
async def test_03_site_specialized_discovery():
    """Verify site-specialized policy discovery for Welfare23, Welfare24, Welfare25."""
    collector = WelfareCollector()
    
    # Site 5: Welfare23 (청년/취업/주거)
    site5_items = await collector.discover_policies_for_site(site_id=5, limit=3)
    assert len(site5_items) >= 1
    assert any(any(k in item.service_name for k in ["청년", "취업", "주거", "일자리", "자산", "학자금"]) for item in site5_items)

    # Site 6: Welfare24 (시니어/소상공인/연금)
    site6_items = await collector.discover_policies_for_site(site_id=6, limit=3)
    assert len(site6_items) >= 1

    # Site 7: Welfare25 (보육/아동/바우처/의료)
    site7_items = await collector.discover_policies_for_site(site_id=7, limit=3)
    assert len(site7_items) >= 1


@pytest.mark.asyncio
async def test_04_welfare_module_with_gov24_candidate():
    """Verify WelfareModule collects and renders HTML with Gov24 official grounding."""
    module = WelfareModule()
    db = SessionLocal()
    try:
        # Collect for Welfare25 (보육/바우처/의료)
        candidates = await module.collect_candidates(db, limit=2, site_id=7)
        assert len(candidates) >= 1
        cand = candidates[0]
        assert cand.external_id is not None
        assert "data.go.kr" in cand.source_attribution or "정부" in cand.source_attribution

        # Enrich
        enriched = await module.enrich_item(db, cand.external_id)
        assert "welfare_item" in enriched
        w_item = enriched["welfare_item"]
        assert len(w_item.eligibility_checklist) > 0

        # Generate content
        gen_data = await module.generate_content(db, enriched)
        assert gen_data["status"] == "SUCCESS"

        # Render HTML
        html = module.render_html(gen_data)
        assert "welfare-article-wrap" in html
        assert "누가 지원받을 수 있나요?" in html
        assert "어떤 혜택을 얼마나 받나요?" in html
        assert "어떻게 신청하나요?" in html
        assert "공식 신청 홈페이지 바로가기" in html
        assert "application/ld+json" in html
        # Check if official grounding or stats fact box is rendered
        assert "공식" in html
    finally:
        db.close()
