"""AI Provider Router implementing failover between OpenAI and Google Gemini."""
from typing import Any, Dict, Optional
from app.ai.base import BaseArticleWriter
from app.ai.gemini_provider import GeminiArticleProvider
from app.ai.openai_provider import OpenAIArticleProvider
from app.ai.prompts import PROMPT_VERSION, SCHEMA_CORRECTION_PROMPT
from app.ai.schemas import GenerationResult
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("ai_router")


class AIProviderRouter:
    """Routes article generation requests to Primary AI provider with automatic Fallback."""

    def __init__(
        self,
        openai_provider: Optional[BaseArticleWriter] = None,
        gemini_provider: Optional[BaseArticleWriter] = None,
        primary: Optional[str] = None,
        fallback: Optional[str] = None
    ) -> None:
        settings = get_settings()
        self.primary_name = (primary or settings.PRIMARY_AI).lower()
        self.fallback_name = (fallback or settings.FALLBACK_AI).lower()

        self.openai = openai_provider or OpenAIArticleProvider()
        self.gemini = gemini_provider or GeminiArticleProvider()

    def _get_provider(self, name: str) -> Optional[BaseArticleWriter]:
        if name == "openai":
            return self.openai
        elif name == "gemini":
            return self.gemini
        return None

    async def generate_article(
        self,
        movie_data: Dict[str, Any],
        prompt_version: str = PROMPT_VERSION
    ) -> GenerationResult:
        """Execute resilient article generation with primary -> retry -> fallback logic."""
        primary_provider = self._get_provider(self.primary_name)
        fallback_provider = self._get_provider(self.fallback_name)

        if not primary_provider:
            return GenerationResult(
                success=False,
                requested_provider=self.primary_name,
                error_message=f"알 수 없는 기본 AI 제공자입니다: {self.primary_name}",
                failure_category="CONFIG_ERROR"
            )

        logger.info("AI Router: Starting generation with Primary Provider '%s'...", self.primary_name)
        attempts = 1

        # Attempt 1: Primary provider
        result = await primary_provider.generate_article(movie_data, prompt_version=prompt_version)

        # Retry once if schema parsing or recoverable error
        if not result.success and result.failure_category in ("SCHEMA_PARSING_FAILED", "EMPTY_RESPONSE"):
            logger.warning("Primary provider '%s' failed validation. Retrying once with correction...", self.primary_name)
            attempts += 1
            result = await primary_provider.generate_article(
                movie_data,
                prompt_version=prompt_version,
                additional_instruction=SCHEMA_CORRECTION_PROMPT
            )

        # If primary succeeded, return result
        if result.success and result.article:
            logger.info("Primary Provider '%s' succeeded in %d attempt(s).", self.primary_name, attempts)
            result.attempts = attempts
            result.fallback_used = False
            return result

        # Primary failed -> Trigger Fallback
        logger.warning(
            "Primary Provider '%s' failed (%s: %s). Activating Fallback Provider '%s'...",
            self.primary_name,
            result.failure_category,
            result.error_message,
            self.fallback_name
        )

        # Trigger Telegram Alert if credit depleted or failover
        try:
            import asyncio
            from app.services.telegram_service import TelegramAlertService
            tg = TelegramAlertService()
            if tg.is_configured():
                topic_title = movie_data.get("title") or movie_data.get("topic") or movie_data.get("keyword") or ""
                err_lower = (result.error_message or "").lower()
                is_credit = result.failure_category == "CREDIT_DEPLETED" or any(k in err_lower for k in ("credit", "402", "quota", "insufficient_quota"))
                if is_credit:
                    await tg.send_credit_depleted_alert(
                        provider=self.primary_name,
                        error_msg=result.error_message or "API 잔액 부족 (402 Payment Required)",
                        fallback_provider=self.fallback_name,
                        topic=topic_title
                    )
                else:
                    await tg.send_failover_alert(
                        primary=self.primary_name,
                        fallback=self.fallback_name,
                        reason=f"[{result.failure_category}] {result.error_message}",
                        topic=topic_title
                    )
        except Exception as te:
            logger.debug("Telegram alert dispatch skipped: %s", str(te))

        if not fallback_provider or self.fallback_name == self.primary_name:
            logger.error("No valid fallback provider configured or fallback equals primary.")
            result.attempts = attempts
            return result

        attempts += 1
        fallback_result = await fallback_provider.generate_article(movie_data, prompt_version=prompt_version)

        if fallback_result.success and fallback_result.article:
            logger.info("Fallback Provider '%s' succeeded successfully!", self.fallback_name)
            fallback_result.requested_provider = self.primary_name
            fallback_result.used_provider = self.fallback_name
            fallback_result.fallback_used = True
            fallback_result.attempts = attempts
            return fallback_result

        # Both primary and fallback failed
        logger.error(
            "Both Primary ('%s') and Fallback ('%s') providers failed to generate article.",
            self.primary_name,
            self.fallback_name
        )
        return GenerationResult(
            success=False,
            requested_provider=self.primary_name,
            used_provider=self.fallback_name,
            fallback_used=True,
            attempts=attempts,
            error_message=f"Primary ({result.error_message}) and Fallback ({fallback_result.error_message}) both failed.",
            failure_category="ALL_PROVIDERS_FAILED"
        )
