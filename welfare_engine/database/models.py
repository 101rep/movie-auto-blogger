"""SQLAlchemy models for Welfare Content Auto Publishing Engine V1.0.
Dedicated schema for welfare contents, multi-persona routing, and publication verification.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ContentStatus(str, Enum):
    """Lifecycle status of a welfare content item."""
    NEW = "NEW"
    ANALYZING = "ANALYZING"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    UPDATED = "UPDATED"
    HOLD = "HOLD"            # <= 50 points
    WAITING = "WAITING"      # 50 ~ 69 points


class PriorityLevel(str, Enum):
    """Priority outcome based on evaluation score."""
    IMMEDIATE = "IMMEDIATE"   # 90 ~ 100 points
    SCHEDULED = "SCHEDULED"   # 70 ~ 89 points
    WAITING = "WAITING"       # 50 ~ 69 points
    HOLD = "HOLD"             # <= 50 points


class WelfareContent(Base):
    """Core table: welfare_contents per specification."""
    __tablename__ = "welfare_contents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    source = Column(String(100), nullable=False)               # 정부24, 복지서비스, 공공데이터포털, 기업마당, 정책브리핑
    category = Column(String(100), nullable=True, index=True)  # 정부지원금, 청년지원, 소상공인 등
    target = Column(String(255), nullable=True)                # 전 국민, 20~40대, 사업자 등
    age = Column(String(50), nullable=True)                    # 연령 요건
    region = Column(String(50), nullable=True, default="전국")  # 전국, 서울, 경기 등
    income_condition = Column(Text, nullable=True)             # 소득 조건
    amount = Column(String(100), nullable=True)                # 지원 규모/금액
    deadline = Column(String(100), nullable=True)              # 마감일 (YYYY-MM-DD or 상시)
    apply_method = Column(Text, nullable=True)                 # 신청 방법
    documents = Column(Text, nullable=True)                    # 필요 서류
    url = Column(String(500), nullable=False)                  # 공식 상세 URL

    priority_score = Column(Integer, default=0)                # 100점 만점 평가 점수
    priority_level = Column(String(50), default="WAITING")     # IMMEDIATE, SCHEDULED, WAITING, HOLD
    score_breakdown = Column(Text, nullable=True)              # JSON string of criteria scores

    persona_type = Column(String(50), default="ALL")           # BLOG_A, BLOG_B, BLOG_C, MULTI, ALL
    duplicate_hash = Column(String(64), unique=True, index=True, nullable=False)

    status = Column(String(50), default=ContentStatus.NEW.value, index=True)
    published_blog = Column(String(100), default="", nullable=True)  # Comma-separated: "BLOG_A,BLOG_B"
    raw_data = Column(Text, nullable=True)                     # Full JSON data collected

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    publications = relationship("WelfarePublication", back_populates="content", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "category": self.category,
            "target": self.target,
            "age": self.age,
            "region": self.region,
            "income_condition": self.income_condition,
            "amount": self.amount,
            "deadline": self.deadline,
            "apply_method": self.apply_method,
            "documents": self.documents,
            "url": self.url,
            "priority_score": self.priority_score,
            "priority_level": self.priority_level,
            "persona_type": self.persona_type,
            "duplicate_hash": self.duplicate_hash,
            "status": self.status,
            "published_blog": self.published_blog,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WelfarePublication(Base):
    """Detailed log and verification record for each published blog post."""
    __tablename__ = "welfare_publications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("welfare_contents.id"), nullable=False, index=True)
    blog_key = Column(String(20), nullable=False, index=True)   # BLOG_A, BLOG_B, BLOG_C
    site_id = Column(Integer, nullable=False)                   # 7, 5, 6
    persona_title = Column(String(255), nullable=False)         # Title generated specifically for this persona
    
    wp_post_id = Column(Integer, nullable=True)
    wp_url = Column(String(500), nullable=True)
    wp_status = Column(String(50), default="future")            # future, publish, failed
    featured_media_id = Column(Integer, nullable=True)

    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    verification_status = Column(String(50), default="PENDING") # VERIFIED, FAILED, PENDING
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    content = relationship("WelfareContent", back_populates="publications")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "blog_key": self.blog_key,
            "site_id": self.site_id,
            "persona_title": self.persona_title,
            "wp_post_id": self.wp_post_id,
            "wp_url": self.wp_url,
            "wp_status": self.wp_status,
            "featured_media_id": self.featured_media_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "verification_status": self.verification_status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
