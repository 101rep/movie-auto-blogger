import logging, secrets
from datetime import timedelta
from sqlalchemy import select, update, or_
from fastapi import HTTPException
from apps.backend.tre.db import SessionLocal, now
from apps.backend.tre.models import Job, Post, PostReply, Account, JobAttempt, Notification, WorkerHeartbeat, WorkerLease, AccountProductHistory
from apps.backend.tre.config import settings
from apps.backend.tre.content import setting, require_pass
from apps.backend.tre.operations import active_guard, enforce_limits, audit
from services.contracts import ProviderError, LiveThreadsProvider, LiveTelegramProvider
from services.mock import MockThreadsProvider, MockTelegramProvider

log = logging.getLogger('worker')
RETRY_DELAYS = [60, 300, 1800]

def heartbeat(db):
    row = db.get(WorkerHeartbeat, 'publisher')
    if row: row.seen_at = now()
    else: db.add(WorkerHeartbeat(name='publisher', seen_at=now()))
    db.commit()

def notify(db, post, success):
    key = f'post:{post.id}:' + ('success' if success else f'failure:{post.retry_count}')
    if db.scalar(select(Notification).where(Notification.event_key == key)): return
    account = db.get(Account, post.account_id)
    product = db.get(Product, post.product_id) if getattr(post, 'product_id', None) else None
    product_name = product.name if product else "없음"
    mode_tag = "[MOCK]" if settings().telegram_mock else "[REAL]"
    if success:
        text = f"{mode_tag} 게시 성공\n계정: {account.name}\n시간: {post.published_at or now()}\nPost ID: {post.remote_id or '없음'}\n상품: {product_name}"
    else:
        action_needed = "계정 토큰 재인증 필요" if post.error_code in ['TOKEN_EXPIRED', 'AUTH_ERROR'] else "자동 재시도 대기"
        text = f"{mode_tag} 게시 실패\n계정: {account.name}\n원인: {post.error_code or 'UNKNOWN'}\n필요 조치: {action_needed}\n재시도: {post.next_retry_at or '없음'}"
    db.add(Notification(post_id=post.id, event_key=key, body=text, mock=settings().telegram_mock))
    db.commit()

def deliver_notifications(factory=SessionLocal):
    provider = MockTelegramProvider() if settings().telegram_mock else LiveTelegramProvider()
    with factory() as db:
        for n in db.scalars(select(Notification).where(Notification.state == 'PENDING').limit(50)):
            try:
                n.remote_id = provider.send(n.body, n.event_key)
                n.state = 'SENT'
            except ProviderError as exc:
                n.state, n.error_code = 'FAILED', exc.code
                audit(db, 'worker', 'NOTIFICATION_FAILED', n.id, 'telegram', exc.code)
            db.commit()

def checkpoint_guard(db, p, owner):
    # End any stale read transaction before observing a stop/pause from another process.
    db.commit()
    active_guard(db, p)
    if p.status not in ['SCHEDULED', 'RETRY_WAIT', 'PUBLISHING', 'PUBLISHED', 'VERIFYING'] or not p.approved_at:
        raise ProviderError('POST_NOT_AUTHORIZED')
    lease = db.get(WorkerLease, 'publisher')
    if not lease or lease.owner != owner or lease.until <= now(): raise ProviderError('LEASE_LOST', True)
    lease.until = now()+timedelta(seconds=120)
    db.commit()

def publish(db, p, provider, owner):
    checkpoint_guard(db, p, owner)
    require_pass(db, p)
    if not p.remote_id:
        enforce_limits(db, p, now())
        p.status = 'PUBLISHING'
        db.commit()
        checkpoint_guard(db, p, owner)
        remote = provider.publish_text(p.body, f'post:{p.id}')
        if not remote: raise ProviderError('MISSING_REMOTE_ID', True)
        p.remote_id, p.status, p.published_at = remote, 'PUBLISHED', now()
        db.commit()
    parent = p.remote_id
    for reply in db.scalars(select(PostReply).where(PostReply.post_id == p.id).order_by(PostReply.position)):
        checkpoint_guard(db, p, owner)
        if not reply.remote_id:
            reply.remote_id = provider.publish_reply(parent, reply.body, f'post:{p.id}:reply:{reply.position}')
            if not reply.remote_id: raise ProviderError('MISSING_REPLY_ID', True)
            db.commit()
        result = provider.get_post(reply.remote_id)
        if result.get('id') != reply.remote_id or result.get('parent_id') != parent: raise ProviderError('REPLY_VERIFICATION_FAILED', True)
        parent = reply.remote_id
    p.status = 'VERIFYING'
    db.commit()
    result = provider.get_post(p.remote_id)
    if result.get('id') != p.remote_id or result.get('text') != p.body: raise ProviderError('VERIFICATION_FAILED', True)
    p.status, p.error_code, p.error_message, p.next_retry_at = 'SUCCESS', None, None, None
    db.get(Account, p.account_id).last_success_at = now()
    if p.product_id and not db.scalar(select(AccountProductHistory).where(AccountProductHistory.post_id == p.id)):
        db.add(AccountProductHistory(account_id=p.account_id, product_id=p.product_id, post_id=p.id, published_at=p.published_at, angle=p.angle, hook_type=p.hook_type))
    db.commit()

def fail(db, job, p, code, retryable):
    p.retry_count += 1
    p.error_code, p.error_message = code, code  # Deliberately never persist raw provider exception/token text.
    account = db.get(Account, p.account_id)
    account.last_error_at = now()
    if code in ['TOKEN_EXPIRED','AUTH_ERROR','PERMISSION_ERROR']:
        account.status, retryable = 'AUTH_REQUIRED', False
    if retryable and p.retry_count <= len(RETRY_DELAYS):
        p.next_retry_at = now()+timedelta(seconds=RETRY_DELAYS[p.retry_count-1])
        p.status, job.state, job.due_at = 'RETRY_WAIT', 'WAITING', p.next_retry_at
    else:
        p.status, job.state, p.next_retry_at = 'FAILED', 'FAILED', None
    db.add(JobAttempt(job_id=job.id, number=job.attempts, result=p.status, error_code=code))
    audit(db, 'worker', 'PUBLISH_FAILED', p.id, 'threads', code)
    db.commit()
    notify(db, p, False)

def run_once(factory=SessionLocal, provider=None, job_id=None):
    owner = secrets.token_hex(16)
    provider = provider or (MockThreadsProvider(factory) if settings().threads_mock else LiveThreadsProvider())
    with factory() as db:
        heartbeat(db)
        if setting(db, 'kill_switch', False): return 0
        acquired = db.execute(update(WorkerLease).where(WorkerLease.name == 'publisher', WorkerLease.until < now()).values(owner=owner, until=now()+timedelta(seconds=120))).rowcount
        db.commit()
        if not acquired: return 0
        try:
            query = select(Job).join(Post, Job.post_id == Post.id).join(Account, Post.account_id == Account.id).where(Account.status == 'ONLINE', Job.due_at <= now(), or_(Job.state == 'WAITING', (Job.state == 'PROCESSING') & (Job.lease_until < now()))).order_by(Job.due_at)
            if job_id is not None: query = query.where(Job.id == job_id)
            job = db.scalar(query.limit(1))
            if not job: return 0
            job.state, job.claim_token, job.lease_until = 'PROCESSING', owner, now()+timedelta(seconds=120)
            job.attempts += 1
            db.commit()
            p = db.get(Post, job.post_id)
            if p.status == 'SUCCESS':
                job.state = 'DONE'
                db.commit()
                notify(db, p, True)
                return 0
            try:
                publish(db, p, provider, owner)
                job.state = 'DONE'
                db.add(JobAttempt(job_id=job.id, number=job.attempts, result='SUCCESS'))
                audit(db, 'worker', 'POST_SUCCESS', p.id, 'threads')
                db.commit()
                notify(db, p, True)
            except HTTPException as exc:
                if exc.detail == 'EMERGENCY_STOP' or str(exc.detail).startswith('ACCOUNT_'):
                    job.state, job.due_at = 'WAITING', now()+timedelta(seconds=10)
                    p.status = 'PUBLISHED' if p.remote_id else 'SCHEDULED'
                    db.commit()
                else: fail(db, job, p, 'VALIDATION_OR_LIMIT_BLOCKED', False)
            except ProviderError as exc: fail(db, job, p, exc.code, exc.retryable)
            except Exception:
                db.rollback()
                log.error('Unexpected worker exception; job=%s; raw exception suppressed', job.id)
                fail(db, job, p, 'INTERNAL_ERROR', False)
            return 1
        finally:
            db.execute(update(WorkerLease).where(WorkerLease.name == 'publisher', WorkerLease.owner == owner).values(until=now(), owner=None))
            db.commit()
            deliver_notifications(factory)
