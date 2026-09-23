import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import settings

class AuditLogger:
    """Records all control actions, security evaluations, and execution results into SQLite."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or settings.AUDIT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                action TEXT,
                level INTEGER,
                status TEXT,
                details TEXT,
                execution_time_ms INTEGER
            )
            """)
            conn.commit()

    def log(
        self,
        user_id: str | int,
        action: str,
        level: int,
        status: str,
        details: Any = None,
        execution_time_ms: int = 0
    ) -> None:
        details_str = json.dumps(details, ensure_ascii=False) if isinstance(details, (dict, list)) else str(details or "")
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, level, status, details, execution_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (str(user_id), action, level, status, details_str, execution_time_ms)
                )
                conn.commit()
        except Exception as e:
            print(f"[AuditLogger Error] Failed to write log: {e}")

    def get_recent_logs(self, limit: int = 15) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, timestamp, user_id, action, level, status, details, execution_time_ms FROM audit_logs ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

audit_logger = AuditLogger()
