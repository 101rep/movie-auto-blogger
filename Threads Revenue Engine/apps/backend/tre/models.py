from typing import Any
from sqlalchemy import String, Text, Integer, Boolean, Float, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base, UTCDateTime, now

class Identity:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, default=now)

class User(Identity, Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)

class Session(Identity, Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[Any] = mapped_column(UTCDateTime)

class LoginAttempt(Identity, Base):
    __tablename__ = "login_attempts"
    address: Mapped[str] = mapped_column(String(100), index=True)

class Account(Identity, Base):
    __tablename__ = "accounts"
    name: Mapped[str] = mapped_column(String(100))
    platform: Mapped[str] = mapped_column(String(30), default="threads")
    username: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default="ONLINE")
    timezone: Mapped[str] = mapped_column(String(80), default="Asia/Seoul")
    daily_post_limit: Mapped[int] = mapped_column(default=3)
    daily_affiliate_limit: Mapped[int] = mapped_column(default=1)
    minimum_interval: Mapped[int] = mapped_column(default=60)
    affiliate_ratio: Mapped[float] = mapped_column(default=0.2)
    content_ratios: Mapped[dict] = mapped_column(JSON, default=lambda: {"INFORMATION":50,"ENGAGEMENT":20,"TRUST":10,"AFFILIATE":20})
    reply_count: Mapped[int] = mapped_column(default=1)
    default_language: Mapped[str] = mapped_column(String(20), default="ko")
    access_token_reference: Mapped[str | None] = mapped_column(String(100))
    token_expire_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    last_success_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    last_error_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    updated_at: Mapped[Any] = mapped_column(UTCDateTime, default=now, onupdate=now)

class Persona(Identity, Base):
    __tablename__ = "personas"
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), unique=True)
    target_description: Mapped[str] = mapped_column(Text, default="")
    primary_desire: Mapped[str] = mapped_column(Text, default="시간 절약")
    secondary_desire: Mapped[str] = mapped_column(Text, default="돈 절약")
    pain_points: Mapped[list] = mapped_column(JSON, default=list)
    tone: Mapped[str] = mapped_column(String(80), default="친근한")
    speech_style: Mapped[str] = mapped_column(String(30), default="존댓말")
    emoji_level: Mapped[int] = mapped_column(default=0)
    hook_preferences: Mapped[list] = mapped_column(JSON, default=list)
    prohibited_styles: Mapped[list] = mapped_column(JSON, default=list)
    content_objectives: Mapped[list] = mapped_column(JSON, default=list)
    ai_strategy: Mapped[dict] = mapped_column(JSON, default=lambda: {'research':'gemini','writing':'claude','review':'gpt'})
    updated_at: Mapped[Any] = mapped_column(UTCDateTime, default=now, onupdate=now)

class InstagramAccount(Identity, Base):
    __tablename__ = 'instagram_accounts'
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), unique=True)
    instagram_id: Mapped[str | None] = mapped_column(String(100))
    business_account_id: Mapped[str | None] = mapped_column(String(100))
    access_token: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default='ONLINE')
    last_publish_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    token_expire_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    threads_ratio: Mapped[float] = mapped_column(Float, default=0.5)
    instagram_ratio: Mapped[float] = mapped_column(Float, default=0.3)
    blog_ratio: Mapped[float] = mapped_column(Float, default=0.2)


class ContentSource(Identity, Base):
    __tablename__ = "content_sources"
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(30), default="MANUAL")
    url: Mapped[str | None] = mapped_column(Text)

class ContentItem(Identity, Base):
    __tablename__ = "content_items"
    source_id: Mapped[int] = mapped_column(ForeignKey("content_sources.id"))
    source_url: Mapped[str | None] = mapped_column(Text)
    source_title: Mapped[str] = mapped_column(String(200))
    source_text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20), default="ko")
    published_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    collected_at: Mapped[Any] = mapped_column(UTCDateTime, default=now)
    hash: Mapped[str] = mapped_column(String(64), unique=True)
    category: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default="RAW")

class ContentAnalysis(Identity, Base):
    __tablename__ = "content_analyses"
    content_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"), unique=True)
    result: Mapped[dict] = mapped_column(JSON)
    provider: Mapped[str] = mapped_column(String(40), default="MOCK")

class Product(Identity, Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("provider", "external_product_id"),)
    provider: Mapped[str] = mapped_column(String(40))
    external_product_id: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(Text)
    affiliate_url: Mapped[str] = mapped_column(Text)
    price: Mapped[float | None] = mapped_column(Float)
    rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None] = mapped_column(Integer)
    delivery_type: Mapped[str | None] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(80))
    image_url: Mapped[str | None] = mapped_column(Text)
    last_checked_at: Mapped[Any] = mapped_column(UTCDateTime, default=now)
    active: Mapped[bool] = mapped_column(default=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

class Post(Identity, Base):
    __tablename__ = "posts"
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content_items.id"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    body: Mapped[str] = mapped_column(Text)
    goal: Mapped[str] = mapped_column(String(30), default="INFORMATION")
    angle: Mapped[str] = mapped_column(String(30), default="PROBLEM_SOLUTION")
    hook_type: Mapped[str] = mapped_column(String(30), default="OBSERVATION")
    status: Mapped[str] = mapped_column(String(30), default="GENERATED", index=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    validation: Mapped[dict] = mapped_column(JSON, default=dict)
    approved_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    scheduled_at: Mapped[Any | None] = mapped_column(UTCDateTime, index=True)
    published_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    remote_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    error_code: Mapped[str | None] = mapped_column(String(80))
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(default=0)
    next_retry_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    mock: Mapped[bool] = mapped_column(default=True)

class PostReply(Identity, Base):
    __tablename__ = "post_replies"
    __table_args__ = (UniqueConstraint("post_id", "position"),)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    position: Mapped[int] = mapped_column(Integer)
    body: Mapped[str] = mapped_column(Text)
    remote_id: Mapped[str | None] = mapped_column(String(120))

class PublicationReservation(Base):
    __tablename__ = "publication_reservations"
    fingerprint: Mapped[str] = mapped_column(String(64), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), unique=True)

class AccountProductHistory(Identity, Base):
    __tablename__ = "account_product_history"
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), unique=True)
    published_at: Mapped[Any] = mapped_column(UTCDateTime, default=now)
    angle: Mapped[str] = mapped_column(String(30))
    hook_type: Mapped[str] = mapped_column(String(30))
    performance_score: Mapped[float | None] = mapped_column(Float)

class Job(Identity, Base):
    __tablename__ = "jobs"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), unique=True)
    state: Mapped[str] = mapped_column(String(30), default="WAITING", index=True)
    due_at: Mapped[Any] = mapped_column(UTCDateTime, index=True)
    lease_until: Mapped[Any | None] = mapped_column(UTCDateTime)
    claim_token: Mapped[str | None] = mapped_column(String(64))
    attempts: Mapped[int] = mapped_column(default=0)

class JobAttempt(Identity, Base):
    __tablename__ = "job_attempts"
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    number: Mapped[int] = mapped_column(Integer)
    result: Mapped[str] = mapped_column(String(30))
    error_code: Mapped[str | None] = mapped_column(String(80))

class Notification(Identity, Base):
    __tablename__ = "notifications"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    event_key: Mapped[str] = mapped_column(String(100), unique=True)
    body: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(30), default="PENDING")
    remote_id: Mapped[str | None] = mapped_column(String(100))
    mock: Mapped[bool] = mapped_column(default=True)
    error_code: Mapped[str | None] = mapped_column(String(80))

class SystemSetting(Base):
    __tablename__ = "system_settings"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[Any] = mapped_column(JSON)

class AuditLog(Identity, Base):
    __tablename__ = "audit_logs"
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(100))
    target: Mapped[str | None] = mapped_column(String(100))
    service: Mapped[str] = mapped_column(String(30), default="application")
    level: Mapped[str] = mapped_column(String(20), default="INFO")
    request_id: Mapped[str | None] = mapped_column(String(100))
    error_code: Mapped[str | None] = mapped_column(String(80))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeats"
    name: Mapped[str] = mapped_column(String(80), primary_key=True)
    seen_at: Mapped[Any] = mapped_column(UTCDateTime, default=now)

class MockRemotePost(Identity, Base):
    __tablename__ = "mock_remote_posts"
    key: Mapped[str] = mapped_column(String(100), unique=True)
    remote_id: Mapped[str] = mapped_column(String(100), unique=True)
    body: Mapped[str] = mapped_column(Text)
    parent_id: Mapped[str | None] = mapped_column(String(100))

class WorkerLease(Base):
    __tablename__ = 'worker_leases'
    name: Mapped[str] = mapped_column(String(40), primary_key=True)
    owner: Mapped[str | None] = mapped_column(String(64))
    until: Mapped[Any] = mapped_column(UTCDateTime, default=now)

class InstagramPost(Identity, Base):
    __tablename__ = 'instagram_posts'
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), index=True)
    content_id: Mapped[int | None] = mapped_column(ForeignKey('content_items.id'))
    media_type: Mapped[str] = mapped_column(String(30), default='CAROUSEL')
    title: Mapped[str | None] = mapped_column(String(200))
    caption: Mapped[str] = mapped_column(Text)
    carousel_data: Mapped[dict] = mapped_column(JSON, default=dict)
    media_urls: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(30), default='GENERATED', index=True)
    remote_id: Mapped[str | None] = mapped_column(String(120), unique=True)
    scheduled_at: Mapped[Any | None] = mapped_column(UTCDateTime, index=True)
    published_at: Mapped[Any | None] = mapped_column(UTCDateTime)
    error_message: Mapped[str | None] = mapped_column(Text)
    mock: Mapped[bool] = mapped_column(default=True)

class InstagramAnalytics(Identity, Base):
    __tablename__ = 'instagram_analytics'
    instagram_post_id: Mapped[int] = mapped_column(ForeignKey('instagram_posts.id'))
    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'))
    reach: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    profile_visits: Mapped[int] = mapped_column(Integer, default=0)
    followers_growth: Mapped[int] = mapped_column(Integer, default=0)
    recorded_at: Mapped[Any] = mapped_column(UTCDateTime, default=now)

class AIUsageLog(Identity, Base):
    __tablename__ = 'ai_usage_logs'
    account_id: Mapped[int | None] = mapped_column(ForeignKey('accounts.id'))
    model: Mapped[str] = mapped_column(String(80))
    provider: Mapped[str] = mapped_column(String(40))
    task_type: Mapped[str] = mapped_column(String(40))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default='SUCCESS')
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
