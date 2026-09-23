import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import JobLog

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AutomationSystem")

def start_job_log(db: Session, job_type: str, input_data: Optional[Dict[str, Any]] = None) -> JobLog:
    inp_str = json.dumps(input_data, ensure_ascii=False) if input_data else None
    job = JobLog(
        job_type=job_type,
        status="STARTED",
        input_data=inp_str,
        started_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info(f"Job started: {job_type} (ID: {job.id})")
    return job

def finish_job_log(
    db: Session,
    job: JobLog,
    status: str = "SUCCESS",
    output_data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> JobLog:
    job.status = status
    if output_data is not None:
        job.output_data = json.dumps(output_data, ensure_ascii=False)
    if error is not None:
        job.error = str(error)
    job.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    logger.info(f"Job finished: {job.job_type} (ID: {job.id}, Status: {status})")
    return job