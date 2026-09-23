import os
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from nexus_command.config import nexus_settings
from nexus_command.models import ChatMessage, SessionContext, MessageType, ActionCard

class SessionManager:
    """Manages multi-turn conversational context, message persistence, and target entity resolution."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or nexus_settings.DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._contexts: Dict[str, SessionContext] = {}
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT DEFAULT '새 대화',
                    last_context_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    msg_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    card_data_json TEXT,
                    risk_level INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

    def get_or_create_context(self, session_id: str, user_id: str = "owner") -> SessionContext:
        if session_id in self._contexts:
            return self._contexts[session_id]

        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
            if row:
                ctx_dict = json.loads(row["last_context_json"]) if row["last_context_json"] else {}
                ctx = SessionContext(
                    session_id=session_id,
                    user_id=row["user_id"],
                    active_target_asset_id=ctx_dict.get("active_target_asset_id"),
                    active_target_name=ctx_dict.get("active_target_name"),
                    active_error_context=ctx_dict.get("active_error_context"),
                    recent_intents=ctx_dict.get("recent_intents", []),
                    recent_tools=ctx_dict.get("recent_tools", []),
                    metadata=ctx_dict.get("metadata", {})
                )
            else:
                ctx = SessionContext(session_id=session_id, user_id=user_id)
                conn.execute(
                    "INSERT INTO sessions (session_id, user_id, last_context_json) VALUES (?, ?, ?)",
                    (session_id, user_id, json.dumps(ctx.model_dump()))
                )
                conn.commit()

            self._contexts[session_id] = ctx
            return ctx

    def update_context(self, session_id: str, **kwargs: Any) -> SessionContext:
        ctx = self.get_or_create_context(session_id)
        for k, v in kwargs.items():
            if hasattr(ctx, k):
                setattr(ctx, k, v)
        ctx.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET last_context_json = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
                (json.dumps(ctx.model_dump()), session_id)
            )
            conn.commit()
        return ctx

    def add_message(self, message: ChatMessage) -> ChatMessage:
        with self._get_connection() as conn:
            card_json = json.dumps(message.card.model_dump()) if message.card else None
            cursor = conn.execute(
                """
                INSERT INTO messages (session_id, sender, msg_type, content, card_data_json, risk_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.session_id,
                    message.sender,
                    message.msg_type.value if hasattr(message.msg_type, "value") else str(message.msg_type),
                    message.content,
                    card_json,
                    message.risk_level.value if hasattr(message.risk_level, "value") else int(message.risk_level),
                    message.created_at
                )
            )
            message.id = cursor.lastrowid
            conn.commit()
        return message

    def get_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        messages = []
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?",
                (session_id, limit)
            ).fetchall()
            for r in rows:
                card = ActionCard(**json.loads(r["card_data_json"])) if r["card_data_json"] else None
                messages.append(ChatMessage(
                    id=r["id"],
                    session_id=r["session_id"],
                    sender=r["sender"],
                    msg_type=MessageType(r["msg_type"]),
                    content=r["content"],
                    card=card,
                    risk_level=r["risk_level"],
                    created_at=str(r["created_at"])
                ))
        return messages

session_manager = SessionManager()
