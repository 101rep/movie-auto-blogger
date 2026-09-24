import random
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select, delete
from fastapi import HTTPException
from .models import Account, AuditLog, Post, Job, PublicationReservation, SystemSetting
from .db import now
from .content import setting, require_pass

def get(db, model, id):
    obj = db.get(model, id)
    if obj is None: raise HTTPException(404, 'Not found')
    return obj

def audit(db, actor, action, target=None, service='application', error_code=None):
    db.add(AuditLog(actor=str(actor), action=action, target=str(target) if target is not None else None, service=service, error_code=error_code))

def active_guard(db, p):
    db.expire_all()
    if setting(db, 'kill_switch', False): raise HTTPException(409, 'EMERGENCY_STOP')
    a = get(db, Account, p.account_id)
    if a.status != 'ONLINE': raise HTTPException(409, 'ACCOUNT_' + a.status)
    return a

def enforce_limits(db, p, when):
    a = get(db, Account, p.account_id)
    tz = ZoneInfo(a.timezone)
    start = when.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    end = (when.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).astimezone(timezone.utc)
    candidates = list(db.scalars(select(Post).where(Post.id != p.id, Post.status.in_(['SCHEDULED','RETRY_WAIT','PUBLISHING','PUBLISHED','VERIFYING','SUCCESS']))))
    own = [q for q in candidates if q.account_id == a.id]
    day = [q for q in own if start <= (q.published_at or q.scheduled_at or q.created_at) < end]
    if len(day) >= a.daily_post_limit: raise HTTPException(409, 'DAILY_LIMIT')
    if p.goal == 'AFFILIATE':
        if sum(q.goal == 'AFFILIATE' for q in day) >= a.daily_affiliate_limit: raise HTTPException(409, 'AFFILIATE_DAILY_LIMIT')
        history = sorted(own, key=lambda q:q.created_at, reverse=True)[:19]
        if (sum(q.goal == 'AFFILIATE' for q in history)+1)/(len(history)+1) > a.affiliate_ratio: raise HTTPException(409, 'AFFILIATE_RATIO_LIMIT')
    if any(abs(((q.published_at or q.scheduled_at or q.created_at)-when).total_seconds()) < a.minimum_interval*60 for q in own): raise HTTPException(409, 'MINIMUM_INTERVAL')
    utc_start = when.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    if sum(utc_start <= (q.published_at or q.scheduled_at or q.created_at) < utc_start+timedelta(days=1) for q in candidates) >= setting(db, 'global_daily_limit', 15): raise HTTPException(409, 'GLOBAL_DAILY_LIMIT')

def schedule(db, p, data, actor):
    db.scalar(select(SystemSetting).where(SystemSetting.key == 'kill_switch').with_for_update())
    if p.status != 'READY' or not p.approved_at: raise HTTPException(409, 'Approved READY post required')
    active_guard(db, p)
    require_pass(db, p)
    when = data.scheduled_at or now()
    if data.window_start:
        start, end = max(data.window_start, now()), data.window_end
        if end < start: raise HTTPException(422, 'Window is in the past')
        when = start + timedelta(seconds=random.uniform(0, (end-start).total_seconds()))
    when += timedelta(seconds=random.randint(0, data.jitter_seconds))
    if data.window_end and when > data.window_end: when = data.window_end
    if when < now()-timedelta(seconds=5): raise HTTPException(422, 'Schedule is in the past')
    enforce_limits(db, p, when)
    reservation = db.get(PublicationReservation, p.fingerprint)
    if reservation and reservation.post_id != p.id: raise HTTPException(409, 'DUPLICATE_RESERVATION')
    if not reservation: db.add(PublicationReservation(fingerprint=p.fingerprint, post_id=p.id))
    job = db.scalar(select(Job).where(Job.post_id == p.id))
    if job is None: db.add(Job(post_id=p.id, due_at=when))
    else: job.state, job.due_at = 'WAITING', when
    p.status, p.scheduled_at = 'SCHEDULED', when
    audit(db, actor, 'POST_SCHEDULED', p.id)
    db.commit()
    return p

def cancel(db, p, actor):
    if p.status in ['PUBLISHING','PUBLISHED','VERIFYING','SUCCESS'] or p.remote_id: raise HTTPException(409, 'Already publishing/published')
    p.status = 'CANCELLED'
    job = db.scalar(select(Job).where(Job.post_id == p.id))
    if job: job.state = 'CANCELLED'
    db.execute(delete(PublicationReservation).where(PublicationReservation.post_id == p.id))
    audit(db, actor, 'POST_CANCELLED', p.id)
    db.commit()

def retry(db, p, actor):
    if p.status not in ['FAILED','RETRY_WAIT']: raise HTTPException(409, 'Not a failed post')
    if p.retry_count >= 3: raise HTTPException(409, 'RETRY_BUDGET_EXHAUSTED')
    active_guard(db, p)
    require_pass(db, p)
    job = db.scalar(select(Job).where(Job.post_id == p.id))
    if not job: raise HTTPException(409, 'No publishing job')
    job.state, job.due_at = 'WAITING', now()
    p.status, p.next_retry_at = 'RETRY_WAIT', now()
    audit(db, actor, 'POST_RETRIED', p.id)
    db.commit()

def kill(db, enabled, actor):
    get(db, SystemSetting, 'kill_switch').value = enabled
    audit(db, actor, 'EMERGENCY_STOP' if enabled else 'SYSTEM_RESUMED', service='security')
    db.commit()
