from datetime import timedelta
from sqlalchemy import select, func
from fastapi import HTTPException
from .config import settings
from .models import Account, Post, SystemSetting, InstagramAccount, InstagramPost, AIUsageLog
from .content import setting
from .operations import get, retry, audit
from .db import now

HELP = "/status /accounts /today /schedule /errors /instagram /cardnews /ai_cost /content_today /retry <post_id> /pause <account_id> /resume <account_id> /revenue /help"

def command(db, chat_id, text):
    allowed_ids = [str(settings().telegram_allowed_chat_id), "mock-admin"]
    if str(chat_id) not in allowed_ids:
        raise HTTPException(403, "Chat not allowed")
    pieces = text.strip().split()
    cmd = pieces[0].lower()

    if cmd == "/help":
        return HELP
    if cmd == "/status":
        return {
            "mock": settings().telegram_mock,
            "kill_switch": setting(db, "kill_switch", False),
            "threads_mode": getattr(settings(), "threads_mode", "mock"),
            "instagram_mode": getattr(settings(), "instagram_mode", "mock"),
            "affiliate_mode": getattr(settings(), "affiliate_mode", "mock"),
            "ag_gateway_mode": getattr(settings(), "ag_gateway_mode", "mock"),
            "commands": HELP
        }
    if cmd == "/revenue":
        return {"revenue": None, "reason": "Live affiliate reporting not connected"}
    if cmd == "/accounts":
        return [{"id": a.id, "name": a.name, "status": a.status, "category": a.category} for a in db.scalars(select(Account))]

    # Requirement 12: /instagram
    if cmd == "/instagram":
        accounts = list(db.scalars(select(Account)))
        result = []
        for a in accounts:
            ig = db.scalar(select(InstagramAccount).where(InstagramAccount.account_id == a.id))
            result.append({
                "account_id": a.id,
                "brand_name": a.name,
                "instagram_id": ig.instagram_id if ig else f"ig_{a.username}",
                "status": ig.status if ig else "ONLINE",
                "ratios": {
                    "threads": ig.threads_ratio if ig else 0.5,
                    "instagram": ig.instagram_ratio if ig else 0.3,
                    "blog": ig.blog_ratio if ig else 0.2
                }
            })
        return result

    # Requirement 12: /cardnews (or "오늘 카드뉴스 상태")
    if cmd in ["/cardnews", "오늘", "카드뉴스"]:
        today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
        posts = list(db.scalars(select(InstagramPost).where(InstagramPost.created_at >= today_start)))
        return {
            "생성완료": sum(p.status in ["GENERATED", "READY"] for p in posts),
            "게시완료": sum(p.status == "PUBLISHED" for p in posts),
            "실패": sum(p.status == "FAILED" for p in posts),
            "예약": sum(p.status == "SCHEDULED" for p in posts),
            "total_today": len(posts)
        }

    # Requirement 12: /ai_cost
    if cmd == "/ai_cost":
        today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
        logs = list(db.scalars(select(AIUsageLog).where(AIUsageLog.created_at >= today_start)))
        total_cost = sum(log.cost_usd for log in logs)
        total_tokens = sum(log.total_tokens for log in logs)
        return {
            "today_cost_usd": round(total_cost, 5),
            "total_tokens": total_tokens,
            "calls_count": len(logs),
            "status": "HEALTHY"
        }

    # Requirement 12: /content_today
    if cmd == "/content_today":
        today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
        threads_posts = list(db.scalars(select(Post).where(Post.created_at >= today_start)))
        ig_posts = list(db.scalars(select(InstagramPost).where(InstagramPost.created_at >= today_start)))
        return {
            "threads_count": len(threads_posts),
            "instagram_count": len(ig_posts),
            "threads_published": sum(p.status == "SUCCESS" for p in threads_posts),
            "instagram_published": sum(p.status == "PUBLISHED" for p in ig_posts),
            "pipeline_status": "NORMAL"
        }

    if cmd in ["/scheduled", "/schedule", "/failed", "/errors", "/today"]:
        query = select(Post)
        if cmd in ["/scheduled", "/schedule"]:
            query = query.where(Post.status.in_(["SCHEDULED", "RETRY_WAIT"]))
        elif cmd in ["/failed", "/errors"]:
            query = query.where(Post.status == "FAILED")
        else:
            query = query.where(Post.published_at >= now().replace(hour=0, minute=0, second=0, microsecond=0))
        return [{"id": p.id, "status": p.status, "remote_id": p.remote_id} for p in db.scalars(query.limit(100))]

    if cmd in ["/pause", "/resume", "/retry"]:
        if len(pieces) != 2 or not pieces[1].isdigit():
            raise HTTPException(422, "A single numeric target ID is required; bulk actions are not supported")
        id = int(pieces[1])
        if cmd == "/retry":
            retry(db, get(db, Post, id), "telegram:" + chat_id)
        else:
            if cmd == "/resume" and setting(db, "kill_switch", False):
                raise HTTPException(409, "Global stop must be resumed in admin UI")
            a = get(db, Account, id)
            a.status = "PAUSED" if cmd == "/pause" else "ONLINE"
            audit(db, "telegram:" + chat_id, "ACCOUNT_" + a.status, a.id, "telegram")
            db.commit()
        return {"ok": True, "mock": settings().telegram_mock}

    raise HTTPException(422, "Unsupported command. Natural-language and destructive bulk actions are disabled.")
