"""OpenAI article provider implementation using official OpenAI SDK."""
import time
from typing import Any, Dict, Optional
import openai
from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError, APITimeoutError

from app.ai.base import BaseArticleWriter
from app.ai.prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt
from app.ai.schemas import ArticleOutput, GenerationResult
from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("openai_provider")


class OpenAIArticleProvider(BaseArticleWriter):
    """Generates structured Korean movie articles via OpenAI."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = (api_key if api_key is not None else (settings.OPENAI_API_KEY or "")).strip()
        raw_model = model or settings.OPENAI_MODEL

        # Automatic OpenRouter gateway detection for sk-or-v1- keys
        if self.api_key.startswith("sk-or-v1-"):
            self.base_url = "https://openrouter.ai/api/v1"
            self.model = raw_model if "/" in raw_model else f"openai/{raw_model}"
            self.is_openrouter = True
        else:
            self.base_url = None
            self.model = raw_model
            self.is_openrouter = False

        self.client = AsyncOpenAI(
            api_key=self.api_key or "sk-dummy-key",
            base_url=self.base_url,
            timeout=45.0
        )

    async def health_check(self) -> Dict[str, Any]:
        """Verify OpenAI/OpenRouter API key and connectivity."""
        if not self.api_key or not self.api_key.strip():
            return {
                "success": False,
                "message": "AI API 키가 설정되지 않았습니다 (.env의 OPENAI_API_KEY 확인 필요)"
            }

        label = "OpenRouter (GPT)" if self.is_openrouter else "OpenAI"
        try:
            # Lightweight check: list models
            await self.client.models.list()
            return {"success": True, "message": f"{label} 정상 연결 성공 (모델: {self.model})"}
        except AuthenticationError:
            return {
                "success": False,
                "message": f"{label} 인증 실패: API 키가 유효하지 않습니다. 플랫폼 설정을 확인하세요."
            }
        except RateLimitError:
            return {
                "success": False,
                "message": f"{label} 요청 한도 초과 또는 잔여 크레딧 부족(Rate Limit/Quota exceeded)."
            }
        except APITimeoutError:
            return {"success": False, "message": "OpenAI 서버 응답 시간 초과 (네트워크 상태를 확인하세요)"}
        except Exception as e:
            logger.error("OpenAI health check error: %s", str(e), exc_info=True)
            return {"success": False, "message": f"OpenAI 연결 오류: {str(e)}"}

    async def generate_article(
        self,
        movie_data: Dict[str, Any],
        prompt_version: str = PROMPT_VERSION,
        additional_instruction: Optional[str] = None
    ) -> GenerationResult:
        """Generate structured ArticleOutput using OpenAI."""
        if not self.api_key or not self.api_key.strip():
            return GenerationResult(
                success=False,
                requested_provider="openai",
                error_message="OpenAI API 키가 설정되지 않았습니다.",
                failure_category="MISSING_CREDENTIALS"
            )

        start_time = time.time()
        user_prompt = movie_data.get("custom_prompt") or build_user_prompt(movie_data)
        system_prompt = movie_data.get("custom_system_prompt") or SYSTEM_PROMPT
        target_schema = movie_data.get("schema") or ArticleOutput

        if additional_instruction:
            user_prompt += f"\n\n[추가 수정 지침]\n{additional_instruction}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            logger.info("Requesting OpenAI article generation with model '%s' (schema=%s)...", self.model, target_schema.__name__)
            # Use OpenAI Structured Outputs parse
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=target_schema,
            )

            latency = round((time.time() - start_time) * 1000, 2)
            parsed_article = completion.choices[0].message.parsed
            usage = completion.usage

            if not parsed_article:
                return GenerationResult(
                    success=False,
                    requested_provider="openai",
                    used_provider="openai",
                    latency_ms=latency,
                    error_message="OpenAI에서 스키마에 맞는 응답을 파싱하지 못했습니다.",
                    failure_category="SCHEMA_PARSING_FAILED"
                )

            return GenerationResult(
                success=True,
                article=parsed_article,
                requested_provider="openai",
                used_provider="openai",
                prompt_version=prompt_version,
                latency_ms=latency,
                prompt_tokens=usage.prompt_tokens if usage else None,
                completion_tokens=usage.completion_tokens if usage else None,
                total_tokens=usage.total_tokens if usage else None
            )

        except AuthenticationError as e:
            return GenerationResult(
                success=False,
                requested_provider="openai",
                used_provider="openai",
                error_message="OpenAI 인증 오류 (API Key 확인 필요)",
                failure_category="AUTH_ERROR"
            )
        except RateLimitError as e:
            err_str = str(e)
            is_credit = any(k in err_str.lower() for k in ("credit", "quota", "insufficient_quota", "402", "balance"))
            return GenerationResult(
                success=False,
                requested_provider="openai",
                used_provider="openai",
                error_message=f"OpenAI 속도 제한/크레딧 초과: {err_str}",
                failure_category="CREDIT_DEPLETED" if is_credit else "RATE_LIMIT"
            )
        except APITimeoutError as e:
            return GenerationResult(
                success=False,
                requested_provider="openai",
                used_provider="openai",
                error_message="OpenAI 응답 시간 초과 (45s timeout)",
                failure_category="TIMEOUT"
            )
        except Exception as e:
            logger.error("OpenAI generation failed: %s", str(e), exc_info=True)
            err_str = str(e)
            is_credit = any(k in err_str.lower() for k in ("credit", "quota", "insufficient_quota", "402", "balance", "payment required"))
            return GenerationResult(
                success=False,
                requested_provider="openai",
                used_provider="openai",
                error_message=err_str,
                failure_category="CREDIT_DEPLETED" if is_credit else "PROVIDER_ERROR"
            )
