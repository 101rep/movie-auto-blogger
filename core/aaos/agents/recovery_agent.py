"""
AAOS Recovery Agent & Browser Verifier Node
Handles post-publication Playwright DOM verification and automated recovery.
"""

import time
import logging
from typing import Dict, Any
from core.aaos.agents.state import AAOSState
from core.aaos.job_service import AAOSJobService
from verification.playwright_verifier import PlaywrightVerifier
from monitoring.metrics import metrics_collector

logger = logging.getLogger("AAOSRecoveryAgent")

class VerifierNode:
    @staticmethod
    def verify(state: AAOSState) -> Dict[str, Any]:
        """Runs Playwright headless browser to confirm post visibility and layout."""
        job_id = state.get("job_id", 0)
        platform = state.get("platform", "threads")
        post_url = state.get("publish_result", {}).get("post_url", "")
        payload = state.get("content_payload", {})

        verifier = PlaywrightVerifier()
        logger.info(f"[VerifierNode] Running Playwright verification for Job #{job_id} at {post_url}")

        if platform == "threads":
            res = verifier.verify_threads(post_url, expected_snippet=payload.get("title"))
        elif platform == "instagram":
            res = verifier.verify_instagram(post_url)
        elif platform == "wordpress":
            res = verifier.verify_wordpress(post_url, expected_title=payload.get("title"))
        else:
            res = {"verified": False, "status": "UNKNOWN_PLATFORM", "screenshot": "", "details": "Unknown platform"}

        # Record in DB & Prometheus
        AAOSJobService.record_verification(
            job_id=job_id,
            platform=platform,
            post_url=post_url,
            verified=res["verified"],
            screenshot_path=res.get("screenshot"),
            error_details=res.get("details")
        )
        metrics_collector.record_verification(platform=platform, verified=res["verified"])

        log_msg = f"[VerifierNode] Job #{job_id} verification {'PASSED' if res['verified'] else 'FAILED'}: {res.get('details')}"
        logger.info(log_msg)

        return {
            "verification_result": res,
            "logs": state.get("logs", []) + [log_msg]
        }

class RecoveryAgent:
    @staticmethod
    def recover(state: AAOSState) -> Dict[str, Any]:
        """Diagnoses failure and manages automatic recovery or escalation."""
        job_id = state.get("job_id", 0)
        platform = state.get("platform", "threads")
        recovery_attempts = state.get("recovery_attempts", 0)
        pub_err = state.get("publish_result", {}).get("error")
        verif_err = state.get("verification_result", {}).get("details")
        
        reason = pub_err or verif_err or "Unknown failure"
        metrics_collector.record_recovery(platform=platform, reason="automated_retry")

        if recovery_attempts < 3:
            # Exponential backoff calculation
            backoff_sec = (2 ** recovery_attempts) * 2
            log_msg = f"[RecoveryAgent] Job #{job_id} failure detected ({reason}). Triggering auto-retry #{recovery_attempts + 1} after {backoff_sec}s backoff."
            logger.warning(log_msg)

            time.sleep(backoff_sec)

            return {
                "recovery_attempts": recovery_attempts + 1,
                "logs": state.get("logs", []) + [log_msg]
            }
        else:
            log_msg = f"[RecoveryAgent] Job #{job_id} permanently failed after {recovery_attempts} retries. Reason: {reason}. Escalated to Telegram Alert."
            logger.critical(log_msg)

            return {
                "final_status": "FAILED",
                "logs": state.get("logs", []) + [log_msg]
            }
