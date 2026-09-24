# -*- coding: utf-8 -*-
"""
Worker Lock System — Production Reliability PRD v2.0 PART 1.3

Prevents simultaneous workers from double-publishing identical articles or overloading endpoints:
- Job Request -> Acquire Lock -> Execute -> Save Result -> Release Lock
- Auto-expires stale locks after TTL seconds (deadlock prevention)
- Atomic check-and-set semantics via SQLite transactions
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from contextlib import contextmanager

from core.aaos.db import get_aaos_db_session
from core.aaos.models import WorkerLock

logger = logging.getLogger("worker_lock")


class WorkerLockManager:
    """Manages distributed worker locks for critical publishing operations."""

    @classmethod
    def acquire(
        cls,
        resource_key: str,
        worker_id: Optional[str] = None,
        ttl_seconds: int = 300
    ) -> Optional[str]:
        """
        Attempts to acquire a lock on `resource_key`.
        Returns `lock_token` if acquired, or `None` if already locked.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=ttl_seconds)
        assigned_worker_id = worker_id or f"worker_{uuid.uuid4().hex[:8]}"

        with get_aaos_db_session() as session:
            # Check existing lock
            existing_lock = session.query(WorkerLock).filter(
                WorkerLock.resource_key == resource_key
            ).first()

            if existing_lock:
                lock_exp = existing_lock.expires_at
                if lock_exp.tzinfo is None:
                    lock_exp = lock_exp.replace(tzinfo=timezone.utc)

                # Re-entrant by same worker or expired -> update expiry and succeed
                if existing_lock.worker_id == assigned_worker_id or lock_exp <= now:
                    existing_lock.worker_id = assigned_worker_id
                    existing_lock.acquired_at = now
                    existing_lock.expires_at = expires_at
                    session.commit()
                    return assigned_worker_id

                # Locked by another worker and still valid
                logger.warning("Resource '%s' already locked by %s until %s", resource_key, existing_lock.worker_id, existing_lock.expires_at.isoformat())
                return None

            # Create new lock
            new_lock = WorkerLock(
                resource_key=resource_key,
                worker_id=assigned_worker_id,
                acquired_at=now,
                expires_at=expires_at
            )
            session.add(new_lock)
            session.commit()
            logger.info("Lock acquired on '%s' by %s (TTL: %ds)", resource_key, assigned_worker_id, ttl_seconds)
            return assigned_worker_id

    @classmethod
    def release(cls, resource_key: str, worker_id: str) -> bool:
        """Releases the lock on `resource_key` if held by `worker_id`."""
        with get_aaos_db_session() as session:
            lock = session.query(WorkerLock).filter(
                WorkerLock.resource_key == resource_key,
                WorkerLock.worker_id == worker_id
            ).first()

            if lock:
                session.delete(lock)
                session.commit()
                logger.info("Lock on '%s' released by %s", resource_key, worker_id)
                return True
            else:
                logger.debug("No active lock matching '%s' and worker '%s'", resource_key, worker_id)
                return False

    @classmethod
    @contextmanager
    def lock(cls, resource_key: str, worker_id: Optional[str] = None, ttl_seconds: int = 300):
        """Context manager for safe lock acquire & automatic release."""
        assigned_id = cls.acquire(resource_key, worker_id, ttl_seconds)
        if not assigned_id:
            raise RuntimeError(f"Could not acquire lock on resource '{resource_key}'.")
        try:
            yield assigned_id
        finally:
            cls.release(resource_key, assigned_id)
