# -*- coding: utf-8 -*-
"""
Antigravity Multi-LLM Role Router
Routes tasks to optimal AI providers based on operational domain:
  - 콘텐츠 생성 (Content Creation / Blog) -> Google Gemini (gemini-3.6-flash)
  - 대화 및 메신저 (Conversation / Chat)  -> OpenAI GPT (gpt-4o / gpt-4o-mini)
  - 코드 분석 및 운영 (Code Analysis / Ops) -> Anthropic Claude (claude-sonnet-4-5)
  - 실험 콘텐츠 및 트렌드 (Experimental / Trend) -> xAI Grok (grok-4.5)
"""

import os
import logging
from typing import Dict, Any, List, Optional
from ai.interfaces import BaseAIProvider
from ai.providers.gemini_provider import GeminiProvider
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.claude_provider import ClaudeProvider
from ai.providers.grok_provider import GrokProvider
from ai.providers.openai_compatible_provider import OpenAICompatibleProvider

logger = logging.getLogger("MultiLLMRouter")


class TaskCategory:
    CONTENT = "content_creation"
    CONVERSATION = "conversation"
    CODE_OPS = "code_analysis"
    EXPERIMENTAL = "experimental"


# Task Alias Normalization Map
TASK_ALIAS_MAP = {
    # 1. 콘텐츠 생성 -> Gemini
    "content": TaskCategory.CONTENT,
    "content_creation": TaskCategory.CONTENT,
    "blog": TaskCategory.CONTENT,
    "writing": TaskCategory.CONTENT,
    "article": TaskCategory.CONTENT,
    "post": TaskCategory.CONTENT,
    "welfare": TaskCategory.CONTENT,
    "travel": TaskCategory.CONTENT,
    "movie": TaskCategory.CONTENT,

    # 2. 대화 및 메신저 -> GPT
    "chat": TaskCategory.CONVERSATION,
    "conversation": TaskCategory.CONVERSATION,
    "dialogue": TaskCategory.CONVERSATION,
    "messenger": TaskCategory.CONVERSATION,
    "telegram": TaskCategory.CONVERSATION,
    "support": TaskCategory.CONVERSATION,
    "user_qa": TaskCategory.CONVERSATION,

    # 3. 코드 분석 및 운영 -> Claude
    "code": TaskCategory.CODE_OPS,
    "code_analysis": TaskCategory.CODE_OPS,
    "ops": TaskCategory.CODE_OPS,
    "debug": TaskCategory.CODE_OPS,
    "server": TaskCategory.CODE_OPS,
    "architecture": TaskCategory.CODE_OPS,
    "refactor": TaskCategory.CODE_OPS,
    "system_ops": TaskCategory.CODE_OPS,

    # 4. 실험 콘텐츠 및 트렌드 -> Grok
    "experimental": TaskCategory.EXPERIMENTAL,
    "experiment": TaskCategory.EXPERIMENTAL,
    "trend": TaskCategory.EXPERIMENTAL,
    "viral": TaskCategory.EXPERIMENTAL,
    "realtime": TaskCategory.EXPERIMENTAL,
    "creative_experiment": TaskCategory.EXPERIMENTAL,
    "humor": TaskCategory.EXPERIMENTAL,
    "meme": TaskCategory.EXPERIMENTAL,
}


class MultiLLMRouter:
    def __init__(self):
        self.gemini = GeminiProvider()
        self.openai = OpenAIProvider()
        self.claude = ClaudeProvider()
        self.grok = GrokProvider()
        self.openai_compatible = OpenAICompatibleProvider()

        # Task -> Provider Mapping
        self._route_table: Dict[str, BaseAIProvider] = {
            TaskCategory.CONTENT: self.gemini,
            TaskCategory.CONVERSATION: self.openai,
            TaskCategory.CODE_OPS: self.claude,
            TaskCategory.EXPERIMENTAL: self.grok,
        }

    def resolve_task_category(self, task_type: str) -> str:
        """Normalizes task input into a standard TaskCategory."""
        normalized = (task_type or "").strip().lower()
        return TASK_ALIAS_MAP.get(normalized, TaskCategory.CONTENT)

    def get_provider(self, task_type: str) -> BaseAIProvider:
        """Returns the assigned AI provider for the given task type."""
        category = self.resolve_task_category(task_type)
        return self._route_table.get(category, self.gemini)

    def get_routing_info(self) -> Dict[str, Any]:
        """Returns metadata about the active routing table and provider configurations."""
        return {
            "status": "ONLINE",
            "routes": {
                "콘텐츠 생성 (Content Creation)": {
                    "category": TaskCategory.CONTENT,
                    "provider": self.gemini.provider_name,
                    "default_model": getattr(self.gemini, "default_model", "gemini-3.6-flash"),
                    "aliases": ["content", "blog", "writing", "article", "welfare", "travel"]
                },
                "대화 및 메신저 (Conversation)": {
                    "category": TaskCategory.CONVERSATION,
                    "provider": self.openai.provider_name,
                    "default_model": getattr(self.openai, "default_model", "gpt-4o-mini"),
                    "aliases": ["chat", "conversation", "dialogue", "messenger", "telegram"]
                },
                "코드 분석 및 운영 (Code Analysis / Ops)": {
                    "category": TaskCategory.CODE_OPS,
                    "provider": self.claude.provider_name,
                    "default_model": getattr(self.claude, "default_model", "claude-sonnet-4-5"),
                    "aliases": ["code", "ops", "debug", "server", "architecture", "refactor"]
                },
                "실험 콘텐츠 및 트렌드 (Experimental / Trend)": {
                    "category": TaskCategory.EXPERIMENTAL,
                    "provider": self.grok.provider_name,
                    "default_model": getattr(self.grok, "default_model", "grok-4.5"),
                    "aliases": ["experimental", "trend", "viral", "realtime", "creative_experiment"]
                }
            }
        }

    async def execute_task(
        self,
        task_type: str,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Executes a prompt using the dynamically routed LLM provider.
        Includes automatic fallback if the assigned provider encounters an error.
        """
        category = self.resolve_task_category(task_type)
        primary_provider = self._route_table.get(category, self.gemini)

        logger.info(f"🔄 Routing task '{task_type}' (category: {category}) -> Provider: {primary_provider.provider_name}")

        try:
            response_text = await primary_provider.generate_response(
                prompt=prompt,
                system_instruction=system_instruction,
                model=model,
                temperature=temperature
            )

            # Check for provider failure message
            if response_text and not response_text.startswith("[") and not "Error" in response_text[:20]:
                return {
                    "status": "SUCCESS",
                    "task_type": task_type,
                    "category": category,
                    "provider": primary_provider.provider_name,
                    "model_used": model or getattr(primary_provider, "default_model", "default"),
                    "response": response_text
                }
            else:
                logger.warning(f"Primary provider {primary_provider.provider_name} returned warning/error: {response_text}. Attempting Gemini fallback...")
        except Exception as e:
            logger.error(f"Error executing with {primary_provider.provider_name}: {e}. Falling back to Gemini...")

        # Fallback to Gemini (Universal Workhorse)
        if primary_provider != self.gemini:
            try:
                fallback_res = await self.gemini.generate_response(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature
                )
                return {
                    "status": "FALLBACK_SUCCESS",
                    "task_type": task_type,
                    "category": category,
                    "primary_provider": primary_provider.provider_name,
                    "provider": "gemini",
                    "model_used": "gemini-3.6-flash",
                    "response": fallback_res
                }
            except Exception as fb_err:
                logger.error(f"Fallback to Gemini also failed: {fb_err}")

        return {
            "status": "ERROR",
            "task_type": task_type,
            "category": category,
            "provider": primary_provider.provider_name,
            "error": "Failed to generate response from routed and fallback providers"
        }

    async def call_tool_task(
        self,
        task_type: str,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calls a tool using the routed LLM provider."""
        category = self.resolve_task_category(task_type)
        provider = self._route_table.get(category, self.gemini)

        logger.info(f"🔄 Routing Tool Call for '{task_type}' -> Provider: {provider.provider_name}")
        return await provider.call_tool(
            prompt=prompt,
            tools=tools,
            system_instruction=system_instruction,
            model=model
        )


# Global Singleton Instance
multi_llm_router = MultiLLMRouter()
