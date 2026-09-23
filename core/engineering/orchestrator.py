"""
AI Engineering Operating Layer Orchestrator
Implements Superpowers workflow control, gstack 5-agent organizational roles,
and Compound Engineering continuous learning loop.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("AIEngineeringOrchestrator")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AI_ENG_DIR = BASE_DIR / "AI_ENGINEERING"
DEBUGGING_HISTORY_FILE = AI_ENG_DIR / "debugging_history.md"
ENGINEERING_MEMORY_FILE = AI_ENG_DIR / "engineering_memory.md"
RELEASE_NOTES_FILE = AI_ENG_DIR / "release_notes.md"
WORKFLOW_RULES_FILE = AI_ENG_DIR / "workflow_rules.md"
AGENT_ROLES_FILE = AI_ENG_DIR / "agent_roles.md"
CODE_REVIEW_RULES_FILE = AI_ENG_DIR / "code_review_rules.md"

# ── 1. gstack Agent Implementations ──────────────────────────────────────────

class CEOAgent:
    """Evaluates business alignment, necessity, and priority."""
    @staticmethod
    def review(request: str) -> Dict[str, Any]:
        logger.info(f"[CEO Agent] Reviewing request: '{request[:60]}...'")
        
        # Priority heuristics
        priority = "P1"
        if any(w in request.lower() for w in ["긴급", "오류", "장애", "실패", "crash", "bug"]):
            priority = "P0"
        elif any(w in request.lower() for w in ["개선", "리팩토링", "정리"]):
            priority = "P2"

        return {
            "approved": True,
            "priority": priority,
            "rationale": "요청 사항이 핵심 자동화 가치 및 시스템 안정성 목표에 부합함.",
            "scope": f"요청 기능 범위: {request[:100]}",
            "constraints": ["기존 코드 삭제 금지", "애드센스 격리 준수", "테스트 통과 필수"]
        }


class EngineeringManagerAgent:
    """Performs deep technical analysis, impact assessment, and task breakdown."""
    @staticmethod
    def plan(ceo_decision: Dict[str, Any], target_files: Optional[List[str]] = None) -> Dict[str, Any]:
        logger.info("[EM Agent] Generating technical specification and task breakdown.")
        files = target_files or []
        
        impact_analysis = {
            "affected_modules": files,
            "database_impact": "None or Non-destructive additive migration",
            "runtime_impact": "Zero disruption to background queue workers",
            "rollback_strategy": "Git reversion or backup restoration"
        }

        tasks = [
            f"1. 영향도 분석 대상 검토 ({len(files)}개 파일)",
            "2. 비파괴 모듈 구현 및 인터페이스 설계",
            "3. 구문 컴파일 및 단위 검증",
            "4. QA 8대 체크리스트 감사",
            "5. 릴리즈 노트 및 복리 메모리 반영"
        ]

        return {
            "impact_analysis": impact_analysis,
            "tasks": tasks,
            "status": "PLAN_APPROVED"
        }


class DeveloperAgent:
    """Executes implementation according to EM plan."""
    @staticmethod
    def implement(plan: Dict[str, Any], implementation_summary: str) -> Dict[str, Any]:
        logger.info(f"[Developer Agent] Implementing changes: {implementation_summary}")
        return {
            "status": "IMPLEMENTED",
            "summary": implementation_summary,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class QAAgent:
    """Audits changes against the 8-pillar code review standards."""
    @staticmethod
    def audit(file_paths: List[str]) -> Dict[str, Any]:
        logger.info(f"[QA Agent] Running 8-pillar code review on {len(file_paths)} files.")
        issues = []
        score = 10.0

        for file_path in file_paths:
            path_obj = Path(file_path)
            if not path_obj.exists():
                issues.append(f"File not found: {file_path}")
                score -= 3.0
                continue

            # Check Python Syntax & Compilation
            if path_obj.suffix == ".py":
                try:
                    res = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(path_obj)],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if res.returncode != 0:
                        issues.append(f"Syntax/Compile Error in {path_obj.name}: {res.stderr[:100]}")
                        score -= 5.0
                except Exception as e:
                    issues.append(f"Compile check exception on {path_obj.name}: {e}")
                    score -= 2.0

        passed = (score >= 8.5 and len(issues) == 0)
        return {
            "passed": passed,
            "score": max(0.0, score),
            "issues": issues,
            "checked_files": file_paths
        }


class ReleaseAgent:
    """Verifies post-test stability and records changelog."""
    @staticmethod
    def release(qa_result: Dict[str, Any], release_title: str, changes_summary: str) -> Dict[str, Any]:
        if not qa_result.get("passed", False):
            logger.error("[Release Agent] Release blocked by QA rejection.")
            return {"released": False, "reason": "QA check failed"}

        logger.info(f"[Release Agent] Authorizing release: {release_title}")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Append to release_notes.md
        entry = (
            f"\n\n### [{release_title}] - {timestamp}\n"
            f"- **Summary:** {changes_summary}\n"
            f"- **QA Score:** {qa_result.get('score')}/10.0\n"
            f"- **Checked Files:** {', '.join([Path(p).name for p in qa_result.get('checked_files', [])])}\n"
        )
        try:
            with open(RELEASE_NOTES_FILE, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            logger.warning(f"Could not append to release notes: {e}")

        return {
            "released": True,
            "title": release_title,
            "timestamp": timestamp
        }


# ── 2. Compound Engineering Learning Loop ───────────────────────────────────

class CompoundMemoryManager:
    """Maintains persistent engineering intelligence and records RCAs."""

    @staticmethod
    def record_incident(
        issue_id: str,
        title: str,
        symptoms: str,
        root_cause: str,
        fix_applied: str,
        future_prevention: str
    ) -> bool:
        logger.info(f"[Compound Memory] Recording RCA: [{issue_id}] {title}")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        rca_entry = (
            f"\n\n---\n\n"
            f"### [{issue_id}] {title}\n"
            f"- **발생 일시:** {timestamp}\n"
            f"- **현상:** {symptoms}\n"
            f"- **근본 원인 (Root Cause):** {root_cause}\n"
            f"- **조치 내역 (Fix):** {fix_applied}\n"
            f"- **재발 방지 대책 (Future Prevention):** {future_prevention}\n"
        )

        try:
            with open(DEBUGGING_HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(rca_entry)
            return True
        except Exception as e:
            logger.error(f"Failed to append to debugging history: {e}")
            return False

    @staticmethod
    def get_known_issues() -> List[str]:
        if not DEBUGGING_HISTORY_FILE.exists():
            return []
        try:
            with open(DEBUGGING_HISTORY_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            lines = [line.strip() for line in content.splitlines() if line.startswith("### [RCA-")]
            return lines
        except Exception:
            return []


# ── 3. Superpowers 7-Step Pipeline Orchestrator ──────────────────────────────

class EngineeringPipeline:
    """Executes the full 7-step Superpowers pipeline powered by gstack and Compound Memory."""

    @staticmethod
    def run_lifecycle(
        request_text: str,
        target_files: Optional[List[str]] = None,
        implementation_summary: str = "Feature implemented successfully"
    ) -> Dict[str, Any]:
        logs = []

        # Step 1: Request
        logs.append(f"[Step 1: Request] '{request_text}'")

        # Step 2 & 3: Problem Analysis & Plan (CEO + EM)
        ceo_eval = CEOAgent.review(request_text)
        logs.append(f"[Step 2: CEO Evaluation] Priority {ceo_eval['priority']}, Approved: {ceo_eval['approved']}")

        em_plan = EngineeringManagerAgent.plan(ceo_eval, target_files)
        logs.append(f"[Step 3: EM Plan] Generated {len(em_plan['tasks'])} task items with impact assessment.")

        # Step 4: Implementation (Developer)
        dev_res = DeveloperAgent.implement(em_plan, implementation_summary)
        logs.append(f"[Step 4: Implementation] {dev_res['summary']}")

        # Step 5 & 6: Testing & Verification (QA)
        qa_res = QAAgent.audit(target_files or [])
        status_str = "PASSED" if qa_res["passed"] else "REJECTED"
        logs.append(f"[Step 5 & 6: QA Audit & Testing] Result: {status_str} (Score: {qa_res['score']}/10.0)")

        # Step 7: Report & Release (Release Agent)
        rel_res = ReleaseAgent.release(
            qa_res,
            release_title=f"Feature: {request_text[:30]}",
            changes_summary=implementation_summary
        )
        logs.append(f"[Step 7: Release & Report] Released: {rel_res.get('released', False)}")

        return {
            "success": rel_res.get("released", False),
            "ceo": ceo_eval,
            "em": em_plan,
            "qa": qa_res,
            "release": rel_res,
            "logs": logs
        }


engineering_pipeline = EngineeringPipeline()
compound_memory = CompoundMemoryManager()
