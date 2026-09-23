# -*- coding: utf-8 -*-
"""
Antigravity Universal AI Provider Router
Provides dynamic provider registry and domain-specific Multi-LLM Routing:
  - Gemini: Content Creation (콘텐츠 생성)
  - GPT: Conversation / Messenger (대화 / 메신저)
  - Claude: Code Analysis / Ops (코드 분석 / 운영)
  - Grok: Experimental / Trend (실험 콘텐츠 / 트렌드)
  - Image: Grok Imagine / GPT Image / Gemini Image (최신 이미지 생성 모델)
"""

import os
from typing import Dict, Optional, Any
from ai.interfaces import BaseAIProvider
from ai.providers.gemini_provider import GeminiProvider
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.grok_provider import GrokProvider
from ai.providers.openai_compatible_provider import OpenAICompatibleProvider
from ai.providers.claude_provider import ClaudeProvider
from ai.providers.image_provider import ImageGenProvider
from ai.multi_llm_router import MultiLLMRouter, multi_llm_router, TaskCategory

class AIProviderRegistry:
    def __init__(self):
        compat_prov = OpenAICompatibleProvider()
        claude_prov = ClaudeProvider()
        image_prov = ImageGenProvider()
        self._providers: Dict[str, Any] = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "grok": GrokProvider(),
            "claude": claude_prov,
            "anthropic": claude_prov,
            "openai_compatible": compat_prov,
            "syntero": compat_prov,
            "image": image_prov,
            "grok_image": image_prov,
            "gpt_image": image_prov,
            "gemini_image": image_prov
        }
        self.default_provider_name = os.getenv("DEFAULT_AI_PROVIDER", "gemini").lower()

    def get(self, name: Optional[str] = None) -> Any:
        prov_name = (name or self.default_provider_name).lower()
        return self._providers.get(prov_name, self._providers["gemini"])

    def register(self, name: str, provider: Any) -> None:
        self._providers[name.lower()] = provider

ai_registry = AIProviderRegistry()
