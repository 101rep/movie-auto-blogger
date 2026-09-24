"""Test suite for Product & Commerce Review Vertical (ItemPick24)."""
import pytest
from app.core.verticals import VerticalType, VerticalStatus
from app.modules.product.module import ProductModule
from app.database.session import SessionLocal
from app.database.models import Site


def test_product_module_registration():
    """Verify that ProductModule registers correctly in platform registry."""
    mod = ProductModule()
    assert mod.vertical == VerticalType.PRODUCT
    assert mod.status == VerticalStatus.PRODUCTION


@pytest.mark.asyncio
async def test_product_module_candidates_and_render():
    """Test candidate discovery, enrichment, generation, and HTML rendering."""
    mod = ProductModule()
    with SessionLocal() as db:
        candidates = await mod.collect_candidates(db, limit=4)
        assert len(candidates) >= 1
        first = candidates[0]
        assert first.vertical == VerticalType.PRODUCT
        assert "실사용" in first.title or first.original_title is not None

        enriched = await mod.enrich_item(db, first.external_id)
        assert "product" in enriched

        gen = await mod.generate_content(db, enriched)
        assert "title" in gen
        assert "body" in gen

        html = mod.render_html(gen)
        assert "실사용자 3줄 핵심 요약" in html
        assert "핵심 스펙 및 제품 사양표" in html
        assert "솔직하게 짚어보는 장점과 아쉬운 점" in html
        assert "공정하게 작성되었으며" in html


def test_product_site_registration():
    """Verify that a PRODUCT site can be registered and queried."""
    with SessionLocal() as db:
        site = Site(
            name="아이템픽24 (ItemPick24)",
            site_url="https://wordpress-1670576-6680151.cloudwaysapps.com",
            vertical="PRODUCT",
            wp_username="ktaehoon80@gmail.com",
            wp_application_password="UWhD nkd8 OLpG Q91f 8dSx 0avk",
            is_active=True,
        )
        db.add(site)
        db.commit()

        queried = db.query(Site).filter(Site.vertical == "PRODUCT").first()
        assert queried is not None
        assert queried.is_active is True
        assert "cloudwaysapps.com" in queried.site_url
