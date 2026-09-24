import os
import time
from typing import Optional, Dict, Any, List
from .schemas import AIResponse, AITaskType, AIProviderName
from apps.backend.tre.models import AIUsageLog
from apps.backend.tre.config import settings

class AGGateway:
    """
    AG Gateway AI Orchestration Layer.
    Dispatches generation tasks through per-account Persona AI Strategy,
    handles seamless Fallback Routing across Gemini, Claude, and GPT,
    and logs granular token costs and latency for observability.
    """
    MODEL_MAP = {
        "gemini": "gemini-2.5-flash",
        "claude": "claude-3-5-sonnet",
        "gpt": "gpt-4o-mini",
        "mock": "mock-llm-v1"
    }

    COST_PER_1K = {
        "gemini-2.5-flash": 0.00015,
        "claude-3-5-sonnet": 0.003,
        "gpt-4o-mini": 0.0003,
        "mock-llm-v1": 0.00002
    }

    def __init__(self, mode: Optional[str] = None):
        cfg = settings()
        self.mode = mode or getattr(cfg, "ag_gateway_mode", "mock")
        self.gemini_key = getattr(cfg, "gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        self.claude_key = getattr(cfg, "anthropic_api_key", os.getenv("ANTHROPIC_API_KEY", ""))
        self.gpt_key = getattr(cfg, "openai_api_key", os.getenv("OPENAI_API_KEY", ""))

    def route_and_generate(
        self,
        task_type: AITaskType,
        prompt: str,
        account_id: Optional[int] = None,
        persona: Optional[Any] = None,
        system_instruction: Optional[str] = None,
        force_provider: Optional[str] = None,
        simulate_failure_on_primary: bool = False,
        db: Optional[Any] = None
    ) -> AIResponse:
        """
        Routes the task to the designated model provider with automatic fallback.
        """
        start_time = time.time()

        # 1. Determine Preferred Provider from Persona AI Strategy
        strategy = getattr(persona, "ai_strategy", {}) or {}
        primary_provider = force_provider or strategy.get(task_type, "gemini")

        # Determine Fallback Provider
        fallback_candidates = ["gpt", "gemini", "claude"]
        fallback_provider = next((p for p in fallback_candidates if p != primary_provider), "mock")

        # 2. Attempt Generation with Primary Provider
        response = None
        error_msg = None

        if not simulate_failure_on_primary:
            try:
                response = self._call_provider(primary_provider, task_type, prompt, system_instruction)
            except Exception as e:
                error_msg = str(e)

        # 3. Fallback Routing if Primary Failed
        if response is None:
            try:
                response = self._call_provider(fallback_provider, task_type, prompt, system_instruction)
                response.fallback_used = True
                response.original_error = error_msg or "Simulated Primary Failure"
            except Exception as fb_err:
                # Ultimate safe mock fallback to guarantee zero crash
                response = self._mock_generate(task_type, prompt)
                response.fallback_used = True
                response.original_error = f"{error_msg} -> {fb_err}"

        latency = int((time.time() - start_time) * 1000)
        response.latency_ms = latency

        # 4. Usage Tracking
        if db:
            try:
                log_entry = AIUsageLog(
                    account_id=account_id,
                    model=response.model,
                    provider=response.provider,
                    task_type=task_type,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    total_tokens=response.total_tokens,
                    cost_usd=response.cost_usd,
                    status="SUCCESS",
                    latency_ms=latency
                )
                db.add(log_entry)
                db.commit()
            except Exception:
                db.rollback()

        return response

    def _call_provider(
        self,
        provider: str,
        task_type: str,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AIResponse:
        """
        Calls live provider API or mock provider depending on configuration and available keys.
        """
        # If in mock mode or API key missing, execute deterministic mock
        if self.mode == "mock" or getattr(settings(), "ai_mock", True):
            return self._mock_generate(task_type, prompt, provider=provider)

        if provider == "gemini" and self.gemini_key:
            return self._call_gemini(task_type, prompt, system_instruction)
        elif provider == "claude" and self.claude_key:
            return self._call_claude(task_type, prompt, system_instruction)
        elif provider == "gpt" and self.gpt_key:
            return self._call_gpt(task_type, prompt, system_instruction)
        else:
            # Fall back to mock provider if key is not configured
            return self._mock_generate(task_type, prompt, provider=provider)

    def _mock_generate(self, task_type: str, prompt: str, provider: str = "mock") -> AIResponse:
        model = self.MODEL_MAP.get(provider, "mock-llm-v1")
        prompt_len = len(prompt)
        p_tokens = max(10, prompt_len // 4)
        c_tokens = 150
        cost = ((p_tokens + c_tokens) / 1000.0) * self.COST_PER_1K.get(model, 0.0001)

        # Deterministic generation tailored to task
        if task_type == "research":
            content = f"[Research Analysis by {provider.upper()}]\n1. 핵심 트렌드 및 타겟 니즈 발견\n2. 근거 데이터: 실사용자 만족도 기반 선별\n3. 권장 앵글: 문제 해결 및 실용성 중심"
        elif task_type == "writing":
            content = f"솔직히 아직도 고민만 하시는 분들 많으시죠?\n\n핵심만 빠르게 짚어드립니다.\n가장 중요한 건 과장된 스펙보다 일상 속 실용성입니다.\n\n여러분은 어떤 선택 기준이 가장 중요하신가요?"
        elif task_type == "cardnews":
            content = f"카드뉴스 슬라이드 구성안 완료 (5장 패키지, 1:1 이미지 프롬프트 포함)"
        elif task_type == "product":
            content = f"상품 매칭 완료: 쿠팡 랭킹 상위 가성비 아이템 (추천 점수 92.5점)"
        elif task_type == "review":
            content = f"검수 결과: PASS (금지어 없음, 공정위 대가성 문구 포함, 사실 부합)"
        elif task_type == "analytics":
            content = f"성과 분석: 조회수 대비 저장률 우수, 추가 후속 카드뉴스 발행 권장"
        else:
            content = f"AG Gateway {task_type} 응답: 최적화된 결과물이 생성되었습니다."

        return AIResponse(
            content=content,
            provider=provider,
            model=model,
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            total_tokens=p_tokens + c_tokens,
            cost_usd=round(cost, 6)
        )

    def _call_gemini(self, task_type: str, prompt: str, system_instruction: Optional[str] = None) -> AIResponse:
        # Live Gemini API via requests or SDK
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return AIResponse(
            content=text,
            provider="gemini",
            model="gemini-2.5-flash",
            prompt_tokens=len(prompt) // 4,
            completion_tokens=len(text) // 4,
            total_tokens=(len(prompt) + len(text)) // 4,
            cost_usd=0.0002
        )

    def _call_claude(self, task_type: str, prompt: str, system_instruction: Optional[str] = None) -> AIResponse:
        import requests
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.claude_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        text = res.json()["content"][0]["text"]
        return AIResponse(
            content=text,
            provider="claude",
            model="claude-3-5-sonnet",
            prompt_tokens=len(prompt) // 4,
            completion_tokens=len(text) // 4,
            total_tokens=(len(prompt) + len(text)) // 4,
            cost_usd=0.003
        )

    def _call_gpt(self, task_type: str, prompt: str, system_instruction: Optional[str] = None) -> AIResponse:
        import requests
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.gpt_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        text = res.json()["choices"][0]["message"]["content"]
        return AIResponse(
            content=text,
            provider="gpt",
            model="gpt-4o-mini",
            prompt_tokens=len(prompt) // 4,
            completion_tokens=len(text) // 4,
            total_tokens=(len(prompt) + len(text)) // 4,
            cost_usd=0.0003
        )
