# -*- coding: utf-8 -*-
"""
AI Provider Interface
Abstract base class defining standardized LLM text generation and tool invocation.
Enables pluggable switching between Gemini, OpenAI (GPT), and xAI (Grok).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseAIProvider(ABC):
    """Universal LLM Provider Interface for Antigravity Central AI."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique name of the provider (e.g., 'gemini', 'openai', 'grok')."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generates natural language response from the AI model."""
        pass

    @abstractmethod
    async def call_tool(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes prompt with Tool Calling capability.
        Returns:
            {
                "tool_called": bool,
                "tool_name": Optional[str],
                "tool_args": Dict[str, Any],
                "response_text": Optional[str]
            }
        """
        pass
