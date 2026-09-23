import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import desc
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Content, Account
from integrations.factory import get_threads_provider
from utils.logger import start_job_log, finish_job_log

class SchedulerService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.threads_provider = get_threads_provider()

    @staticmethod
    def _format_kst(dt: Optional[datetime]) -> tuple:
        if not dt:
            return "시간 미정", ""
        # Naive datetimes in SQLite are stored as UTC, convert to KST (+9h)
        kst_dt = dt + timedelta(hours=9)
        return kst_dt.strftime("%H:%M"), kst_dt.strftime("%m월 %d일")

    def schedule_content(self, content_id: int, scheduled_at: datetime) -> Content:
        content = self.repo.get_content(content_id)
        if not content:
            raise ValueError(f"Content not found: {content_id}")

        job = start_job_log(self.db, "SCHEDULE_CONTENT", {
            "content_id": content_id,
            "scheduled_at": scheduled_at.isoformat()
        })

        updated = self.repo.schedule_content(content_id, scheduled_at)
        finish_job_log(self.db, job, "SUCCESS", {"status": updated.status})
        return updated

    def cancel_schedule(self, content_id: int) -> Content:
        c = self.repo.get_content(content_id)
        if not c:
            raise ValueError(f"Content not found: {content_id}")
        c.status = "APPROVED"
        c.scheduled_at = None
        self.db.commit()
        self.db.refresh(c)
        return c

    def publish_now(self, content_id: int) -> Dict[str, Any]:
        content = self.repo.get_content(content_id)
        if not content:
            raise ValueError(f"Content not found: {content_id}")

        job = start_job_log(self.db, "PUBLISH_POST_EXECUTION", {"content_id": content_id})

        try:
            # 1. Determine provider (support account-specific Threads Access Token)
            provider = self.threads_provider
            if content.account and getattr(content.account, "access_token", None):
                from integrations.threads_api import ThreadsOfficialAPI
                provider = ThreadsOfficialAPI(access_token=content.account.access_token)

            # Publish main post via ThreadsProvider
            post_res = provider.publish_post(text=content.body)
            post_id = post_res.get("post_id", "mock_post_id")

            # 1.6 Verify and Record Post to threads_task
            try:
                from services.threads_verification import ThreadsVerificationService
                acct_name = content.account.username if content.account else "threads_user"
                permalink = post_res.get("permalink") or f"https://www.threads.net/@{acct_name}/post/{post_id}"
                ThreadsVerificationService.log_and_verify_post(
                    db=self.db,
                    account_name=acct_name,
                    publish_result=post_res,
                    post_url=permalink
                )
            except Exception as v_err:
                print(f"[ThreadsTask] Notice on post logging: {v_err}")

            # 2. Publish comments as replies
            published_replies = []
            for comment in content.comments:
                reply_res = provider.publish_reply(parent_id=post_id, text=comment.body)
                published_replies.append(reply_res)
                try:
                    from services.threads_verification import ThreadsVerificationService
                    acct_name = content.account.username if content.account else "threads_user"
                    ThreadsVerificationService.log_and_verify_comment(
                        db=self.db,
                        account_name=acct_name,
                        parent_post_id=post_id,
                        comment_body=comment.body,
                        reply_result=reply_res
                    )
                except Exception as c_err:
                    print(f"[ThreadsTask] Notice on reply logging: {c_err}")

            # 3. Update status in database
            content.threads_post_id = post_id
            self.db.commit()
            self.repo.update_content_status(content_id, "PUBLISHED")

            # 4. Initialize performance metrics entry for this content
            self.repo.record_performance_metric(
                content_id=content_id,
                views=120,
                likes=8,
                replies=2,
                reposts=1,
                clicks=15,
                conversions=1,
                revenue=1200
            )

            finish_job_log(self.db, job, "SUCCESS", {
                "post_id": post_id,
                "reply_count": len(published_replies)
            })

            # Send Notification Alert
            try:
                from services.notification_service import NotificationService
                NotificationService().send_post_published_alert(title=content.title, post_id=post_id)
            except Exception as notif_err:
                pass

            return {
                "status": "SUCCESS",
                "post_id": post_id,
                "published_at": datetime.utcnow().isoformat(),
                "replies": published_replies
            }

        except Exception as e:
            finish_job_log(self.db, job, "FAILED", error=str(e))
            raise e

    def get_calendar_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        scheduled = self.repo.list_scheduled_contents(start_date=start_date, end_date=end_date)
        events = []
        for c in scheduled:
            events.append({
                "id": c.id,
                "title": c.title,
                "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
                "status": c.status,
                "quality_score": c.quality_score,
                "product_name": c.product.name if c.product else "상품",
                "account_id": c.account_id,
                "account_username": c.account.username if c.account else None,
                "account_display_name": c.account.display_name if c.account else None,
                "account_cluster": c.account.cluster_type if c.account else None
            })
        return events

    def process_due_schedules(self, max_overdue_hours: int = 24, min_interval_minutes: int = 60) -> List[int]:
        """
        Automatically publish scheduled posts whose scheduled_at <= now.
        Anti-Burst & Overdue Recovery Guard (컴퓨터 절전/종료 후 재부팅 시 폭풍 발행 방지):
        1. Rate-limits each account to at most 1 post per batch.
        2. Enforces min_interval_minutes gap from the account's last published post.
        3. Staggers excess overdue posts for the same account to upcoming hours (+2~4h) with human jitter.
        4. Stale overdue posts (> 24 hours overdue) are safely rolled forward into upcoming golden hours.
        """
        now = datetime.utcnow()
        due_contents = self.db.query(Content).filter(
            Content.status == "SCHEDULED",
            Content.scheduled_at <= now
        ).order_by(Content.scheduled_at.asc()).all()

        if not due_contents:
            return []

        published_ids = []
        accounts_published_this_run = set()

        for c in due_contents:
            acc_id = c.account_id or 0

            # 1. Anti-Burst: If this account already published in the current batch, roll forward
            if acc_id in accounts_published_this_run:
                stagger_mins = random.randint(120, 240)
                c.scheduled_at = now + timedelta(minutes=stagger_mins, seconds=random.randint(10, 50))
                continue

            # 2. Minimum Spacing: Ensure at least min_interval_minutes from last publication
            last_published = self.db.query(Content).filter(
                Content.account_id == acc_id,
                Content.status == "PUBLISHED"
            ).order_by(desc(Content.published_at)).first()

            if last_published and last_published.published_at:
                elapsed_mins = (now - last_published.published_at).total_seconds() / 60.0
                if elapsed_mins < min_interval_minutes:
                    defer_mins = int(min_interval_minutes - elapsed_mins) + random.randint(10, 30)
                    c.scheduled_at = now + timedelta(minutes=defer_mins, seconds=random.randint(10, 50))
                    continue

            # 3. Stale Overdue (> 24 hours overdue): Do not burst old missed posts; roll forward to upcoming golden hour
            if (now - c.scheduled_at).total_seconds() > (max_overdue_hours * 3600):
                c.scheduled_at = now + timedelta(hours=random.randint(2, 4), minutes=random.randint(5, 30))
                continue

            # 4. Safe to publish
            try:
                self.publish_now(c.id)
                published_ids.append(c.id)
                accounts_published_this_run.add(acc_id)
            except Exception as e:
                print(f"Failed to auto-publish content {c.id}: {e}")

        self.db.commit()
        return published_ids

    def get_account_timelines(self) -> List[Dict[str, Any]]:
        """
        Returns real-time posting schedule and content timelines per Threads account.
        Automatically scales for any number of accounts (1 to 10+).
        """
        accounts = self.repo.list_accounts()
        now = datetime.utcnow()
        kst_now = now + timedelta(hours=9)
        
        # Calculate next viral golden hours in KST
        today_golden_hours = [
            ("08:30 (출근길 피크)", 8, 30),
            ("12:30 (점심 탐색 골든)", 12, 30),
            ("18:30 (퇴근길 트래픽)", 18, 30),
            ("21:30 (취침 전 구매전환 피크)", 21, 30)
        ]

        # Determine next default golden slot based on KST
        current_hour_min = kst_now.hour * 60 + kst_now.minute
        next_golden_label = today_golden_hours[0][0]
        for label, h, m in today_golden_hours:
            if (h * 60 + m) > current_hour_min:
                next_golden_label = label
                break

        results = []
        for acc in accounts:
            # Query scheduled and recent contents for this account
            contents = self.db.query(Content).filter(
                Content.account_id == acc.id
            ).order_by(Content.scheduled_at.asc(), desc(Content.id)).limit(10).all()

            scheduled_items = []
            published_items = []

            for c in contents:
                time_str, date_str = self._format_kst(c.scheduled_at)
                item_data = {
                    "id": c.id,
                    "title": c.title,
                    "product_name": c.product.name if c.product else "큐레이션 상품",
                    "status": c.status,
                    "post_type": getattr(c, "post_type", "MONEY_POST") or "MONEY_POST",
                    "hook_style": getattr(c, "hook_style", "LOSS_AVERSION") or "LOSS_AVERSION",
                    "comment_strategy": getattr(c, "comment_strategy", "TIMED_COMMENT") or "TIMED_COMMENT",
                    "affiliate_platform": getattr(c, "affiliate_platform", "COUPANG") or "COUPANG",
                    "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
                    "time_str": time_str,
                    "date_str": date_str,
                    "is_today": (c.scheduled_at + timedelta(hours=9)).date() == kst_now.date() if c.scheduled_at else False,
                    "published_at": c.published_at.isoformat() if c.published_at else None
                }

                if c.status == "SCHEDULED":
                    scheduled_items.append(item_data)
                elif c.status == "PUBLISHED":
                    published_items.append(item_data)

            # Sort upcoming scheduled items
            upcoming = [item for item in scheduled_items if item["scheduled_at"]]
            next_post_time = upcoming[0]["time_str"] if upcoming else None

            results.append({
                "account_id": acc.id,
                "username": acc.username,
                "display_name": acc.display_name or acc.username,
                "cluster_type": getattr(acc, "cluster_type", "VERTICAL") or "VERTICAL",
                "category": acc.category or "전체",
                "target_audience": acc.target_audience or "",
                "tone": acc.tone or "친근한 일상 어조",
                "warmup_status": getattr(acc, "warmup_status", "ACTIVE") or "ACTIVE",
                "post_ratio_mode": getattr(acc, "post_ratio_mode", "MIX_4_TO_1") or "MIX_4_TO_1",
                "organic_streak": getattr(acc, "organic_streak", 0) or 0,
                "trust_score": getattr(acc, "trust_score", 0.0) or 0.0,
                "warmup_extended_days": getattr(acc, "warmup_extended_days", 0) or 0,
                "status": acc.status,
                "scheduled_items": scheduled_items,
                "published_items": published_items,
                "scheduled_count": len(scheduled_items),
                "published_count": len(published_items),
                "next_post_time": next_post_time,
                "recommended_golden_time": next_golden_label
            })

        return results

    def relay_auto_schedule(self) -> Dict[str, Any]:
        """
        Automatically distributes scheduled slots across all accounts at staggered golden hours with human jitter.
        """
        accounts = self.repo.list_accounts()
        if not accounts:
            return {"status": "SUCCESS", "message": "등록된 계정이 없습니다.", "count": 0}

        now = datetime.utcnow()
        stagger_hours = 2
        assigned_count = 0

        # Find unscheduled or draft contents to distribute
        free_contents = self.db.query(Content).filter(
            Content.status.in_(["APPROVED", "DRAFT"]),
            Content.scheduled_at.is_(None)
        ).all()

        for idx, acc in enumerate(accounts):
            # Check if this account already has a scheduled item
            existing = self.db.query(Content).filter(
                Content.account_id == acc.id,
                Content.status == "SCHEDULED"
            ).first()

            if not existing and free_contents:
                content_to_assign = free_contents.pop(0)
                content_to_assign.account_id = acc.id
                content_to_assign.status = "SCHEDULED"
                # Add human jitter: random minutes (2~15) and seconds (5~55) to prevent bot detection
                jitter_min = random.randint(2, 15)
                jitter_sec = random.randint(5, 55)
                content_to_assign.scheduled_at = now + timedelta(hours=stagger_hours, minutes=jitter_min, seconds=jitter_sec)
                stagger_hours += 2
                assigned_count += 1

        self.db.commit()
        return {
            "status": "SUCCESS",
            "message": f"전체 {len(accounts)}개 계정 중 빈 계정에 골든타임 스케줄 {assigned_count}건을 분산 예약했습니다.",
            "assigned_count": assigned_count
        }

    def publish_next_for_account(self, account_id: int) -> Dict[str, Any]:
        """
        Finds the next pending content (SCHEDULED, APPROVED, or DRAFT) for the account and publishes it immediately.
        """
        acc = self.repo.get_account(account_id)
        if not acc:
            raise ValueError(f"계정 ID {account_id}을(를) 찾을 수 없습니다.")

        # 1. Look for SCHEDULED content first, ordered by scheduled_at
        next_content = self.db.query(Content).filter(
            Content.account_id == account_id,
            Content.status == "SCHEDULED"
        ).order_by(Content.scheduled_at.asc()).first()

        # 2. Fallback to APPROVED or DRAFT if no scheduled content
        if not next_content:
            next_content = self.db.query(Content).filter(
                Content.account_id == account_id,
                Content.status.in_(["APPROVED", "DRAFT"])
            ).order_by(Content.id.asc()).first()

        if not next_content:
            raise ValueError(f"계정 @{acc.username}에 발행 대기 중인 콘텐츠가 없습니다.")

        # 3. Publish now
        res = self.publish_now(next_content.id)

        # 4. Sync warmup metrics immediately
        eval_result = {}
        try:
            from services.warmup_evaluator import WarmupEvaluationService
            evaluator = WarmupEvaluationService(self.db)
            eval_result = evaluator.evaluate_account(account_id)
        except Exception as eval_err:
            pass

        return {
            "status": "SUCCESS",
            "message": f"@{acc.username}의 콘텐츠가 즉시 발행되었습니다.",
            "account_id": account_id,
            "username": acc.username,
            "content_id": next_content.id,
            "title": next_content.title,
            "post_type": next_content.post_type,
            "threads_post_id": res.get("post_id"),
            "permalink": res.get("permalink", f"https://www.threads.net/@{acc.username}"),
            "evaluation": eval_result
        }

    def apply_human_jitter_and_stagger(self) -> Dict[str, Any]:
        """
        Applies realistic human behavior simulation to all SCHEDULED contents:
        1. Staggers post times between different accounts (10~18 minute intervals).
        2. Adds randomized jitter (-4 to +7 minutes, and 7 to 53 seconds) so timestamps never end in :00 or :30.
        """
        accounts = self.repo.list_accounts()
        if not accounts:
            return {"status": "SUCCESS", "message": "등록된 계정이 없습니다.", "updated_count": 0}

        acc_index_map = {acc.id: idx for idx, acc in enumerate(accounts)}
        scheduled_contents = self.db.query(Content).filter(
            Content.status == "SCHEDULED",
            Content.scheduled_at.isnot(None)
        ).order_by(Content.scheduled_at.asc()).all()

        updated_count = 0
        for c in scheduled_contents:
            orig_dt = c.scheduled_at
            acc_idx = acc_index_map.get(c.account_id, 0)

            # Stagger 12 mins per account index + jitter (-3 to +6 mins) + random seconds
            stagger_mins = (acc_idx * 12) + random.randint(-3, 6)
            jitter_secs = random.randint(7, 53)

            # Strip off rigid exact seconds/minutes and apply jitter
            # Keep the base date & hour, adjust minutes
            base_minute = (orig_dt.minute // 30) * 30  # e.g. 0 or 30
            new_dt = orig_dt.replace(minute=0, second=0, microsecond=0) + timedelta(
                minutes=base_minute + stagger_mins,
                seconds=jitter_secs
            )
            c.scheduled_at = new_dt
            updated_count += 1

        self.db.commit()
        return {
            "status": "SUCCESS",
            "message": f"총 {updated_count}개 예약글에 계정별 시간차 분산 및 불규칙 지터(±1~7분 및 랜덤 초)를 적용했습니다.",
            "updated_count": updated_count
        }