# -*- coding: utf-8 -*-
"""
Google Gemini AI Provider Adapter
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from config import settings
from ai.interfaces import BaseAIProvider

logger = logging.getLogger("GeminiProvider")

class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, default_model: str = "gemini-3.6-flash"):
        self.api_key = api_key or getattr(settings, "GEMINI_API_KEY", "")
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        mdl = model or self.default_model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={self.api_key}"
        
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        body: Dict[str, Any] = {"contents": contents}
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=body)
            if resp.status_code != 200:
                logger.error(f"Gemini API error {resp.status_code}: {resp.text[:200]}")
                return f"[Gemini Error {resp.status_code}]"
            data = resp.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                logger.error(f"Gemini parse error: {e}")
                return "[Gemini 응답 파싱 실패]"

    async def call_tool(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        mdl = model or self.default_model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={self.api_key}"
        
        body: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "tools": [{"functionDeclarations": tools}]
        }
        if system_instruction:
            body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=body)
            if resp.status_code != 200:
                logger.error(f"Gemini call_tool error {resp.status_code}: {resp.text[:200]}")
                return {"tool_called": False, "response_text": f"API Error {resp.status_code}"}
                
            data = resp.json()
            try:
                candidate = data["candidates"][0]
                parts = candidate["content"]["parts"]
                for part in parts:
                    if "functionCall" in part:
                        fc = part["functionCall"]
                        return {
                            "tool_called": True,
                            "tool_name": fc.get("name"),
                            "tool_args": fc.get("args", {}),
                            "response_text": None
                        }
                    elif "text" in part:
                        return {
                            "tool_called": False,
                            "tool_name": None,
                            "tool_args": {},
                            "response_text": part["text"]
                        }
            except Exception as e:
                logger.error(f"Gemini response parsing error: {e}")
                
        return {"tool_called": False, "response_text": "도구 호출 파싱 불가"}
