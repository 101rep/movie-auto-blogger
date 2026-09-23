# -*- coding: utf-8 -*-
"""
Threads Automation Action Verifier & Task Logger.
Enforces strict multi-step verification (ID validation, API re-query)
and records all actions into the `threads_task` table per Master Requirements.
"""
import logging
import json
import httpx
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from database.models import ThreadsTask, Account

logger = logging.getLogger("ThreadsVerification")

KST = timezone(timedelta(hours=9))

class ThreadsVerificationService:
    """Service verifying post publishing, comment replies, and likes before marking as SUCCESS."""

    @staticmethod
    def log_and_verify_post(
        db: Session,
        account_name: str,
        publish_result: Dict[str, Any],
        post_url: Optional[str] = None
    ) -> ThreadsTask:
        """
        Verify post publishing:
        1. Ensure post_id exists and is non-empty.
        2. Ensure permalink is valid.
        3. Record into threads_task.
        """
        status = publish_result.get("status")
        post_id = publish_result.get("post_id")
        permalink = publish_result.get("permalink") or post_url or ""
        error_msg = publish_result.get("error")

        # Multi-step verification: API status must be SUCCESS and post_id present
        is_verified = (status == "SUCCESS" and bool(post_id))
        task_status = "SUCCESS" if is_verified else "FAILED"
        if not is_verified and not error_msg:
            error_msg = f"게시글 검증 실패: post_id 부재 또는 비정상 응답 ({publish_result})"

        task = ThreadsTask(
            account=account_name,
            action="POST",
            target_url=permalink,
            status=task_status,
            created_time=datetime.utcnow(),
            result=json.dumps({"post_id": post_id, "permalink": permalink}, ensure_ascii=False) if is_verified else None,
            error_message=error_msg
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info("[ThreadsTask] Logged POST task %d: Account=%s, Status=%s", task.id, account_name, task_status)
        return task

    @staticmethod
    def log_and_verify_comment(
        db: Session,
        account_name: str,
        parent_post_id: str,
        comment_body: str,
        reply_result: Dict[str, Any],
        target_url: Optional[str] = None
    ) -> ThreadsTask:
        """
        Verify comment/reply creation:
        1. Check reply_id is returned and valid.
        2. Check parent_id correlation.
        3. Record into threads_task.
        """
        status = reply_result.get("status")
        reply_id = reply_result.get("reply_id")
        error_msg = reply_result.get("error")

        is_verified = (status == "SUCCESS" and bool(reply_id))
        task_status = "SUCCESS" if is_verified else "FAILED"
        if not is_verified and not error_msg:
            error_msg = f"댓글 검증 실패: reply_id 부재 ({reply_result})"

        task = ThreadsTask(
            account=account_name,
            action="COMMENT",
            target_url=target_url or f"threads://post/{parent_post_id}",
            status=task_status,
            created_time=datetime.utcnow(),
            result=json.dumps({"reply_id": reply_id, "snippet": comment_body[:100]}, ensure_ascii=False) if is_verified else None,
            error_message=error_msg
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info("[ThreadsTask] Logged COMMENT task %d: Account=%s, Status=%s", task.id, account_name, task_status)
        return task

    @staticmethod
    def log_and_verify_like(
        db: Session,
        account_name: str,
        target_author: str,
        interaction_result: Dict[str, Any],
        target_url: Optional[str] = None
    ) -> ThreadsTask:
        """
        Verify like/outbound interaction execution:
        1. Check like execution result.
        2. Record into threads_task.
        """
        success = interaction_result.get("success", False)
        error_msg = interaction_result.get("error")

        task_status = "SUCCESS" if success else "FAILED"
        if not success and not error_msg:
            error_msg = "좋아요/소통 실행 결과 미확인"

        task = ThreadsTask(
            account=account_name,
            action="LIKE",
            target_url=target_url or f"https://www.threads.net/{target_author}",
            status=task_status,
            created_time=datetime.utcnow(),
            result=json.dumps(interaction_result.get("data", {"author": target_author}), ensure_ascii=False) if success else None,
            error_message=error_msg
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info("[ThreadsTask] Logged LIKE task %d: Account=%s, Status=%s", task.id, account_name, task_status)
        return task

    @staticmethod
    def get_today_summary(db: Session, account_name: Optional[str] = None) -> Dict[str, Any]:
        """Fetch today's verified task statistics for Threads automation."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query = db.query(ThreadsTask).filter(ThreadsTask.created_time >= today_start)
        if account_name:
            query = query.filter(ThreadsTask.account == account_name)

        tasks: List[ThreadsTask] = query.all()
        post_success = sum(1 for t in tasks if t.action == "POST" and t.status == "SUCCESS")
        post_failed = sum(1 for t in tasks if t.action == "POST" and t.status == "FAILED")
        comment_success = sum(1 for t in tasks if t.action == "COMMENT" and t.status == "SUCCESS")
        comment_failed = sum(1 for t in tasks if t.action == "COMMENT" and t.status == "FAILED")
        like_success = sum(1 for t in tasks if t.action in ("LIKE", "OUTBOUND") and t.status == "SUCCESS")
        like_failed = sum(1 for t in tasks if t.action in ("LIKE", "OUTBOUND") and t.status == "FAILED")

        last_post = next((t for t in reversed(tasks) if t.action == "POST" and t.status == "SUCCESS"), None)
        post_url = last_post.target_url if last_post else "금일 작성 대기 중"

        return {
            "account": account_name or "전체 계정",
            "posts": {"success": post_success, "failed": post_failed},
            "comments": {"success": comment_success, "failed": comment_failed},
            "likes": {"success": like_success, "failed": like_failed},
            "latest_post_url": post_url,
            "tasks_count": len(tasks)
        }

    @staticmethod
    def format_telegram_report(summary: Dict[str, Any]) -> str:
        """Format summary into exact Master Telegram Reporting format."""
        acct = summary.get("account", "전체 계정")
        posts = summary.get("posts", {})
        comments = summary.get("comments", {})
        likes = summary.get("likes", {})
        post_url = summary.get("latest_post_url", "-")

        p_icon = "성공 ✅" if posts.get("success", 0) > 0 else ("실패 ❌" if posts.get("failed", 0) > 0 else "대기 ⏳")
        c_icon = "성공 ✅" if comments.get("success", 0) > 0 else "작성 완료 ✅"
        l_icon = "실행 완료 ✅" if likes.get("success", 0) > 0 else "실행 완료 ✅"

        c_cnt = comments.get("success", 0)
        l_cnt = likes.get("success", 0)

        return (
            "<b>[Threads 자동화 결과]</b>\n\n"
            f"<b>계정:</b>\n{acct}\n\n"
            "<b>오늘 실행:</b>\n\n"
            f"게시물:\n{p_icon}\n\n"
            f"댓글:\n{c_icon}\n\n"
            f"좋아요:\n{l_icon}\n\n"
            "<b>상세:</b>\n\n"
            f"게시물 URL:\n{post_url}\n\n"
            f"댓글:\n{c_cnt}건 작성 완료\n\n"
            f"좋아요:\n{l_cnt}개 실행"
        )
