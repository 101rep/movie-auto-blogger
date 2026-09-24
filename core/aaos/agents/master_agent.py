"""
AAOS Master Agent - Orchestrates task lifecycle and registers job entries in DB.
"""

import logging
from typing import Dict, Any
from core.aaos.agents.state import AAOSState
from core.aaos.job_service import AAOSJobService

logger = logging.getLogger("AAOSMasterAgent")

class MasterAgent:
    @staticmethod
    def initialize(state: AAOSState) -> Dict[str, Any]:
        """Validates input parameters and creates AAOSJob record."""
        platform = state.get("platform", "threads").lower()
        topic = state.get("target_topic", "General Update")
        account = state.get("account", "@ktaehoon80")

        # Create or fetch persistent job ID
        job_id = state.get("job_id", 0)
        if not job_id:
            job = AAOSJobService.create_job(
                platform=platform,
                account=account,
                content_id=f"topic_{hash(topic) % 100000}",
                payload={"topic": topic}
            )
            job_id = job.id

        log_entry = f"[MasterAgent] Job #{job_id} initialized for platform '{platform}', topic: '{topic[:30]}...'"
        logger.info(log_entry)

        return {
            "job_id": job_id,
            "platform": platform,
            "account": account,
            "target_topic": topic,
            "qa_retries": state.get("qa_retries", 0),
            "recovery_attempts": state.get("recovery_attempts", 0),
            "logs": state.get("logs", []) + [log_entry]
        }

    @staticmethod
    def finalize(state: AAOSState) -> Dict[str, Any]:
        """Summarizes final outcome of the entire workflow."""
        job_id = state.get("job_id")
        verified = state.get("verification_result", {}).get("verified", False)
        pub_success = state.get("publish_result", {}).get("success", False)

        final_status = "SUCCESS" if (pub_success and verified) else "FAILED"
        log_entry = f"[MasterAgent] Job #{job_id} workflow concluded with status: {final_status}"
        logger.info(log_entry)

        return {
            "final_status": final_status,
            "logs": state.get("logs", []) + [log_entry]
        }
