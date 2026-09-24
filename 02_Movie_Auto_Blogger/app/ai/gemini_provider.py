"""Google Gemini article provider implementation using official google-genai SDK."""
import time
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.ai.base import BaseArticleWriter
from app.ai.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt
from app.ai.schemas import ArticleOutput, GenerationResult
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("gemini_provider")


class GeminiArticleProvider(BaseArticleWriter):
    """Generates structured Korean movie articles via Google Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        # Initialize client if API key is provided
        if self.api_key and self.api_key.strip():
            self.client = genai.Client(api_key=self.api_key.strip())
        else:
            self.client = None

    async def health_check(self) -> Dict[str, Any]:
        """Verify Gemini API key and model connectivity."""
        if not self.api_key or not self.api_key.strip():
            return {
                "success": False,
                "message": "Google Gemini API 키가 설정되지 않았습니다 (.env의 GEMINI_API_KEY 확인 필요)"
            }

        try:
            client = self.client or genai.Client(api_key=self.api_key.strip())
            # Simple model check
            model_info = client.models.get(model=self.model)
            return {
                "success": True,
                "message": f"Gemini API 정상 연결 성공 (모델: {model_info.name or self.model})"
            }
        except APIError as e:
            return {
                "success": False,
                "message": f"Gemini API 오류 ({e.code}): {e.message}"
            }
        except Exception as e:
            logger.error("Gemini health check error: %s", str(e), exc_info=True)
            return {"success": False, "message": f"Gemini 연결 오류: {str(e)}"}

    async def generate_article(
        self,
        movie_data: Dict[str, Any],
        prompt_version: str = PROMPT_VERSION,
        additional_instruction: Optional[str] = None
    ) -> GenerationResult:
        """Generate structured ArticleOutput using Google Gemini SDK."""
        if not self.api_key or not self.api_key.strip():
            return GenerationResult(
                success=False,
                requested_provider="gemini",
                error_message="Gemini API 키가 설정되지 않았습니다.",
                failure_category="MISSING_CREDENTIALS"
            )

        start_time = time.time()
        user_prompt = movie_data.get("custom_prompt") or build_user_prompt(movie_data)
        system_prompt = movie_data.get("custom_system_prompt") or SYSTEM_PROMPT
        target_schema = movie_data.get("schema") or ArticleOutput

        if additional_instruction:
            user_prompt += f"\n\n[추가 수정 지침]\n{additional_instruction}"

        try:
            logger.info("Requesting Gemini article generation with model '%s' (schema=%s)...", self.model, target_schema.__name__)
            client = self.client or genai.Client(api_key=self.api_key.strip())

            # Configure structured output with Pydantic schema
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=target_schema,
                temperature=0.7,
            )

            response = await client.aio.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config,
            )

            latency = round((time.time() - start_time) * 1000, 2)

            if not response.text:
                return GenerationResult(
                    success=False,
                    requested_provider="gemini",
                    used_provider="gemini",
                    latency_ms=latency,
                    error_message="Gemini에서 빈 텍스트 응답을 반환했습니다.",
                    failure_category="EMPTY_RESPONSE"
                )

            # Parse and validate with Pydantic
            article_output = target_schema.model_validate_json(response.text)

            # Capture token usage metadata if available
            usage_meta = getattr(response, "usage_metadata", None)
            p_tokens = getattr(usage_meta, "prompt_token_count", None) if usage_meta else None
            c_tokens = getattr(usage_meta, "candidates_token_count", None) if usage_meta else None
            t_tokens = getattr(usage_meta, "total_token_count", None) if usage_meta else None

            return GenerationResult(
                success=True,
                article=article_output,
                requested_provider="gemini",
                used_provider="gemini",
                prompt_version=prompt_version,
                latency_ms=latency,
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_tokens=t_tokens
            )

        except APIError as e:
            logger.warning("Gemini APIError encountered: %s", str(e))
            category = "RATE_LIMIT" if e.code == 429 else "AUTH_ERROR" if e.code in (401, 403) else "PROVIDER_ERROR"
            return GenerationResult(
                success=False,
                requested_provider="gemini",
                used_provider="gemini",
                error_message=f"Gemini API 오류 ({e.code}): {e.message}",
                failure_category=category
            )
        except Exception as e:
            logger.error("Gemini generation failed: %s", str(e), exc_info=True)
            return GenerationResult(
                success=False,
                requested_provider="gemini",
                used_provider="gemini",
                error_message=str(e),
                failure_category="PROVIDER_ERROR"
            )
