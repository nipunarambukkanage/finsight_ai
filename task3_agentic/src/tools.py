"""Five assessment tools with explicit typed permissions and safe fallbacks."""

from __future__ import annotations

import math
import hashlib
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Any

import numpy as np

from .tracing import TraceLogger


class AgentRole(str, Enum):
    DATA_ANALYST = "data_analyst"
    RESEARCH_WRITER = "research_writer"
    SINGLE_RESEARCH = "single_research"


ROLE_TOOLS = {
    AgentRole.DATA_ANALYST: {"get_price_data", "calculate_volatility", "llm_sentiment"},
    AgentRole.RESEARCH_WRITER: {"get_news", "web_search"},
    AgentRole.SINGLE_RESEARCH: {"get_price_data", "get_news", "calculate_volatility", "llm_sentiment", "web_search"},
}


class AuthorizedTools:
    def __init__(self, role: AgentRole, trace: TraceLogger | None = None, *, allow_demo_fallback: bool = False):
        self.role = role
        self.trace = trace
        self.allow_demo_fallback = allow_demo_fallback
        self._price_cache: dict[tuple[str, str], dict[str, Any]] = {}

    def _invoke(self, name: str, arguments: dict[str, Any], fn):
        if name not in ROLE_TOOLS[self.role]:
            raise PermissionError(f"{self.role.value} cannot call {name}")
        if self.trace:
            return self.trace.call(self.role.value, name, arguments, fn)
        return fn()

    def get_price_data(self, ticker: str, period: str = "2y") -> dict[str, Any]:
        ticker = ticker.strip().upper()
        def fetch() -> dict[str, Any]:
            try:
                import yfinance as yf
                raw = yf.download(ticker, period=period, interval="1d", auto_adjust=False, progress=False, threads=False)
                if raw is None or raw.empty:
                    raise ValueError("empty yfinance response")
                if hasattr(raw.columns, "levels"):
                    raw.columns = [column[0] for column in raw.columns]
                close = raw["Close"].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
                close = close[close > 0]
                if close.empty:
                    raise ValueError("no close prices")
                return {"ticker": ticker, "period": period, "current_price": float(close.iloc[-1]), "close": close.tail(504).tolist(), "data_mode": "live", "limitations": []}
            except Exception as exc:
                if not self.allow_demo_fallback:
                    return {"ticker": ticker, "period": period, "current_price": None, "close": [], "data_mode": "unavailable", "limitations": [f"Live price provider unavailable: {exc}"]}

                seed = int.from_bytes(hashlib.sha256(f"{ticker}:{period}".encode()).digest()[:8], "big") % 2**32
                rng = np.random.default_rng(seed)
                close = (100 * np.exp(np.cumsum(rng.normal(0.0003, 0.018, 504)))).tolist()
                return {"ticker": ticker, "period": period, "current_price": close[-1], "close": close, "data_mode": "demo", "limitations": [f"Live price provider unavailable: {exc}"]}
        key = (ticker, period)
        if key in self._price_cache:
            return self._price_cache[key]
        result = self._invoke("get_price_data", {"ticker": ticker, "period": period}, fetch)
        self._price_cache[key] = result
        return result

    def get_news(self, ticker: str, n: int = 10) -> list[dict[str, Any]]:
        ticker = ticker.strip().upper()
        def fetch() -> list[dict[str, Any]]:
            try:
                import yfinance as yf
                rows = yf.Ticker(ticker).news or []
                result = []
                for row in rows:
                    content = row.get("content", {})
                    title = row.get("title") or content.get("title")
                    if title:
                        result.append({"headline": title, "url": row.get("link") or content.get("canonicalUrl", {}).get("url"), "publisher": row.get("publisher")})
                if result:
                    return result[:n]
                raise ValueError("empty news response")
            except Exception as exc:
                if not self.allow_demo_fallback:
                    return []
                return [{"headline": headline, "url": None, "publisher": "deterministic-demo", "limitation": str(exc)} for headline in [
                    f"{ticker}: no live headline available", f"{ticker}: demo growth update", f"{ticker}: demo regulatory risk",
                    f"{ticker}: demo supply chain update", f"{ticker}: demo margin commentary", f"{ticker}: demo customer demand update",
                    f"{ticker}: demo competition commentary", f"{ticker}: demo cybersecurity disclosure", f"{ticker}: demo liquidity update",
                    f"{ticker}: demo capital allocation update",
                ][:n]]
        return self._invoke("get_news", {"ticker": ticker, "n": n}, fetch)

    def calculate_volatility(self, ticker: str, window: int = 20) -> dict[str, Any]:
        def calculate() -> dict[str, Any]:
            prices = self.get_price_data(ticker, "2y")
            close = np.asarray(prices["close"], dtype=float)
            returns = np.diff(np.log(close))
            value = float(np.std(returns[-window:], ddof=1) * math.sqrt(252)) if len(returns) >= max(2, window) else None
            return {"ticker": ticker.upper(), "window": window, "annualized_volatility": value, "data_mode": prices.get("data_mode"), "limitations": prices.get("limitations", [])}
        return self._invoke("calculate_volatility", {"ticker": ticker.upper(), "window": window}, calculate)

    def llm_sentiment(self, headlines: list[str]) -> dict[str, Any]:
        def classify() -> dict[str, Any]:
            api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
            if api_key and headlines:
                try:
                    from backend.app.providers.gateway import ModelRequest, model_gateway
                    prompt = "Classify these financial headlines. Return JSON only with overall_score in [-1,1] and label positive, negative, or neutral. Headlines:\n" + "\n".join(headlines[:10])
                    request = ModelRequest(task_type="task3_headline_sentiment", complexity="medium", allow_demo_fallback=False)
                    async def call_gateway():
                        return await model_gateway.generate(prompt, request=request)
                    try:
                        asyncio.get_running_loop()
                    except RuntimeError:
                        raw, telemetry = asyncio.run(call_gateway())
                    else:
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            raw, telemetry = executor.submit(lambda: asyncio.run(call_gateway())).result()
                    body = json.loads(raw if isinstance(raw, str) else raw.model_dump_json())
                    score = max(-1.0, min(1.0, float(body["overall_score"])))
                    label = str(body["label"]).lower()
                    if label not in {"positive", "negative", "neutral"}:
                        raise ValueError("invalid sentiment label")
                    return {"overall_score": round(score, 4), "label": label, "count": len(headlines), "provider": telemetry.get("provider", "gateway")}
                except Exception as exc:
                    if not self.allow_demo_fallback:
                        return {"overall_score": None, "label": "unavailable", "count": len(headlines),
                                "provider": "unavailable", "limitations": [f"Live sentiment provider unavailable: {exc}"]}


                    provider_error = str(exc)
            else:
                provider_error = "No hosted sentiment provider credentials configured"
            if not self.allow_demo_fallback and not api_key:
                return {"overall_score": None, "label": "unavailable", "count": len(headlines),
                        "provider": "unavailable", "limitations": [provider_error]}
            scores = []
            for headline in headlines:
                lower = headline.lower()
                score = 0.6 if any(word in lower for word in ("growth", "record", "beats", "upgrade")) else -0.6 if any(word in lower for word in ("loss", "lawsuit", "downgrade", "risk", "decline")) else 0.0
                scores.append(score)
            overall = sum(scores) / len(scores) if scores else 0.0
            return {"overall_score": round(overall, 4), "label": "positive" if overall > 0.15 else "negative" if overall < -0.15 else "neutral", "count": len(scores),
                    "provider": "lexical-demo", "limitations": [provider_error] if provider_error else []}
        return self._invoke("llm_sentiment", {"headlines": headlines[:10]}, classify)

    def web_search(self, query: str) -> list[dict[str, Any]]:
        def search() -> list[dict[str, Any]]:
            try:
                from ddgs import DDGS
                return [{"title": row.get("title", ""), "snippet": row.get("body", ""), "url": row.get("href")} for row in DDGS().text(query, max_results=5)]
            except Exception as exc:
                if not self.allow_demo_fallback:
                    return [{"title": "Search unavailable", "snippet": f"No external commentary available: {exc}", "url": None}]
                return [{"title": "Search unavailable", "snippet": f"No external commentary available: {exc}", "url": None}]
        return self._invoke("web_search", {"query": query}, search)
