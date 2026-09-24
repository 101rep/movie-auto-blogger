"""
AAOS QA Agent - Rigorous Pre-Publication Quality Auditor
Verifies compliance with Anti-Cliche, length constraints, and structural fidelity.
"""

import logging
from typing import Dict, Any, List
from core.aaos.agents.state import AAOSState

logger = logging.getLogger("AAOSQAAgent")

BANNED_CLICHES = [
    "현대 사회에서",
    "더 나은 미래를 위해",
    "지금 바로 알아보겠습니다",
    "눈길을 끕니다",
    "주목받고 있습니다",
    "놀라운 혁신"
]

class QAAgent:
    @staticmethod
    def audit(state: AAOSState) -> Dict[str, Any]:
        platform = state.get("platform", "threads")
        payload = state.get("content_payload", {})
        retries = state.get("qa_retries", 0)

        issues: List[str] = []
        score = 10.0

        # Check clichés
        text_content = str(payload.get("body", "") or payload.get("body_html", "") or payload.get("caption", ""))
        for cliche in BANNED_CLICHES:
            if cliche in text_content:
                issues.append(f"AI 상투어구 발견: '{cliche}'")
                score -= 2.0

        # Platform specific validations
        if platform == "threads":
            body = payload.get("body", "")
            if len(body) > 500:
                issues.append(f"Threads 500자 제한 초과 ({len(body)}자)")
                score -= 3.0
            if len(body) < 30:
                issues.append("내용이 너무 짧습니다 (최소 30자)")
                score -= 3.0

        elif platform == "instagram":
            slides = payload.get("slides", [])
            if len(slides) != 5:
                issues.append(f"Instagram 5장 슬라이드 미충족 (현재 {len(slides)}장)")
                score -= 4.0

        elif platform == "wordpress":
            html = payload.get("body_html", "")
            if "<h2>" not in html:
                issues.append("워드프레스 E-E-A-T 구조(H2 태그) 누락")
                score -= 3.0

        passed = (score >= 7.0 and len(issues) == 0)

        if not passed:
            logger.warning(f"[QAAgent] Content rejected (Score: {score:.1f}/10.0). Issues: {issues}")
            log_msg = f"[QAAgent] QA REJECTED (Score: {score:.1f}) - Issues: {', '.join(issues)}"
            return {
                "qa_results": {
                    "passed": False,
                    "score": score,
                    "issues": issues
                },
                "qa_retries": retries + 1,
                "logs": state.get("logs", []) + [log_msg]
            }

        logger.info(f"[QAAgent] Content passed QA audit with score {score:.1f}/10.0")
        log_msg = f"[QAAgent] QA PASSED (Score: {score:.1f}/10.0) - Zero defects detected"
        return {
            "qa_results": {
                "passed": True,
                "score": score,
                "issues": []
            },
            "logs": state.get("logs", []) + [log_msg]
        }
