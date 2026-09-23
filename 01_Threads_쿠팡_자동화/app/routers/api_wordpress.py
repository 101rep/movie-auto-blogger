# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.connection import get_db
from database.models import Content
from services.wordpress_service import WordPressService
from config import settings

router = APIRouter(prefix="/api/wordpress", tags=["WordPress"])

@router.get("/status")
def get_wordpress_status():
    """Check WordPress connectivity and configuration"""
    wp = WordPressService()
    res = wp.test_connection()
    return {
        "enabled": getattr(settings, "WORDPRESS_ENABLED", True),
        "auto_bridge": getattr(settings, "WORDPRESS_AUTO_BRIDGE", True),
        "site_url": getattr(settings, "WORDPRESS_URL", "https://trendspot24.com"),
        "username": getattr(settings, "WORDPRESS_USERNAME", ""),
        "connection": res
    }

@router.post("/test")
def test_wordpress_connection():
    """Trigger real-time connection test"""
    wp = WordPressService()
    return wp.test_connection()

@router.post("/bridge/{content_id}")
def bridge_content_to_wordpress(content_id: int, db: Session = Depends(get_db)):
    """Bridge specific Threads content to WordPress as an E-E-A-T article"""
    wp = WordPressService()
    res = wp.bridge_content(db, content_id)
    if res.get("status") != "SUCCESS":
        raise HTTPException(status_code=400, detail=res.get("message", "Bridge failed"))
    return res

@router.get("/posts")
def list_bridged_posts(limit: int = 20, db: Session = Depends(get_db)):
    """List contents that have been bridged to WordPress"""
    posts = db.query(Content).filter(
        Content.wordpress_url.isnot(None)
    ).order_by(desc(Content.updated_at)).limit(limit).all()

    return {
        "total_count": len(posts),
        "posts": [
            {
                "id": p.id,
                "title": p.title,
                "product_name": p.product.name if p.product else "",
                "account_username": p.account.username if p.account else "",
                "wordpress_post_id": p.wordpress_post_id,
                "wordpress_url": p.wordpress_url,
                "wordpress_status": p.wordpress_status,
                "status": p.status
            }
            for p in posts
        ]
    }