# -*- coding: utf-8 -*-
"""
Universal AI Image Generation Provider Adapter (Synterolink / OpenAI / Gemini / Grok Image)
Supports:
  - GPT Image: gpt-image-2.5, gpt-image-2, gpt-image-2.5-sunburst, gpt-image-2.5-flare
  - Grok Imagine: grok-imagine-image
  - Gemini Image: gemini-3.1-flash-image, gemini-3-pro-image
"""

import os
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger("ImageGenProvider")

class ImageGenProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: str = "gpt-image-2.5"
    ):
        self.api_key = (
            api_key
            or os.getenv("IMAGE_GEN_API_KEY")
            or os.getenv("GROK_IMAGE_API_KEY", "")
        ).strip()
        
        raw_base = (
            base_url
            or os.getenv("IMAGE_GEN_BASE_URL")
            or "https://api.synterolink.com/v1"
        ).rstrip("/")
        
        if not raw_base.endswith("/images/generations"):
            self.endpoint_url = f"{raw_base}/images/generations"
        else:
            self.endpoint_url = raw_base
            
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "image_gen"

    @property
    def available_models(self) -> List[str]:
        return [
            "gpt-image-2.5",
            "gpt-image-2",
            "gpt-image-2.5-sunburst",
            "gpt-image-2.5-flare",
            "grok-imagine-image",
            "gemini-3.1-flash-image",
            "gemini-3-pro-image"
        ]

    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        size: str = "1024x1024",
        n: int = 1
    ) -> Dict[str, Any]:
        """
        Generates images via Synterolink / OpenAI Compatible Image Generation API.
        """
        if not self.api_key:
            return {"status": "ERROR", "message": "Image Generation API Key is not configured."}

        target_model = model or self.default_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": target_model,
            "prompt": prompt,
            "n": n,
            "size": size
        }

        logger.info(f"🎨 [Image Provider] Requesting image generation with model '{target_model}'...")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(self.endpoint_url, headers=headers, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    image_urls = [item.get("url") for item in data.get("data", []) if item.get("url")]
                    b64_data = [item.get("b64_json") for item in data.get("data", []) if item.get("b64_json")]
                    return {
                        "status": "SUCCESS",
                        "model": target_model,
                        "image_urls": image_urls,
                        "b64_data": b64_data,
                        "raw_data": data.get("data", [])
                    }
                else:
                    logger.warning(f"Image API returned status {resp.status_code}: {resp.text[:200]}")
                    return {
                        "status": "UPSTREAM_ERROR",
                        "status_code": resp.status_code,
                        "model": target_model,
                        "error_message": resp.text[:300]
                    }
        except Exception as e:
            logger.error(f"Image generation exception: {e}")
            return {
                "status": "EXCEPTION",
                "model": target_model,
                "error": str(e)
            }
