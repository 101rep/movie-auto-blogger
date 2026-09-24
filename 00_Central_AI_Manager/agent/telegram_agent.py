# -*- coding: utf-8 -*-
"""
AG Telegram Agent — 다중 턴 Gemini Agent
- 이전 대화 문맥을 포함하여 Gemini API 호출
- 허용 Tool 화이트리스트로 프롬프트 인젝션 방어
- L1~L5 권한 분류 기반 도구 실행 또는 승인 요청
- 비용(토큰) 기록
"""

import httpx
import json
import logging
from typing import Tuple, Optional, Dict, Any, List

from config import settings
from agent.conversation_manager import conversation_manager
from agent.memory_db import agent_db
from router.gemini_tools import GEMINI_FUNCTION_DECLARATIONS, execute_tool_call
from security.permission import permission_engine

logger = logging.getLogger("telegram_agent")

# ── Tool 화이트리스트 (Prompt Injection 방어) ─────────────────────────────────
ALLOWED_TOOLS: set = {t["name"] for t in GEMINI_FUNCTION_DECLARATIONS}

# ── 시스템 인스트럭션 ────────────────────────────────────────────────────────
SYSTEM_INSTRUCTION = (
    "당신은 사장님(단독 관리자)의 'AG Command Center' 개인 AI 관제 비서입니다. "
    "Cloudways 리눅스 서버(139.59.125.237), 8대 워드프레스 블로그, "
    "Threads x 쿠팡 파트너스 자동화, ItemPick24 상품 블로그를 총괄합니다.\n\n"
    "규칙:\n"
    "1. 제공된 도구(Tools)만 사용하세요. 허용되지 않은 도구 이름은 절대 호출하지 마세요.\n"
    "2. 민감한 API 키, 비밀번호, 인증 토큰은 절대 응답에 포함하지 마세요.\n"
    "3. 이전 대화 맥락(블로그 번호, 날짜, 승인 대상 등)을 정확히 이어받으세요.\n"
    "4. 불명확한 대상(어떤 블로그? 어느 계정?)은 확인 질문 후 실행하세요.\n"
    "5. 한국어 경어체로 답변하되 텔레그램 HTML 태그(<b>, <code>, <i>)를 활용하세요.\n"
    "6. 도구 호출 성공과 실제 발행/실행 성공을 구분하여 보고하세요.\n"
    "7. 실패한 작업은 숨기지 말고 원인과 해결 방안을 제시하세요.\n"
    "8. 영화 블로그나 워드프레스 블로그의 중복 글 검사/삭제 요청이 오면 반드시 manage_blog_posts 도구를 호출하세요.\n"
    "9. 블로그 글의 '내용이 없다', '내용 채워줘', '글 수정해줘', '본문 보완해줘', '글 다시 써줘'라는 요청이 오면, "
    "절대 포스터만 수정하는 fix_blog_post_poster를 호출하지 말고, 반드시 repair_blog_post_content 도구를 호출하여 "
    "워드프레스 본문 전체를 풍부한 E-E-A-T 고품질 콘텐츠로 실제 즉시 수정·업데이트하세요. "
    "오직 단순 포스터 누락 교체 요청일 때만 fix_blog_post_poster를 호출하세요."
)


import dataclasses

def sanitize_for_json(obj: Any) -> Any:
    """Recursively sanitize complex objects (dataclasses, Enums, datetimes, Pydantic models) for JSON serialization."""
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(item) for item in obj]
    elif dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return sanitize_for_json(dataclasses.asdict(obj))
    elif hasattr(obj, "value"):  # Enums (e.g. ProgramStatus)
        return obj.value
    elif hasattr(obj, "isoformat"):  # datetime / date
        return obj.isoformat()
    elif hasattr(obj, "model_dump"):  # Pydantic v2
        return sanitize_for_json(obj.model_dump())
    elif hasattr(obj, "__dict__"):
        return sanitize_for_json(obj.__dict__)
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)


class TelegramAgent:
    """Multi-turn Gemini Agent with context memory, tool whitelist, and cost tracking."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def _build_tools_payload(self) -> List[Dict]:
        return [
            {
                "function_declarations": [
                    {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                k: {
                                    "type": v.get("type", "string").lower(),
                                    "description": v.get("description", "")
                                }
                                for k, v in tool.get("parameters", {}).get("properties", {}).items()
                            },
                            "required": tool.get("parameters", {}).get("required", [])
                        }
                    }
                    for tool in GEMINI_FUNCTION_DECLARATIONS
                ]
            }
        ]

    async def respond(self, user_id: str, prompt: str) -> Tuple[str, Optional[Dict]]:
        """
        Main entry: process user message with full conversation context.
        Returns (response_text, optional_reply_markup).
        """
        # Store user message
        conversation_manager.add_user_message(user_id, prompt)

        # Build Gemini history (last 10 messages)
        history = conversation_manager.get_gemini_history(user_id, limit=10)

        # Ensure history ends with user message (last item should be current prompt)
        # The conversation manager already added the message, so history includes it
        if not history or history[-1].get("role") != "user":
            history.append({"role": "user", "parts": [{"text": prompt}]})

        task_id = agent_db.create_task(user_id, idempotency_key=None)
        tools_payload = self._build_tools_payload()

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                contents = list(history)  # copy

                for turn in range(5):  # max 5 agentic turns
                    payload = {
                        "contents": contents,
                        "tools": tools_payload,
                        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]}
                    }

                    resp = await client.post(
                        f"{self.base_url}?key={self.api_key}",
                        json=sanitize_for_json(payload)
                    )

                    if resp.status_code != 200:
                        err = f"Gemini API 오류 (HTTP {resp.status_code}): {resp.text[:300]}"
                        agent_db.update_task(task_id, "failed", error=err)
                        return f"⚠️ {err}", None

                    res_json = resp.json()

                    # Track token usage
                    usage = res_json.get("usageMetadata", {})
                    if usage:
                        agent_db.record_cost(
                            provider="gemini",
                            model=self.model,
                            input_tokens=usage.get("promptTokenCount", 0),
                            output_tokens=usage.get("candidatesTokenCount", 0),
                            task_id=task_id
                        )

                    candidates = res_json.get("candidates", [])
                    if not candidates:
                        return "답변을 생성하지 못했습니다.", None

                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])

                    function_calls = [p["functionCall"] for p in parts if "functionCall" in p]

                    # No tool calls → final text response
                    if not function_calls:
                        final_text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
                        if final_text:
                            conversation_manager.add_model_message(user_id, final_text)
                        agent_db.update_task(task_id, "done", result=final_text[:500])
                        return final_text or "작업이 완료되었습니다.", None

                    # Append model's tool request to history
                    contents.append({"role": "model", "parts": parts})

                    # Process each tool call
                    function_response_parts = []
                    for fc in function_calls:
                        tool_name = fc.get("name", "")
                        tool_args = fc.get("args", {})

                        # ── Whitelist check (Prompt Injection Defense) ──
                        if tool_name not in ALLOWED_TOOLS:
                            logger.warning(f"[Security] Blocked unknown tool: {tool_name}")
                            function_response_parts.append({
                                "functionResponse": {
                                    "name": tool_name,
                                    "response": {"error": f"도구 '{tool_name}'은 허용되지 않습니다."}
                                }
                            })
                            continue

                        # ── Permission check ──
                        allowed, reason, level = permission_engine.check_execution_permission(user_id, tool_name, tool_args)

                        if not allowed:
                            # Create DB-persisted approval request
                            approval_id, token = agent_db.create_approval(
                                user_id=user_id,
                                action_name=tool_name,
                                params=tool_args,
                                description=f"AI 요청: {tool_name}",
                                level=int(level),
                                task_id=task_id
                            )
                            level_icon = "⚠️" if int(level) == 3 else "🚨"
                            msg = (
                                f"{level_icon} <b>[보안 승인 요청 - Level {int(level)}]</b>\n\n"
                                f"• <b>작업</b>: <code>{tool_name}</code>\n"
                                f"• <b>설정</b>: <code>{json.dumps(tool_args, ensure_ascii=False)[:100]}</code>\n"
                                f"• <b>승인 유효 시간</b>: 5분\n\n"
                                f"위 작업을 승인하시겠습니까?"
                            )
                            markup = {
                                "inline_keyboard": [[
                                    {"text": "✅ 승인", "callback_data": f"confirm:{token}"},
                                    {"text": "❌ 취소", "callback_data": f"cancel:{token}"}
                                ]]
                            }
                            agent_db.update_task(task_id, "awaiting_approval")
                            return msg, markup

                        # ── Execute tool ──
                        agent_db.log_audit(user_id, tool_name, int(level), "EXECUTING", tool_args)
                        tool_result = await execute_tool_call(tool_name, tool_args, user_id)
                        agent_db.log_audit(user_id, tool_name, int(level), tool_result.get("status", "DONE"), {"result": str(tool_result)[:300]})

                        function_response_parts.append({
                            "functionResponse": {
                                "name": tool_name,
                                "response": {"result": sanitize_for_json(tool_result)}
                            }
                        })

                    contents.append({"role": "user", "parts": function_response_parts})

                # Max turns reached
                agent_db.update_task(task_id, "done", result="max_turns")
                return "작업 처리가 완료되었습니다.", None

            except Exception as e:
                logger.exception(f"[TelegramAgent] Error: {e}")
                agent_db.update_task(task_id, "failed", error=str(e))
                return f"⚠️ AI 처리 중 오류: {e}", None


telegram_agent = TelegramAgent()
