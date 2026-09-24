"""Tests for WordPress Trust Page Publisher and dry-run deployment."""
import pytest
from trust_page_generator.config import BLOG_REGISTRY
from trust_page_generator.generator import TrustPageGenerator
from trust_page_generator.publisher import WordPressTrustPagePublisher
from trust_page_generator.database.session import init_db


@pytest.mark.asyncio
async def test_01_publisher_auth_and_dry_run():
    """Verify publisher dry-run deployment works across all 8 blogs."""
    init_db()
    gen = TrustPageGenerator()
    gen.build_and_save_all_to_db()

    cfg = BLOG_REGISTRY[1]
    pub = WordPressTrustPagePublisher(cfg)
    assert pub.auth_header.startswith("Basic ")

    # Run dry-run
    res = await pub.deploy_all_for_blog(dry_run=True)
    assert res["success_count"] == 8
    assert res["failed_count"] == 0
    assert len(res["details"]) == 8
    for d in res["details"]:
        assert d["status"] == "DRY_RUN_OK"
        assert d["url"].startswith("https://travelpick24.com/")
