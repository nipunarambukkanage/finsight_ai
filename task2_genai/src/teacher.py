"""Free-tier Groq teacher adapter with a startup capability check."""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import Any

import httpx


@dataclass(frozen=True)
class TeacherPreflight:
    available: bool
    model: str
    reason: str | None = None
    models_seen: int = 0
    rate_limit_headers: dict[str, str] | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class GroqTeacher:
    def __init__(self, model: str = "qwen/qwen3.6-27b", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return TeacherPreflight(False, self.model, "GROQ_API_KEY is not configured").as_dict()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
                response.raise_for_status()
                models = {item["id"] for item in response.json().get("data", [])}
                available = self.model in models
                reason = None if available else "configured teacher model is not listed by provider"
                return TeacherPreflight(available, self.model, reason, len(models), {key: value for key, value in response.headers.items() if "ratelimit" in key.lower()}).as_dict()
        except Exception as exc:
            return TeacherPreflight(False, self.model, str(exc)).as_dict()

    async def __call__(self, system_prompt: str, user_prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is required for teacher generation")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "temperature": 0.2, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]})
            response.raise_for_status()
            return str(response.json()["choices"][0]["message"]["content"])
