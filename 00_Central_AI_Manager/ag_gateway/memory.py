import os
import sqlite3
from typing import Any, List, Tuple

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ag_memory.db"))

class MemoryStore:
    """Simple SQLite based memory store for persisting key-value data and task history.

    - `set(key, value)`: store a JSON-serializable value.
    - `get(key) -> Any`: retrieve the value or None.
    - `add_history(task_id: str, summary: str)`: record a task execution.
    - `get_history(limit: int = 10) -> List[Tuple[str, str]]`: recent entries.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS kv (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    summary TEXT,
                    ts DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def set(self, key: str, value: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def get(self, key: str) -> Any:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM kv WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def add_history(self, task_id: str, summary: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO history (task_id, summary) VALUES (?, ?)", (task_id, summary)
            )
            conn.commit()

    def get_history(self, limit: int = 10) -> List[Tuple[str, str]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT task_id, summary FROM history ORDER BY ts DESC LIMIT ?", (limit,)
            )
            return cur.fetchall()
