"""
AAOS Job Service - Centralized lifecycle and database service for AAOS Jobs,
execution logs, and Playwright verification logs.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import logging
from sqlalchemy import desc

from core.aaos.db import get_aaos_db_session
from core.aaos.models import AAOSJob, AAOSExecutionLog, AAOSVerificationLog

logger = logging.getLogger("AAOSJobService")

class AAOSJobService:
    @staticmethod
    def create_job(platform: str, account: Optional[str] = None, content_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> AAOSJob:
        with get_aaos_db_session() as session:
            job = AAOSJob(
                platform=platform,
                account=account,
                content_id=content_id,
                status="PENDING",
                payload_json=json.dumps(payload or {}, ensure_ascii=False)
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            session.expunge(job)
            return job

    @staticmethod
    def mark_in_progress(job_id: int):
        with get_aaos_db_session() as session:
            job = session.query(AAOSJob).filter(AAOSJob.id == job_id).first()
            if job:
                job.status = "IN_PROGRESS"
                session.commit()

    @staticmethod
    def record_execution(
        job_id: int,
        success: bool,
        api_response: Optional[str] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        retry_count: int = 0,
        duration_ms: int = 0
    ) -> AAOSExecutionLog:
        with get_aaos_db_session() as session:
            job = session.query(AAOSJob).filter(AAOSJob.id == job_id).first()
            if job:
                if success:
                    job.status = "API_SUCCESS"
                else:
                    job.status = "FAILED"
                    job.retry_count = retry_count
                    job.last_error = error_message
            
            exec_log = AAOSExecutionLog(
                job_id=job_id,
                api_response=api_response,
                error_message=error_message,
                error_code=error_code,
                retry_count=retry_count,
                duration_ms=duration_ms
            )
            session.add(exec_log)
            session.commit()
            session.refresh(exec_log)
            session.expunge(exec_log)
            return exec_log

    @staticmethod
    def record_verification(
        job_id: int,
        platform: str,
        post_url: str,
        verified: bool,
        screenshot_path: Optional[str] = None,
        error_details: Optional[str] = None
    ) -> AAOSVerificationLog:
        with get_aaos_db_session() as session:
            job = session.query(AAOSJob).filter(AAOSJob.id == job_id).first()
            if job:
                if verified:
                    job.status = "VERIFIED"
                    job.completed_at = datetime.now(timezone.utc)
                else:
                    job.status = "VERIFICATION_FAILED"
                    job.last_error = error_details

            verif_log = AAOSVerificationLog(
                job_id=job_id,
                platform=platform,
                post_url=post_url,
                verified=1 if verified else 0,
                screenshot_path=screenshot_path,
                error_details=error_details
            )
            session.add(verif_log)
            session.commit()
            session.refresh(verif_log)
            session.expunge(verif_log)
            return verif_log

    @staticmethod
    def get_system_status() -> Dict[str, Any]:
        """Returns high-level statistics across all registered AAOS jobs."""
        with get_aaos_db_session() as session:
            total_jobs = session.query(AAOSJob).count()
            verified = session.query(AAOSJob).filter(AAOSJob.status == "VERIFIED").count()
            failed = session.query(AAOSJob).filter(AAOSJob.status.in_(["FAILED", "VERIFICATION_FAILED"])).count()
            pending = session.query(AAOSJob).filter(AAOSJob.status.in_(["PENDING", "IN_PROGRESS", "API_SUCCESS"])).count()

            # By platform
            platforms = ["threads", "instagram", "wordpress"]
            platform_stats = {}
            for p in platforms:
                p_total = session.query(AAOSJob).filter(AAOSJob.platform == p).count()
                p_verified = session.query(AAOSJob).filter(AAOSJob.platform == p, AAOSJob.status == "VERIFIED").count()
                p_failed = session.query(AAOSJob).filter(AAOSJob.platform == p, AAOSJob.status.in_(["FAILED", "VERIFICATION_FAILED"])).count()
                platform_stats[p] = {
                    "total": p_total,
                    "verified": p_verified,
                    "failed": p_failed
                }

            return {
                "total_jobs": total_jobs,
                "verified": verified,
                "failed": failed,
                "pending": pending,
                "platforms": platform_stats
            }

    @staticmethod
    def get_recent_failed_jobs(limit: int = 10) -> List[Dict[str, Any]]:
        with get_aaos_db_session() as session:
            jobs = session.query(AAOSJob).filter(
                AAOSJob.status.in_(["FAILED", "VERIFICATION_FAILED"])
            ).order_by(desc(AAOSJob.id)).limit(limit).all()

            results = []
            for j in jobs:
                results.append({
                    "id": j.id,
                    "platform": j.platform,
                    "account": j.account,
                    "content_id": j.content_id,
                    "status": j.status,
                    "retry_count": j.retry_count,
                    "last_error": j.last_error,
                    "created_at": j.created_at.isoformat() if j.created_at else None
                })
            return results

    @staticmethod
    def get_recent_logs(limit: int = 15) -> List[Dict[str, Any]]:
        with get_aaos_db_session() as session:
            exec_logs = session.query(AAOSExecutionLog).order_by(desc(AAOSExecutionLog.id)).limit(limit).all()
            results = []
            for log in exec_logs:
                results.append({
                    "id": log.id,
                    "job_id": log.job_id,
                    "error_message": log.error_message,
                    "error_code": log.error_code,
                    "retry_count": log.retry_count,
                    "duration_ms": log.duration_ms,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                })
            return results
