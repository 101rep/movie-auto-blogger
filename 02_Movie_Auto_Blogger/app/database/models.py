"""SQLAlchemy models for Movie Auto Blogger v1.

Matches Master PRD Section 30 specifications:
- movies
- posts
- media
- automation_runs
- automation_events
- settings
- admin_users
"""
from datetime import datetime, timezone
import enum
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.base import Base


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class JobStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    PROCESSING = "PROCESSING"
    QUALITY_CHECK = "QUALITY_CHECK"
    PUBLISHING = "PUBLISHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRY_WAIT = "RETRY_WAIT"


class PostStatusEnum(str, enum.Enum):
    COLLECTED = "COLLECTED"
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    GENERATING = "GENERATING"
    PROCESSING = "PROCESSING"
    GENERATED = "GENERATED"
    QUALITY_CHECK = "QUALITY_CHECK"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    PUBLISHING = "PUBLISHING"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRY_WAIT = "RETRY_WAIT"


class QualityStatusEnum(str, enum.Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    FAIL = "FAIL"


class Movie(Base):
    """Normalized movie candidate and details model."""
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="tmdb")
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    overview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    release_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    runtime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    genres_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    popularity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vote_average: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vote_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    director: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cast_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    poster_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    backdrop_reference: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    candidate_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    naver_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    naver_rating_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    naver_vote_count: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    imdb_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    imdb_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    imdb_votes: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    rotten_tomatoes_score: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metacritic_score: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    watcha_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    @property
    def poster_url(self) -> Optional[str]:
        return self.poster_reference

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="movie", cascade="all, delete-orphan")
    media: Mapped[List["Media"]] = relationship("Media", back_populates="movie", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_movies_source_external_id"),
        Index("ix_movies_source_external_id", "source", "external_id"),
    )


class Post(Base):
    """Article post model tracking generation, validation, and WordPress publication."""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    article_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rendered_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seo_title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Multi-Vertical & Site Architecture
    vertical: Mapped[str] = mapped_column(String(50), nullable=False, default="MOVIE", index=True)
    site_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True)

    # AI tracking
    ai_requested_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_used_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="v1.0")
    generator_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="1.0")
    quality_profile: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="default")
    experience_grounding_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # PASS, REVIEW, FAIL, N/A

    # Quality and status
    quality_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # PASS, REVIEW, FAIL
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=PostStatusEnum.COLLECTED.value,
        index=True
    )

    # WordPress details
    wordpress_post_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    wordpress_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationship
    movie: Mapped["Movie"] = relationship("Movie", back_populates="posts")
    site: Mapped[Optional["Site"]] = relationship("Site", back_populates="posts")


class Media(Base):
    """Media asset model tracking images and WordPress media uploads."""
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), default="poster")  # poster, backdrop
    wordpress_media_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wordpress_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, uploaded, failed
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationship
    movie: Mapped["Movie"] = relationship("Movie", back_populates="media")


class AutomationRun(Base):
    """Tracks each execution of the daily or manual automation pipeline."""
    __tablename__ = "automation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    candidate_count: Mapped[int] = mapped_column(Integer, default=0)
    eligible_count: Mapped[int] = mapped_column(Integer, default=0)
    generated_count: Mapped[int] = mapped_column(Integer, default=0)
    scheduled_count: Mapped[int] = mapped_column(Integer, default=0)
    published_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(50), default="running")  # running, completed, failed
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationship
    events: Mapped[List["AutomationEvent"]] = relationship(
        "AutomationEvent", back_populates="run", cascade="all, delete-orphan"
    )


class AutomationEvent(Base):
    """Event log entries for an automation run (Never stores secrets)."""
    __tablename__ = "automation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("automation_runs.id", ondelete="CASCADE"), nullable=True
    )
    stage: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, error
    event_code: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationship
    run: Mapped[Optional["AutomationRun"]] = relationship("AutomationRun", back_populates="events")


class AppSetting(Base):
    """Non-secret operational settings stored in the database."""
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class AdminUser(Base):
    """Admin user account for authenticated dashboard access."""
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Site(Base):
    """Multi-site publishing target configuration."""
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    site_url: Mapped[str] = mapped_column(String(255), nullable=False)
    vertical: Mapped[str] = mapped_column(String(50), nullable=False, default="MOVIE")
    wp_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    wp_application_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="site")


class ContentJob(Base):
    """Job lock and execution tracker preventing duplicate processing."""
    __tablename__ = "content_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    movie_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=True, index=True)
    post_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True, index=True)
    job_type: Mapped[str] = mapped_column(String(50), default="movie_article", index=True)
    status: Mapped[str] = mapped_column(String(30), default=JobStatusEnum.PENDING.value, index=True)

    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retry: Mapped[int] = mapped_column(Integer, default=3)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # TRANSIENT, PERMANENT
    is_retryable: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    movie: Mapped[Optional["Movie"]] = relationship("Movie")
    post: Mapped[Optional["Post"]] = relationship("Post")


class InterviewSessionModel(Base):
    """Persistent storage for Experience Interview sessions and Context Notebooks."""
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(300), nullable=False)
    main_keyword: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    vertical: Mapped[str] = mapped_column(String(50), default="EXPERIENCE")
    status: Mapped[str] = mapped_column(String(30), default="IN_PROGRESS", index=True)
    current_round: Mapped[int] = mapped_column(Integer, default=0)

    turns_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context_notebook_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outline_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    draft_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grounding_report_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    post_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("posts.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    post: Mapped[Optional["Post"]] = relationship("Post")


