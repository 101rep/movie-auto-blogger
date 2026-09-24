from datetime import timedelta
from sqlalchemy import select, func, text
from .models import Account, Post, Job, AuditLog, WorkerHeartbeat, Notification, InstagramPost
from .content import setting
from .config import settings
from .db import now

def snapshot(db):
    posts=list(db.scalars(select(Post).order_by(Post.created_at.desc()).limit(500)))
    today=now().replace(hour=0,minute=0,second=0,microsecond=0)
    published=[p for p in posts if p.published_at and p.published_at>=today]
    beat=db.get(WorkerHeartbeat,"publisher")
    heartbeat={"status":"ONLINE" if beat and beat.seen_at>now()-timedelta(seconds=30) else "OFFLINE","last_seen":beat.seen_at if beat else None}
    queue={state:db.scalar(select(func.count()).select_from(Job).where(Job.state==state)) for state in ["WAITING","PROCESSING","DONE","FAILED"]}
    return {"mock":settings().threads_mock,"kill_switch":setting(db,"kill_switch",False),"today_timezone":"UTC","today_posts":len(published),"success":sum(p.status=="SUCCESS" for p in published),"failed":sum(p.status=="FAILED" for p in posts),"scheduled":sum(p.status in ["SCHEDULED","RETRY_WAIT"] for p in posts),"affiliate":sum(p.goal=="AFFILIATE" for p in published),"information":sum(p.goal=="INFORMATION" for p in published),"worker":heartbeat,"queue":queue,"accounts":db.scalar(select(func.count()).select_from(Account)),"instagram":{"mode":"MOCK" if settings().is_instagram_mock else "ONLINE","posts":db.scalar(select(func.count()).select_from(InstagramPost))},"telegram":{"mode":"MOCK" if settings().telegram_mock else "NOT_IMPLEMENTED","sent":db.scalar(select(func.count()).select_from(Notification).where(Notification.state=="SENT")),"failed":db.scalar(select(func.count()).select_from(Notification).where(Notification.state=="FAILED"))}}

def health(db,name):
    cfg=settings()
    if name=="db":
        db.execute(text("SELECT 1"));return {"service":name,"status":"ONLINE"}
    if name=="worker": return snapshot(db)["worker"]
    if name=="redis":
        if cfg.queue_mode=="db": return {"status":"NOT_REQUIRED","transport":"database"}
        from redis import Redis
        try:
            Redis.from_url(cfg.redis_url,socket_timeout=2,socket_connect_timeout=2).ping()
            return {"status":"ONLINE"}
        except Exception: return {"status":"OFFLINE","error_code":"REDIS_UNAVAILABLE"}
    if name in ["threads","instagram","telegram","ai"]:
        return {"service":name,"status":"MOCK" if getattr(cfg,name+"_mock") else "NOT_IMPLEMENTED","live_verified":False}
    return {"status":"UNKNOWN"}
