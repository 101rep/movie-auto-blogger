"""Unit tests for database models, relationships, and constraints."""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database.models import (
    AdminUser,
    AppSetting,
    AutomationEvent,
    AutomationRun,
    Media,
    Movie,
    Post,
    PostStatusEnum,
)


def test_movie_creation_and_unique_constraint(db_session: Session):
    """Test Movie model persistence and unique constraint on (source, external_id)."""
    movie1 = Movie(
        source="tmdb",
        external_id="12345",
        title="기생충",
        original_title="Parasite",
        popularity=98.5,
        vote_average=8.5,
        vote_count=15000,
        director="봉준호"
    )
    db_session.add(movie1)
    db_session.commit()
    assert movie1.id is not None

    # Duplicate insertion must raise IntegrityError
    movie_duplicate = Movie(
        source="tmdb",
        external_id="12345",
        title="기생충 재개봉"
    )
    db_session.add(movie_duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_post_creation_and_relationship(db_session: Session):
    """Test Post persistence linked to a Movie."""
    movie = Movie(
        source="tmdb",
        external_id="99999",
        title="인셉션",
        original_title="Inception"
    )
    db_session.add(movie)
    db_session.commit()

    post = Post(
        movie_id=movie.id,
        title="인셉션 영화 총정리 및 결말 해석",
        slug="inception-summary-review",
        excerpt="크리스토퍼 놀란 감독의 명작 인셉션에 대해 알아봅니다.",
        status=PostStatusEnum.COLLECTED.value,
        ai_requested_provider="openai",
        ai_used_provider="openai"
    )
    db_session.add(post)
    db_session.commit()

    assert post.id is not None
    assert post.movie.title == "인셉션"
    assert len(movie.posts) == 1


def test_automation_run_and_events(db_session: Session):
    """Test AutomationRun and AutomationEvent tracking."""
    run = AutomationRun(
        run_uuid="test-run-uuid-001",
        candidate_count=30,
        eligible_count=2,
        generated_count=2,
        scheduled_count=2,
        status="completed"
    )
    db_session.add(run)
    db_session.commit()

    event = AutomationEvent(
        run_id=run.id,
        stage="collector",
        event_code="CANDIDATES_DISCOVERED",
        message="30 candidate movies collected successfully."
    )
    db_session.add(event)
    db_session.commit()

    assert event.id is not None
    assert len(run.events) == 1
    assert run.events[0].event_code == "CANDIDATES_DISCOVERED"
