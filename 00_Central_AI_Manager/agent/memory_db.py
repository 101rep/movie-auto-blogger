# -*- coding: utf-8 -*-
"""
AG Command Center — Independent SQLite Memory Database
8-table schema for conversations, tasks, approvals, costs, and audit logs.
Completely separate from existing audit_log.db.
"""

import sqlite3
import json
import time
import hashlib
import secrets
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "ag_agent.db"


class AgentMemoryDB:
    """Centralized SQLite store for AG Command Center state."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _ensure_schema(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_ctx TEXT DEFAULT '',
                    created_at REAL NOT NULL,
                    last_active REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_calls_json TEXT DEFAULT '[]',
                    ts REAL NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES conversation_sessions(session_id)
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE,
                    status TEXT NOT NULL DEFAULT 'pending',
                    step TEXT DEFAULT '',
                    user_id TEXT NOT NULL,
                    tool_sequence TEXT DEFAULT '[]',
                    result TEXT DEFAULT '',
                    error TEXT DEFAULT '',
                    started_at REAL,
                    ended_at REAL,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tool_runs (
                    run_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    params_json TEXT DEFAULT '{}',
                    result_json TEXT DEFAULT '{}',
                    status TEXT NOT NULL DEFAULT 'pending',
                    ts REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    token TEXT NOT NULL UNIQUE,
                    nonce TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action_name TEXT NOT NULL,
                    action_hash TEXT NOT NULL,
                    params_json TEXT DEFAULT '{}',
                    description TEXT DEFAULT '',
                    level INTEGER DEFAULT 2,
                    target TEXT DEFAULT '',
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL,
                    consumed_at REAL DEFAULT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'SUCCESS',
                    detail_json TEXT DEFAULT '{}',
                    ts REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS preferences (
                    user_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (user_id, key)
                );

                CREATE TABLE IF NOT EXISTS usage_costs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    cost_usd REAL DEFAULT 0.0,
                    ts REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, ts);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, created_at);
                CREATE INDEX IF NOT EXISTS idx_approvals_token ON approvals(token);
                CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id, ts);
            """)

    # ── Conversation Sessions ─────────────────────────────────────────────────

    def get_or_create_session(self, user_id: str) -> str:
        now = time.time()
        with self._connect() as conn:
            # Active session within 2 hours
            row = conn.execute(
                "SELECT session_id FROM conversation_sessions WHERE user_id=? AND last_active > ? ORDER BY last_active DESC LIMIT 1",
                (user_id, now - 7200)
            ).fetchone()
            if row:
                conn.execute("UPDATE conversation_sessions SET last_active=? WHERE session_id=?", (now, row["session_id"]))
                return row["session_id"]
            session_id = f"sess_{user_id}_{int(now)}"
            conn.execute(
                "INSERT INTO conversation_sessions (session_id, user_id, created_at, last_active) VALUES (?,?,?,?)",
                (session_id, user_id, now, now)
            )
            return session_id

    def add_message(self, session_id: str, role: str, content: str, tool_calls: list = None):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, tool_calls_json, ts) VALUES (?,?,?,?,?)",
                (session_id, role, content, json.dumps(tool_calls or []), time.time())
            )

    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content, tool_calls_json, ts FROM messages WHERE session_id=? ORDER BY ts DESC LIMIT ?",
                (session_id, limit)
            ).fetchall()
        return [{"role": r["role"], "content": r["content"], "tool_calls": json.loads(r["tool_calls_json"]), "ts": r["ts"]} for r in reversed(rows)]

    def reset_session(self, user_id: str):
        """Start a fresh session by expiring existing ones."""
        with self._connect() as conn:
            conn.execute("UPDATE conversation_sessions SET last_active=0 WHERE user_id=?", (user_id,))

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def create_task(self, user_id: str, idempotency_key: str = None) -> str:
        task_id = f"task_{int(time.time())}_{secrets.token_hex(3)}"
        ikey = idempotency_key or task_id
        with self._connect() as conn:
            # Duplicate check
            existing = conn.execute("SELECT task_id FROM tasks WHERE idempotency_key=?", (ikey,)).fetchone()
            if existing:
                return existing["task_id"]
            conn.execute(
                "INSERT INTO tasks (task_id, idempotency_key, status, user_id, created_at) VALUES (?,?,?,?,?)",
                (task_id, ikey, "pending", user_id, time.time())
            )
        return task_id

    def update_task(self, task_id: str, status: str, step: str = "", result: str = "", error: str = ""):
        now = time.time()
        with self._connect() as conn:
            ended = now if status in ("done", "failed", "cancelled") else None
            conn.execute(
                "UPDATE tasks SET status=?, step=?, result=?, error=?, ended_at=? WHERE task_id=?",
                (status, step, result, error, ended, task_id)
            )

    def get_tasks(self, user_id: str = None, status: str = None, limit: int = 20) -> List[Dict]:
        sql = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if user_id:
            sql += " AND user_id=?"
            params.append(user_id)
        if status:
            sql += " AND status=?"
            params.append(status)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    # ── Approvals (DB persistent) ─────────────────────────────────────────────

    def create_approval(self, user_id: str, action_name: str, params: dict, description: str, level: int, ttl: int = 300, task_id: str = None) -> Tuple[str, str]:
        """Returns (approval_id, token)."""
        token = f"ag_{secrets.token_hex(6)}"
        nonce = secrets.token_hex(8)
        action_hash = hashlib.sha256(f"{action_name}{json.dumps(params, sort_keys=True)}{nonce}".encode()).hexdigest()[:16]
        approval_id = f"appr_{int(time.time())}_{secrets.token_hex(3)}"
        now = time.time()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO approvals
                   (approval_id, task_id, token, nonce, user_id, action_name, action_hash, params_json, description, level, expires_at, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (approval_id, task_id, token, nonce, user_id, action_name, action_hash, json.dumps(params), description, level, now + ttl, now)
            )
        return approval_id, token

    def consume_approval(self, token: str, user_id: str) -> Tuple[bool, Optional[Dict], str]:
        """Validate and consume a one-time approval token."""
        now = time.time()
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM approvals WHERE token=?", (token,)).fetchone()
            if not row:
                return False, None, "유효하지 않거나 이미 처리된 승인 요청입니다."
            item = dict(row)
            if item["consumed_at"] is not None:
                return False, None, "이미 사용된 승인 토큰입니다. 재사용 불가."
            if item["user_id"] != user_id:
                return False, None, "다른 사용자의 승인 토큰입니다."
            if now > item["expires_at"]:
                return False, None, "승인 유효 시간이 만료되었습니다. 다시 요청해 주세요."
            conn.execute("UPDATE approvals SET consumed_at=? WHERE token=?", (now, token))
            item["params"] = json.loads(item["params_json"])
            return True, item, "승인 성공"

    def cancel_approval(self, token: str, user_id: str) -> Tuple[bool, str]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM approvals WHERE token=? AND user_id=? AND consumed_at IS NULL", (token, user_id)).fetchone()
            if not row:
                return False, "취소할 수 없는 승인 요청입니다."
            conn.execute("UPDATE approvals SET consumed_at=-1 WHERE token=?", (token,))
            return True, f"요청 '{row['description']}' 취소됨"

    def get_pending_approvals(self, user_id: str) -> List[Dict]:
        now = time.time()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM approvals WHERE user_id=? AND consumed_at IS NULL AND expires_at > ? ORDER BY created_at DESC",
                (user_id, now)
            ).fetchall()
        return [dict(r) for r in rows]

    # ── Usage Costs ───────────────────────────────────────────────────────────

    def record_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int, task_id: str = None):
        # Approximate cost (Gemini flash pricing ~$0.075/1M input, $0.30/1M output)
        cost_map = {
            "gemini": {"input": 0.000000075, "output": 0.0000003},
            "openai": {"input": 0.00000015, "output": 0.0000006},
            "claude": {"input": 0.000003, "output": 0.000015},
            "grok": {"input": 0.000003, "output": 0.000015},
        }
        rates = cost_map.get(provider.lower().split("-")[0], {"input": 0.000001, "output": 0.000003})
        cost = input_tokens * rates["input"] + output_tokens * rates["output"]
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO usage_costs (task_id, provider, model, input_tokens, output_tokens, cost_usd, ts) VALUES (?,?,?,?,?,?,?)",
                (task_id, provider, model, input_tokens, output_tokens, cost, time.time())
            )

    def get_cost_summary(self, days: int = 30) -> Dict:
        since = time.time() - days * 86400
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT provider, model, SUM(input_tokens) as ti, SUM(output_tokens) as to_, SUM(cost_usd) as cost, COUNT(*) as calls FROM usage_costs WHERE ts > ? GROUP BY provider, model",
                (since,)
            ).fetchall()
            total = conn.execute("SELECT SUM(cost_usd) as total FROM usage_costs WHERE ts > ?", (since,)).fetchone()
        return {
            "by_provider": [dict(r) for r in rows],
            "total_usd": round((total["total"] or 0), 6),
            "period_days": days
        }

    # ── Preferences ───────────────────────────────────────────────────────────

    def set_pref(self, user_id: str, key: str, value: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO preferences (user_id, key, value, updated_at) VALUES (?,?,?,?)",
                (user_id, key, value, time.time())
            )

    def get_pref(self, user_id: str, key: str, default: str = None) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM preferences WHERE user_id=? AND key=?", (user_id, key)).fetchone()
        return row["value"] if row else default

    # ── Data Retention ────────────────────────────────────────────────────────

    def purge_old_data(self, days: int = 30):
        cutoff = time.time() - days * 86400
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE ts < ?", (cutoff,))
            conn.execute("DELETE FROM audit_logs WHERE ts < ?", (cutoff,))
            conn.execute("DELETE FROM usage_costs WHERE ts < ?", (cutoff,))
            conn.execute("DELETE FROM approvals WHERE expires_at < ? AND consumed_at IS NOT NULL", (cutoff,))

    # ── Audit Log ─────────────────────────────────────────────────────────────

    def log_audit(self, user_id: str, action: str, level: int, status: str, detail: dict = None):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_logs (user_id, action, level, status, detail_json, ts) VALUES (?,?,?,?,?,?)",
                (user_id, action, level, status, json.dumps(detail or {}), time.time())
            )


# Singleton
agent_db = AgentMemoryDB()
