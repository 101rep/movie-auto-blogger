# -*- coding: utf-8 -*-
"""AAOS (AI Automation Operating System) Unified Database Models."""
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import (
    String, Text, Integer, Boolean, Float, JSON, ForeignKey, DateTime, create_engine
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AAOSBase(DeclarativeBase):
    pass


class AAOSJob(AAOSBase):
    """Core Job Management Table tracking all platform publishing tasks."""
    __tablename__ = "aaos_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(50), index=True)  # threads, instagram, wordpress, etc.
    account: Mapped[str] = mapped_column(String(100), index=True)
    content_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", index=True)  # PENDING, RUNNING, SUCCESS, FAILED, VERIFYING, VERIFIED
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    execution_logs: Mapped[list["AAOSExecutionLog"]] = relationship("AAOSExecutionLog", back_populates="job", cascade="all, delete-orphan")
    verification_logs: Mapped[list["AAOSVerificationLog"]] = relationship("AAOSVerificationLog", back_populates="job", cascade="all, delete-orphan")


class AAOSExecutionLog(AAOSBase):
    """Detailed Execution & API attempt logging for jobs."""
    __tablename__ = "aaos_execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("aaos_jobs.id"), index=True)
    api_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    job: Mapped["AAOSJob"] = relationship("AAOSJob", back_populates="execution_logs")


class AAOSVerificationLog(AAOSBase):
    """Playwright / Browser-level actual service appearance verification logs."""
    __tablename__ = "aaos_verification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("aaos_jobs.id"), nullable=True, index=True)
    platform: Mapped[str] = mapped_column(String(50), index=True)
    post_url: Mapped[str] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    screenshot_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    job: Mapped[Optional["AAOSJob"]] = relationship("AAOSJob", back_populates="verification_logs")


class PublishQueue(AAOSBase):
    """Publishing Queue Table per PRD v2.0 Part 1.2."""
    __tablename__ = "publish_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blog_id: Mapped[int] = mapped_column(Integer, index=True)
    post_id: Mapped[int] = mapped_column(Integer, index=True)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)  # pending, processing, success, failed, retry, cancelled
    worker_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lock_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class DailyPublishLimit(AAOSBase):
    """Daily Publish Limit Engine Table per PRD v2.0 Part 1.4."""
    __tablename__ = "daily_publish_limit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blog_id: Mapped[int] = mapped_column(Integer, index=True)
    date: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD (KST)
    limit_count: Mapped[int] = mapped_column(Integer, default=4)
    published_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class WorkerLock(AAOSBase):
    """Distributed Worker Lock Table per PRD v2.0 Part 1.3."""
    __tablename__ = "worker_locks"

    resource_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    worker_id: Mapped[str] = mapped_column(String(100), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AIMemoryRecord(AAOSBase):
    """AI Memory System Table per PRD v2.0 Part 7."""
    __tablename__ = "ai_memory_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    changed_files: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    test_results: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

