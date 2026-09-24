"""RQ transport: DB jobs remain authoritative. Use Linux RQ worker in Compose."""
import logging, signal, threading
from redis import Redis
from rq import Queue
from sqlalchemy import select
from apps.backend.tre.config import settings
from apps.backend.tre.db import SessionLocal, now
from apps.backend.tre.models import Job
from apps.backend.tre.content import setting

def execute(job_id=None):
    from .engine import run_once
    return run_once(job_id=job_id)

def main():
    stop=threading.Event()
    signal.signal(signal.SIGTERM, lambda *_:stop.set())
    signal.signal(signal.SIGINT, lambda *_:stop.set())
    redis=Redis.from_url(settings().redis_url, socket_timeout=5, socket_connect_timeout=5)
    queue=Queue('publishing', connection=redis, default_timeout=90)
    while not stop.is_set():
        try:
            # One bounded tick: the worker records its own heartbeat and claims a DB job.
            # Expiring queued ticks prevents an unbounded backlog during worker downtime.
            if redis.set('dispatch:tick', '1', nx=True, ex=5):
                queue.enqueue(execute, result_ttl=10, failure_ttl=300, ttl=10)
        except Exception as exc:
            logging.error('Dispatcher unavailable: %s', type(exc).__name__)
        stop.wait(5)

if __name__=='__main__': main()
