# -*- coding: utf-8 -*-
"""
Blog Daily Limit Engine — Production Reliability PRD v2.0 PART 1.4

Enforces strict daily publishing caps across blogs (specifically EnterPick24):
- Logic: Check today's published count -> If >= 4, halt publishing; If < 4, allow schedule/publish.
- Table: daily_publish_limit (blog_id, date, limit_count, published_count)
- Prevents runaway publishing and search engine spam penalties.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from zoneinfo import ZoneInfo

from core.aaos.db import get_aaos_db_session
from core.aaos.models import DailyPublishLimit

logger = logging.getLogger("daily_limit_engine")

DEFAULT_DAILY_LIMITS = {
    1: 4,  # 트래블픽24
    2: 4,  # 트렌드스팟24
    3: 0,  # 아이템픽24 (자동 스케줄 제외 / 수동 전용)
    4: 3,  # 엔터픽24 (엄격 3개 제한: 09:00, 14:00, 20:00)
    5: 4,  # 복지픽23
    6: 4,  # 복지픽24
    7: 4,  # 복지픽25
    8: 4,  # 뉴스픽24
}


class DailyLimitEngine:
    """Controls and tracks daily publication quotas per blog."""

    @staticmethod
    def _get_kst_today() -> str:
        kst = ZoneInfo("Asia/Seoul")
        return datetime.now(kst).strftime("%Y-%m-%d")

    @classmethod
    def can_publish(
        cls,
        blog_id: int,
        date_str: Optional[str] = None
    ) -> Tuple[bool, int, int, str]:
        """
        Checks whether blog_id can publish another post on date_str.
        Returns: (can_publish: bool, current_published: int, limit: int, message: str)
        """
        target_date = date_str or cls._get_kst_today()
        default_limit = DEFAULT_DAILY_LIMITS.get(blog_id, 4)

        with get_aaos_db_session() as session:
            record = session.query(DailyPublishLimit).filter(
                DailyPublishLimit.blog_id == blog_id,
                DailyPublishLimit.date == target_date
            ).first()

            if not record:
                # Initialize record for today
                record = DailyPublishLimit(
                    blog_id=blog_id,
                    date=target_date,
                    limit_count=default_limit,
                    published_count=0
                )
                session.add(record)
                session.commit()
                session.refresh(record)

            current = record.published_count
            limit = record.limit_count

            if blog_id == 3:  # ItemPick24
                return False, current, 0, "아이템픽24는 자동 스케줄 대상이 아니며 수동 URL 즉시발행 전용입니다."

            if current >= limit:
                msg = f"오늘({target_date}) 블로그 #{blog_id}의 일일 최대 발행 한도({limit}편)를 초과하여 발행이 차단되었습니다 (현재: {current}편)."
                logger.warning(msg)
                return False, current, limit, msg

            remaining = limit - current
            msg = f"블로그 #{blog_id} 오늘 발행 가능 (현재: {current}/{limit}편, 잔여: {remaining}편)."
            return True, current, limit, msg

    @classmethod
    def record_publication(cls, blog_id: int, date_str: Optional[str] = None) -> int:
        """Increments the published count for blog_id on date_str."""
        target_date = date_str or cls._get_kst_today()
        default_limit = DEFAULT_DAILY_LIMITS.get(blog_id, 4)

        with get_aaos_db_session() as session:
            record = session.query(DailyPublishLimit).filter(
                DailyPublishLimit.blog_id == blog_id,
                DailyPublishLimit.date == target_date
            ).first()

            if not record:
                record = DailyPublishLimit(
                    blog_id=blog_id,
                    date=target_date,
                    limit_count=default_limit,
                    published_count=1
                )
                session.add(record)
            else:
                record.published_count += 1

            session.commit()
            logger.info("Recorded publication for Blog #%d on %s (Count: %d/%d)", blog_id, target_date, record.published_count, record.limit_count)
            return record.published_count

    @classmethod
    def get_status_overview(cls, date_str: Optional[str] = None) -> Dict[str, Any]:
        """Returns overview of all 8 blogs' daily publishing counts for today."""
        target_date = date_str or cls._get_kst_today()
        overview = {}

        with get_aaos_db_session() as session:
            records = session.query(DailyPublishLimit).filter(
                DailyPublishLimit.date == target_date
            ).all()

            record_map = {r.blog_id: r for r in records}

            for blog_id in range(1, 9):
                rec = record_map.get(blog_id)
                published = rec.published_count if rec else 0
                limit = rec.limit_count if rec else DEFAULT_DAILY_LIMITS.get(blog_id, 4)
                overview[blog_id] = {
                    "published": published,
                    "limit": limit,
                    "is_full": (published >= limit and limit > 0),
                    "remaining": max(0, limit - published) if limit > 0 else 0
                }

        return {"date": target_date, "blogs": overview}
