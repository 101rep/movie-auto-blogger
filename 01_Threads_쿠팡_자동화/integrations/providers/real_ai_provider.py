import json
import re
from typing import Optional, Type
from pydantic import BaseModel
from integrations.interfaces import AIProvider
from config import settings

class RealAIProvider(AIProvider):
    def __init__(self):
        self.provider_name = settings.AI_PROVIDER.lower()
        self.api_key = settings.AI_API_KEY
        self.model_name = settings.AI_MODEL

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("AI_API_KEY is not configured.")

        if self.provider_name == "gemini":
            from google import genai
            client = genai.Client(api_key=self.api_key)
            config = {}
            if system_prompt:
                config["system_instruction"] = system_prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text
        elif self.provider_name == "openai":
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            res = client.chat.completions.create(
                model=self.model_name or "gpt-4o-mini",
                messages=messages
            )
            return res.choices[0].message.content
        else:
            raise ValueError(f"Unsupported live AI provider: {self.provider_name}")

    def generate_structured(self, prompt: str, schema_class: Type[BaseModel], system_prompt: Optional[str] = None) -> BaseModel:
        schema_fields = list(schema_class.model_fields.keys())
        augmented_prompt = (
            f"{prompt}\n\n"
            f"필수 JSON 필드 목록: {schema_fields}\n"
            f"반드시 위 스키마 형식에 맞는 순수 JSON만 응답하세요. 코드 블록(```json)이나 다른 설명 없이 JSON 문자열만 출력하세요."
        )
        raw_text = self.generate_text(prompt=augmented_prompt, system_prompt=system_prompt)
        
        # Robust extraction: find JSON object {...} or array [...]
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw_text)
        if match:
            clean = match.group(1).strip()
        else:
            clean = re.sub(r"^```json\s*", "", raw_text.strip())
            clean = re.sub(r"\s*```$", "", clean)
            
        data = json.loads(clean)
        return schema_class.model_validate(data)