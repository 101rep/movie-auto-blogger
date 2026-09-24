# -*- coding: utf-8 -*-
"""
Conversation Manager — 다중 턴 대화 세션 관리
사용자별 최근 10개 메시지 문맥을 Gemini contents 형식으로 반환.
"""

from typing import List, Dict
from agent.memory_db import agent_db


class ConversationManager:

    def get_session(self, user_id: str) -> str:
        return agent_db.get_or_create_session(user_id)

    def add_user_message(self, user_id: str, text: str):
        session_id = self.get_session(user_id)
        agent_db.add_message(session_id, "user", text)

    def add_model_message(self, user_id: str, text: str, tool_calls: list = None):
        session_id = self.get_session(user_id)
        agent_db.add_message(session_id, "model", text, tool_calls)

    def get_gemini_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Returns message history in Gemini contents format:
        [{"role": "user", "parts": [{"text": "..."}]}, ...]
        """
        session_id = self.get_session(user_id)
        messages = agent_db.get_recent_messages(session_id, limit)
        history = []
        for msg in messages:
            role = "model" if msg["role"] == "model" else "user"
            history.append({"role": role, "parts": [{"text": msg["content"]}]})
        return history

    def reset(self, user_id: str):
        agent_db.reset_session(user_id)

    def set_project_context(self, user_id: str, ctx: str):
        agent_db.set_pref(user_id, "project_ctx", ctx)

    def get_project_context(self, user_id: str) -> str:
        return agent_db.get_pref(user_id, "project_ctx", "")


conversation_manager = ConversationManager()
