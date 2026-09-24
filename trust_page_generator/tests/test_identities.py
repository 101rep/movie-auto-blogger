"""Tests for 8 Blog Brand Identities (PRD Principle 1 & 2)."""
from trust_page_generator.identities import MASTER_IDENTITIES, sync_identities_to_db
from trust_page_generator.database.session import init_db, SessionLocal
from trust_page_generator.database.models import BlogIdentity


def test_01_identities_completeness_and_differentiation():
    """Verify all 8 blogs have fully distinct identities and missions."""
    assert len(MASTER_IDENTITIES) == 8

    brand_names = set()
    missions = set()
    tones = set()
    categories = set()

    for blog_id, ident in MASTER_IDENTITIES.items():
        assert ident["brand_name"] not in brand_names, f"Duplicate brand name: {ident['brand_name']}"
        assert ident["mission"] not in missions, f"Duplicate mission: {ident['mission']}"
        assert ident["tone"] not in tones, f"Duplicate tone: {ident['tone']}"

        brand_names.add(ident["brand_name"])
        missions.add(ident["mission"])
        tones.add(ident["tone"])
        categories.add(ident["category"])

        # Check required fields
        for field in ["blog_id", "brand_name", "domain", "category", "mission", "target_user", "tone", "content_policy", "trust_message", "email"]:
            assert field in ident
            assert len(str(ident[field])) > 0

    assert len(brand_names) == 8
    assert len(missions) == 8


def test_02_identities_db_sync():
    """Verify syncing identities into database works cleanly."""
    init_db()
    synced = sync_identities_to_db()
    assert len(synced) == 8

    db = SessionLocal()
    try:
        count = db.query(BlogIdentity).count()
        assert count == 8
    finally:
        db.close()
