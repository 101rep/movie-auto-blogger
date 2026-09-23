import json
import re
from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, ValidationError

def clean_json_string(raw_str: str) -> str:
    # Strip markdown codeblocks like ```json ... ```
    cleaned = raw_str.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()

def parse_and_validate_json(raw_str: str, schema_class: Type[BaseModel]) -> BaseModel:
    cleaned = clean_json_string(raw_str)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Fallback heuristic: find first { and last }
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(cleaned[start:end+1])
        else:
            raise ValueError(f"Failed to decode JSON from AI output: {e}")

    try:
        return schema_class.model_validate(data)
    except ValidationError as ve:
        raise ValueError(f"JSON schema validation failed: {ve}")