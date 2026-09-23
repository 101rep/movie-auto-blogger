from typing import List, Dict, Any
from sqlalchemy.orm import Session
from services.autopilot_service import AutopilotService
from utils.logger import start_job_log, finish_job_log

class BulkImportService:
    """
    Bulk Product Batch Automation Service.
    Imports multiple keywords or product sources and automatically generates spaced calendar schedules.
    """
    def __init__(self, db: Session):
        self.db = db
        self.autopilot_svc = AutopilotService(db)

    def process_bulk_keywords(self, keywords: List[str], base_interval_hours: int = 4) -> Dict[str, Any]:
        job = start_job_log(self.db, "BULK_BATCH_PROCESSING", {"keyword_count": len(keywords)})
        results = []
        failures = []

        current_offset = 2  # Start 2 hours from now
        for kw in keywords:
            kw = kw.strip()
            if not kw:
                continue
            try:
                auto_res = self.autopilot_svc.run_autopilot(
                    keyword=kw,
                    schedule_hours_later=current_offset
                )
                results.append({
                    "keyword": kw,
                    "status": "SUCCESS",
                    "content_id": auto_res["content_id"],
                    "title": auto_res["title"],
                    "scheduled_at": auto_res["scheduled_at"]
                })
                current_offset += base_interval_hours  # Space next post by X hours
            except Exception as e:
                failures.append({
                    "keyword": kw,
                    "error": str(e)
                })

        finish_job_log(self.db, job, "SUCCESS", {
            "success_count": len(results),
            "failure_count": len(failures)
        })

        return {
            "status": "SUCCESS",
            "total_processed": len(keywords),
            "success_count": len(results),
            "failure_count": len(failures),
            "results": results,
            "failures": failures
        }