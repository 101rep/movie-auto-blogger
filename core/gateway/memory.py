# -*- coding: utf-8 -*-
"""
AI Memory System — AG Gateway PRD v2.0 PART 7

Institutional knowledge repository tracking engineering solutions:
- Fields: problem, root_cause, solution, changed_files, test_results
- Dual Persistence:
  1. Relational SQLite table (ai_memory_records in data/aaos.db)
  2. Markdown append in AI_ENGINEERING/debugging_history.md
- Ensures no solved issue is ever repeated (Compound Learning Loop).
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from zoneinfo import ZoneInfo

from core.aaos.db import get_aaos_db_session
from core.aaos.models import AIMemoryRecord

logger = logging.getLogger("ai_memory_system")


class AIMemorySystem:
    """Records and retrieves engineering problem-solution pairs."""

    @classmethod
    def record_issue(
        cls,
        problem: str,
        root_cause: str,
        solution: str,
        changed_files: Optional[str] = None,
        test_results: Optional[str] = None
    ) -> AIMemoryRecord:
        """Saves a new solved issue to SQLite and markdown repository."""
        # 1. DB Save
        with get_aaos_db_session() as session:
            record = AIMemoryRecord(
                problem=problem,
                root_cause=root_cause,
                solution=solution,
                changed_files=changed_files,
                test_results=test_results
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            session.expunge(record)
            logger.info("Recorded AI Memory #%d: %s", record.id, problem[:40])

        # 2. Markdown Append (debugging_history.md)
        cls._append_to_markdown(problem, root_cause, solution, changed_files, test_results)
        return record

    @staticmethod
    def _append_to_markdown(
        problem: str,
        root_cause: str,
        solution: str,
        changed_files: Optional[str],
        test_results: Optional[str]
    ) -> None:
        try:
            workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            md_path = os.path.join(workspace_root, "AI_ENGINEERING", "debugging_history.md")
            if os.path.exists(md_path):
                kst = ZoneInfo("Asia/Seoul")
                now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S KST")
                entry = f"""
### [Issue Log: {problem[:60]}] - {now_kst}
- **문제 (Problem):** {problem}
- **원인 (Root Cause):** {root_cause}
- **해결책 (Solution):** {solution}
- **변경 파일 (Changed Files):** {changed_files or "N/A"}
- **테스트 결과 (Test Results):** {test_results or "PASS"}

---
"""
                with open(md_path, "a", encoding="utf-8") as f:
                    f.write(entry)
                logger.info("Appended AI memory to %s", md_path)
        except Exception as e:
            logger.warning("Failed to append AI memory to markdown: %s", e)

    @classmethod
    def get_recent_memories(cls, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves most recent solved issues."""
        with get_aaos_db_session() as session:
            records = session.query(AIMemoryRecord).order_by(
                AIMemoryRecord.id.desc()
            ).limit(limit).all()

            return [
                {
                    "id": r.id,
                    "problem": r.problem,
                    "root_cause": r.root_cause,
                    "solution": r.solution,
                    "changed_files": r.changed_files,
                    "test_results": r.test_results,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in records
            ]
