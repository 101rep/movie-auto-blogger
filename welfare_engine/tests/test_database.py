"""Unit tests for Welfare Engine Database and Session Lifecycle (ADR-004 & Rule 5)."""
import uuid
import pytest
from datetime import datetime
from welfare_engine.database.session import init_db, SessionLocal, get_db
from welfare_engine.database.models import (
    WelfareContent, WelfarePublication, ContentStatus, PriorityLevel
)


def test_01_init_db_and_create_content():
    """Verify database initialization, schema constraints, and content creation."""
    init_db()
    unique_hash = f"hash_test_{uuid.uuid4().hex}"

    with get_db() as db:
        # Create test item
        content = WelfareContent(
            title="테스트 청년지원 정책",
            source="정부24",
            category="청년지원",
            target="청년",
            age="만 19~34세",
            region="서울",
            amount="월 20만원",
            deadline="2026-12-31",
            url=f"https://gov.kr/test-policy-{unique_hash}",
            duplicate_hash=unique_hash,
            status=ContentStatus.NEW.value
        )
        db.add(content)
        db.commit()
        db.refresh(content)
        assert content.id is not None
        assert content.status == ContentStatus.NEW.value

        # Test duplicate hash rejection
        dup = WelfareContent(
            title="중복 정책",
            source="정부24",
            url=f"https://gov.kr/test-policy-{unique_hash}",
            duplicate_hash=unique_hash
        )
        db.add(dup)
        with pytest.raises(Exception):
            db.commit()
        db.rollback()


def test_02_status_transitions_and_publication_relation():
    """Verify content lifecycle transitions (NEW -> READY -> PUBLISHED) and relationship."""
    unique_hash = f"hash_relation_{uuid.uuid4().hex}"

    with get_db() as db:
        content = WelfareContent(
            title="관계 테스트 복지 정책",
            source="정부24",
            category="생활지원",
            target="전국민",
            url=f"https://gov.kr/test-policy-{unique_hash}",
            duplicate_hash=unique_hash,
            status=ContentStatus.NEW.value
        )
        db.add(content)
        db.commit()
        db.refresh(content)

        # Transition to READY
        content.status = ContentStatus.READY.value
        content.priority_score = 92
        content.priority_level = PriorityLevel.IMMEDIATE.value
        db.commit()

        # Add publication record
        pub = WelfarePublication(
            content_id=content.id,
            blog_key="BLOG_A",
            site_id=7,
            persona_title="[복지 상담사] 청년지원 정책 신청 가이드",
            wp_post_id=12345,
            wp_url="https://welfare25.travelpick24.com/post-12345",
            wp_status="future",
            verification_status="VERIFIED"
        )
        db.add(pub)
        db.commit()

        content.status = ContentStatus.PUBLISHED.value
        content.published_blog = "BLOG_A"
        db.commit()

        # Verify relation
        db.refresh(content)
        assert len(content.publications) == 1
        assert content.publications[0].wp_post_id == 12345
        assert content.publications[0].verification_status == "VERIFIED"
