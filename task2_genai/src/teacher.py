"""Free-tier Groq teacher adapter with a startup capability check."""

from __future__ import annotations

import os
from typing import Any

import httpx


class GroqTeacher:
    def __init__(self, model: str = "qwen/qwen3.6-27b", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {"available": False, "reason": "GROQ_API_KEY is not configured", "model": self.model}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
                response.raise_for_status()
                models = {item["id"] for item in response.json().get("data", [])}
                return {"available": self.model in models, "model": self.model, "models_seen": len(models), "rate_limit_headers": {key: value for key, value in response.headers.items() if "ratelimit" in key.lower()}}
        except Exception as exc:
            return {"available": False, "model": self.model, "reason": str(exc)}

    async def __call__(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is required for teacher generation")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "temperature": 0.2, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]})
            response.raise_for_status()
            return str(response.json()["choices"][0]["message"]["content"])

