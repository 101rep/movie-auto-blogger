"""
AAOS LangGraph Multi-Agent State Definition
"""

from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict

class AAOSState(TypedDict):
    job_id: int
    platform: str                    # 'threads' | 'instagram' | 'wordpress'
    account: Optional[str]
    target_topic: str
    content_payload: Dict[str, Any]  # title, body, slides, image_urls, tags
    qa_results: Dict[str, Any]       # passed: bool, score: float, critiques: list
    qa_retries: int                  # counter for re-drafting
    publish_result: Dict[str, Any]   # success: bool, remote_id: str, post_url: str, error: str
    verification_result: Dict[str, Any] # verified: bool, screenshot: str, details: str
    recovery_attempts: int           # counter for retry publishing
    final_status: str                # 'SUCCESS' | 'FAILED' | 'REJECTED'
    logs: List[str]
