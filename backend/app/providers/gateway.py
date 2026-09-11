"""Application-owned model gateway.

Agents depend on this policy surface, never directly on a vendor SDK. The
gateway records the selected route and only uses the demo provider when the
caller explicitly allows a labelled fallback.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Optional, Type

import httpx
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.providers.manager import DemoProvider
from backend.app.core.telemetry import record


@dataclass(frozen=True)
class ModelRequest:
    task_type: str
    privacy: str = "standard"
    complexity: str = "medium"
    latency_requirement: str = "medium"
    budget: str = "medium"
    allow_demo_fallback: bool = False


class ModelGateway:
    def __init__(self) -> None:
        self.demo = DemoProvider()

    def route(self, request: ModelRequest) -> str:
        has_hosted = bool(settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY or settings.GROQ_API_KEY)
        if request.privacy == "confidential" and not has_hosted:
            return "OLLAMA" if request.latency_requirement == "low" else "VLLM"
        if settings.GROQ_API_KEY and request.complexity != "high":
            return "GROQ"
        if request.complexity == "high" and has_hosted:
            return "OPENROUTER"
        if has_hosted:
            return "OPENROUTER"
        return "DEMO" if request.allow_demo_fallback else "UNAVAILABLE"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, *, request: ModelRequest, schema: Optional[Type[BaseModel]] = None, timeout_seconds: float = 20.0) -> tuple[str | BaseModel, dict[str, Any]]:
        provider = self.route(request)
        started = time.perf_counter()
        if provider == "DEMO":
            raw = await self.demo.generate(prompt, system_prompt=system_prompt)
        elif provider in {"OPENROUTER", "GROQ", "VLLM"}:
            raw = await self._openai_compatible(provider, prompt, system_prompt, timeout_seconds)
        elif provider == "OLLAMA":
            raw = await self._ollama(prompt, system_prompt, timeout_seconds)
        else:
            raise RuntimeError("No model route is configured; set a provider key or explicitly enable demo fallback")
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        telemetry = {"provider": provider, "task_type": request.task_type, "latency_ms": latency_ms, "privacy": request.privacy}
        record("model", "generate", duration_ms=latency_ms, attributes={"provider": provider, "task_type": request.task_type, "privacy": request.privacy})
        if schema is not None:
            try:
                return schema.model_validate_json(raw), telemetry
            except Exception as exc:
                telemetry["schema_error"] = str(exc)
                raise ValueError(f"Model output failed {schema.__name__} validation") from exc
        return raw, telemetry

    async def _ollama(self, prompt: str, system_prompt: Optional[str], timeout: float) -> str:
        base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        model = getattr(settings, "OLLAMA_MODEL", "llama3.2")
        messages = ([{"role": "system", "content": system_prompt}] if system_prompt else []) + [{"role": "user", "content": prompt}]
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(2):
                try:
                    response = await client.post(f"{base_url}/api/chat", json={"model": model, "messages": messages, "stream": False, "options": {"temperature": 0}})
                    response.raise_for_status()
                    body = response.json()
                    return str(body.get("message", {}).get("content", ""))
                except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
                    retryable = not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code >= 500
                    if attempt == 0 and retryable:
                        await asyncio.sleep(0.2)
                        continue
                    raise
        raise RuntimeError("Ollama request exhausted its retry budget")

    async def _openai_compatible(self, provider: str, prompt: str, system_prompt: Optional[str], timeout: float) -> str:
        if provider == "OPENROUTER":
            base_url, api_key, model = "https://openrouter.ai/api/v1", settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY, "openai/gpt-4o-mini"
        elif provider == "GROQ":
            base_url, api_key, model = "https://api.groq.com/openai/v1", getattr(settings, "GROQ_API_KEY", ""), "llama-3.3-70b-versatile"
        else:
            base_url, api_key, model = getattr(settings, "VLLM_BASE_URL", "http://localhost:8001/v1"), "local", getattr(settings, "VLLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
        if not api_key and provider != "VLLM":
            raise RuntimeError(f"{provider} credentials are not configured")
        messages = ([{"role": "system", "content": system_prompt}] if system_prompt else []) + [{"role": "user", "content": prompt}]
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(2):
                try:
                    response = await client.post(f"{base_url.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json={"model": model, "messages": messages, "temperature": 0})
                    response.raise_for_status()
                    body = response.json()
                    return str(body["choices"][0]["message"]["content"])
                except (httpx.TimeoutException, httpx.HTTPStatusError) as exc:
                    retryable = not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code == 429 or exc.response.status_code >= 500
                    if attempt == 0 and retryable:
                        await asyncio.sleep(0.2)
                        continue
                    raise
        raise RuntimeError("Model gateway request exhausted its retry budget")


model_gateway = ModelGateway()
