# -*- coding: utf-8 -*-
"""
Multi-LLM Router MCP Tool Implementations
Exposes task-based LLM generation and routing metadata to MCP Gateway:
  - execute_llm_task(task_type, prompt, system_instruction)
  - get_llm_routes()
"""

import logging
from typing import Dict, Any, Optional
from mcp_server.auth import auth_guard, PermissionLevel
from ai.multi_llm_router import multi_llm_router

logger = logging.getLogger("LLMTools")


async def route_and_execute_task(
    task_type: str,
    prompt: str,
    system_instruction: str = "",
    model: str = "",
    auth_token: str = ""
) -> Dict[str, Any]:
    """
    작업 유형(task_type: content, chat, code, experimental)에 따라
    Gemini, GPT, Claude, Grok 중 최적의 모델을 자동 선택하여 실행합니다.
    """
    guard = auth_guard.enforce_guard("execute_llm_task", PermissionLevel.READ, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    if not prompt or not prompt.strip():
        return {"status": "ERROR", "message": "prompt 파라미터가 비어있습니다."}

    logger.info(f"🧠 [MCP LLM Router] Executing task '{task_type}'...")
    res = await multi_llm_router.execute_task(
        task_type=task_type,
        prompt=prompt,
        system_instruction=system_instruction if system_instruction else None,
        model=model if model else None
    )
    return res


async def get_llm_routes(auth_token: str = "") -> Dict[str, Any]:
    """
    현재 Multi-LLM Router의 작업 유형별 매핑(Gemini/GPT/Claude/Grok) 및 가용 모델 정보를 반환합니다.
    """
    guard = auth_guard.enforce_guard("llm_routing_status", PermissionLevel.READ, auth_token if auth_token else None)
    if guard.get("status") != "ALLOWED":
        return guard

    return multi_llm_router.get_routing_info()
