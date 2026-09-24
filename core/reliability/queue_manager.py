# -*- coding: utf-8 -*-
"""
Publishing Queue Manager — Production Reliability PRD v2.0 PART 1.2

Manages lifecycle of tasks in the PublishQueue table:
- State Machine: pending -> processing -> success / failed / retry / cancelled
- Multi-Worker coordination with safe status transitions
- Retry counter and error tracking
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from zoneinfo import ZoneInfo

from core.aaos.db import get_aaos_db_session
from core.aaos.models import PublishQueue

logger = logging.getLogger("queue_manager")


class PublishQueueManager:
    """Enterprise Queue Manager for WordPress & Social Publishing Tasks."""

    @staticmethod
    def enqueue(
        blog_id: int,
        post_id: int,
        scheduled_time: datetime,
        worker_id: Optional[str] = None
    ) -> PublishQueue:
        """Enqueues a new publishing task with 'pending' status."""
        with get_aaos_db_session() as session:
            # Check for existing duplicate queue item
            existing = session.query(PublishQueue).filter(
                PublishQueue.blog_id == blog_id,
                PublishQueue.post_id == post_id,
                PublishQueue.status.in_(["pending", "processing", "success"])
            ).first()

            if existing:
                logger.info("Task already queued for blog %d, post %d (status: %s)", blog_id, post_id, existing.status)
                return existing

            queue_item = PublishQueue(
                blog_id=blog_id,
                post_id=post_id,
                scheduled_time=scheduled_time,
                status="pending",
                worker_id=worker_id,
                retry_count=0
            )
            session.add(queue_item)
            session.commit()
            session.refresh(queue_item)
            session.expunge(queue_item)
            logger.info("Enqueued task #%d for Blog %d (Scheduled: %s)", queue_item.id, blog_id, scheduled_time.isoformat())
            return queue_item

    @staticmethod
    def get_pending_tasks(blog_id: Optional[int] = None, limit: int = 10) -> List[PublishQueue]:
        """Retrieves pending tasks ready for execution."""
        with get_aaos_db_session() as session:
            query = session.query(PublishQueue).filter(
                PublishQueue.status.in_(["pending", "retry"])
            )
            if blog_id is not None:
                query = query.filter(PublishQueue.blog_id == blog_id)

            query = query.order_by(PublishQueue.scheduled_time.asc()).limit(limit)
            items = query.all()
            for item in items:
                session.expunge(item)
            return items

    @staticmethod
    def mark_processing(queue_id: int, worker_id: str, lock_token: Optional[str] = None) -> bool:
        """Transitions queue item from 'pending'/'retry' to 'processing'."""
        with get_aaos_db_session() as session:
            item = session.query(PublishQueue).filter(PublishQueue.id == queue_id).first()
            if not item or item.status not in ("pending", "retry"):
                return False

            item.status = "processing"
            item.worker_id = worker_id
            item.lock_token = lock_token
            item.locked_at = datetime.now(timezone.utc)
            session.commit()
            return True

    @staticmethod
    def mark_success(queue_id: int) -> bool:
        """Transitions queue item to 'success' upon verified publishing."""
        with get_aaos_db_session() as session:
            item = session.query(PublishQueue).filter(PublishQueue.id == queue_id).first()
            if not item:
                return False

            item.status = "success"
            item.published_at = datetime.now(timezone.utc)
            item.lock_token = None
            item.locked_at = None
            item.error_message = None
            session.commit()
            logger.info("Queue item #%d marked as SUCCESS", queue_id)
            return True

    @staticmethod
    def mark_failed(queue_id: int, error_message: str, max_retries: int = 3) -> bool:
        """Marks queue item as failed or transitions to 'retry' if retries remain."""
        with get_aaos_db_session() as session:
            item = session.query(PublishQueue).filter(PublishQueue.id == queue_id).first()
            if not item:
                return False

            item.retry_count += 1
            item.error_message = error_message
            item.lock_token = None
            item.locked_at = None

            if item.retry_count < max_retries:
                item.status = "retry"
                logger.warning("Queue item #%d marked for RETRY (%d/%d): %s", queue_id, item.retry_count, max_retries, error_message)
            else:
                item.status = "failed"
                logger.error("Queue item #%d permanently FAILED after %d retries: %s", queue_id, max_retries, error_message)

            session.commit()
            return True

    @staticmethod
    def cancel_task(queue_id: int, reason: str = "User cancelled") -> bool:
        """Cancels a pending or retry task."""
        with get_aaos_db_session() as session:
            item = session.query(PublishQueue).filter(PublishQueue.id == queue_id).first()
            if not item:
                return False

            item.status = "cancelled"
            item.error_message = reason
            item.lock_token = None
            item.locked_at = None
            session.commit()
            logger.info("Queue item #%d CANCELLED: %s", queue_id, reason)
            return True

    @staticmethod
    def get_queue_summary() -> Dict[str, Any]:
        """Provides status distribution of the queue."""
        with get_aaos_db_session() as session:
            all_items = session.query(PublishQueue).all()
            counts = {
                "pending": 0,
                "processing": 0,
                "success": 0,
                "failed": 0,
                "retry": 0,
                "cancelled": 0,
                "total": len(all_items)
            }
            for it in all_items:
                if it.status in counts:
                    counts[it.status] += 1

            return counts
