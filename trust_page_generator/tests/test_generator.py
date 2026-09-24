"""Tests for Trust Page Generator HTML, AdSense compliance, and 64 page coverage."""
from trust_page_generator.identities import MASTER_IDENTITIES
from trust_page_generator.generator import TrustPageGenerator
from trust_page_generator.database.session import init_db, SessionLocal
from trust_page_generator.database.models import TrustPage


def test_01_all_8_pages_generated_for_single_blog():
    """Verify all 8 mandatory trust pages are generated for Blog 1 (Travel)."""
    gen = TrustPageGenerator()
    pages = gen.generate_all_pages_for_blog(1)
    assert len(pages) == 8

    slugs = [p["slug"] for p in pages]
    expected_slugs = [
        "about-us",
        "editorial-policy",
        "verification-policy",
        "privacy-policy",
        "terms",
        "contact",
        "correction-policy",
        "partnership"
    ]
    for s in expected_slugs:
        assert s in slugs, f"Missing slug: {s}"

    # Verify content quality
    about_page = next(p for p in pages if p["slug"] == "about-us")
    assert "트래블픽24" in about_page["content"]
    assert "공식 사이트 소개" in about_page["content"]

    privacy_page = next(p for p in pages if p["slug"] == "privacy-policy")
    assert "Google AdSense" in privacy_page["content"]
    assert "쿠키" in privacy_page["content"]
    assert "adssettings.google.com" in privacy_page["content"]

    verification_page = next(p for p in pages if p["slug"] == "verification-policy")
    assert "한국관광공사" in verification_page["content"] or "팩트체크" in verification_page["content"]


def test_02_build_and_save_all_to_db():
    """Verify all 64 pages (8 blogs x 8 pages) are persisted into database."""
    init_db()
    gen = TrustPageGenerator()
    total_saved = gen.build_and_save_all_to_db()
    assert total_saved == 64

    db = SessionLocal()
    try:
        count = db.query(TrustPage).count()
        assert count == 64
        # Verify status is READY
        ready_count = db.query(TrustPage).filter(TrustPage.status == "READY").count()
        assert ready_count == 64
    finally:
        db.close()
