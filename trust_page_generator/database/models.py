from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BlogIdentity(Base):
    """Core table: blog_identity per PRD specification."""
    __tablename__ = "blog_identity"

    blog_id = Column(Integer, primary_key=True)               # Matching Site ID (1~8)
    brand_name = Column(String(100), nullable=False)          # 트래블픽24, 트렌드스팟24, etc.
    domain = Column(String(255), nullable=False)              # https://travelpick24.com
    category = Column(String(100), nullable=False)            # 종합 여행 가이드, etc.
    mission = Column(Text, nullable=False)                    # Brand Mission
    target_user = Column(String(255), nullable=False)         # Target Audience
    tone = Column(String(100), nullable=False)                # Writing Tone
    content_policy = Column(Text, nullable=False)             # Content Philosophy & Criteria
    trust_message = Column(Text, nullable=False)              # Trust Message
    email = Column(String(120), nullable=False)               # Official Contact Email
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    pages = relationship("TrustPage", back_populates="identity", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blog_id": self.blog_id,
            "brand_name": self.brand_name,
            "domain": self.domain,
            "category": self.category,
            "mission": self.mission,
            "target_user": self.target_user,
            "tone": self.tone,
            "content_policy": self.content_policy,
            "trust_message": self.trust_message,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TrustPage(Base):
    """Core table: trust_pages per PRD specification."""
    __tablename__ = "trust_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    blog_id = Column(Integer, ForeignKey("blog_identity.blog_id"), nullable=False, index=True)
    page_type = Column(String(50), nullable=False, index=True)  # about-us, editorial-policy, privacy-policy, terms, etc.
    title = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)                     # Full rendered HTML
    status = Column(String(50), default="READY")               # DRAFT, READY, PUBLISHED, FAILED
    wp_page_id = Column(Integer, nullable=True)                # WordPress REST API Page ID
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    identity = relationship("BlogIdentity", back_populates="pages")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "blog_id": self.blog_id,
            "page_type": self.page_type,
            "title": self.title,
            "slug": self.slug,
            "status": self.status,
            "wp_page_id": self.wp_page_id,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "updated_date": self.updated_date.isoformat() if self.updated_date else None,
        }
