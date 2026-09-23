# -*- coding: utf-8 -*-
"""
Anthropic Claude AI Provider Adapter (via OpenAI-Compatible / Synterolink or Direct API)
Supports models like claude-sonnet-4-5, claude-opus-4-6, claude-haiku-4-5
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from ai.interfaces import BaseAIProvider

logger = logging.getLogger("ClaudeProvider")

class ClaudeProvider(BaseAIProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None
    ):
        self.api_key = (
            api_key
            or os.getenv("CLAUDE_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
        ).strip()

        raw_base = (
            base_url
            or os.getenv("CLAUDE_BASE_URL")
            or os.getenv("OPENAI_COMPATIBLE_BASE_URL")
            or "https://api.synterolink.com/v1"
        ).rstrip("/")

        if not raw_base.endswith("/chat/completions"):
            self.endpoint_url = f"{raw_base}/chat/completions"
        else:
            self.endpoint_url = raw_base

        self.default_model = (
            default_model
            or os.getenv("CLAUDE_DEFAULT_MODEL")
            or "claude-sonnet-4-5"
        )

    @property
    def provider_name(self) -> str:
        return "claude"

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        if not self.api_key:
            return "[Claude API Key 미설정 (.env의 CLAUDE_API_KEY 확인 필요)]"

        mdl = model or self.default_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": mdl,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", self.endpoint_url, headers=headers, json=body) as resp:
                    if resp.status_code != 200:
                        logger.error(f"Claude API error {resp.status_code}")
                        return f"[Claude Error {resp.status_code}]"

                    chunks = []
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        if line.startswith("data:"):
                            data_str = line[5:].strip()
                            if "[DONE]" in data_str:
                                break
                            try:
                                j = json.loads(data_str)
                                delta = j.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if delta:
                                    chunks.append(delta)
                            except Exception:
                                pass
                    return "".join(chunks)
        except Exception as e:
            logger.error(f"Claude streaming error, fallback: {e}")
            body["stream"] = False
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self.endpoint_url, headers=headers, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                return f"[Claude Error {resp.status_code}]"

    async def call_tool(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"tool_called": False, "response_text": "[Claude API Key 미설정]"}

        mdl = model or self.default_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        openai_tools = []
        for t in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t.get("name"),
                    "description": t.get("description", ""),
                    "parameters": t.get("parameters", {"type": "object", "properties": {}})
                }
            })

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        body = {
            "model": mdl,
            "messages": messages,
            "tools": openai_tools,
            "tool_choice": "auto"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.endpoint_url, headers=headers, json=body)
            if resp.status_code != 200:
                logger.error(f"Claude Tool error {resp.status_code}: {resp.text[:200]}")
                return {"tool_called": False, "response_text": f"Claude Error {resp.status_code}"}

            data = resp.json()
            choice = data["choices"][0]["message"]
            if choice.get("tool_calls"):
                tc = choice["tool_calls"][0]["function"]
                try:
                    args = json.loads(tc.get("arguments", "{}"))
                except Exception:
                    args = {}
                return {
                    "tool_called": True,
                    "tool_name": tc.get("name"),
                    "tool_args": args,
                    "response_text": None
                }
            return {
                "tool_called": False,
                "tool_name": None,
                "tool_args": {},
                "response_text": choice.get("content", "")
            }
