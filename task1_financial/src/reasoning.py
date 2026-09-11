"""Validated LLM reasoning with deterministic demo behavior and repair handling."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable, Optional

from .contracts import EquitySnapshot, HeadlineSentiment, EquityResearchResult, SignalReasoning, SentimentLabel
from .prompts import HEADLINE_SENTIMENT_SYSTEM, HEADLINE_SENTIMENT_USER, SIGNAL_SYSTEM, SIGNAL_USER

logger = logging.getLogger(__name__)
JsonCaller = Callable[[str, str], Awaitable[str]]


def _demo_headline(headline: str) -> HeadlineSentiment:
    lower = headline.lower()
    negative = any(word in lower for word in ("loss", "lawsuit", "downgrade", "risk", "decline", "cuts"))
    positive = any(word in lower for word in ("growth", "record", "beats", "upgrade", "strong", "surge"))
    label = SentimentLabel.negative if negative and not positive else SentimentLabel.positive if positive else SentimentLabel.neutral
    return HeadlineSentiment(headline=headline, sentiment=label, confidence=0.62, brief_reason="Keyword evidence in the headline supports this classification.")


def _signed(item: HeadlineSentiment) -> float:
    return item.confidence * {SentimentLabel.positive: 1, SentimentLabel.negative: -1, SentimentLabel.neutral: 0}[item.sentiment]


async def analyze_news_and_signal(
    snapshot: EquitySnapshot,
    caller: Optional[JsonCaller] = None,
) -> EquityResearchResult:
    valid: list[HeadlineSentiment] = []
    invalid = 0
    for item in snapshot.headlines:
        headline = str(item.get("headline", "")).strip()
        if not headline:
            invalid += 1
            continue
        try:
            if caller is None:
                parsed = _demo_headline(headline)
            else:
                prompt = HEADLINE_SENTIMENT_USER.format(headline=headline)
                raw = await caller(HEADLINE_SENTIMENT_SYSTEM, prompt)
                try:
                    parsed = HeadlineSentiment.model_validate_json(raw)
                except Exception:


                    repaired = await caller(HEADLINE_SENTIMENT_SYSTEM, prompt + "\nReturn only schema-valid JSON; repair your previous response.")
                    parsed = HeadlineSentiment.model_validate_json(repaired)
                if parsed.headline.strip() != headline:
                    raise ValueError("model returned a sentiment for a different headline")
            valid.append(parsed)
        except Exception as exc:
            invalid += 1
            logger.warning("Invalid headline response: %s", exc)
    score = sum(_signed(item) for item in valid) / len(valid) if valid else 0.0
    reasoning: Optional[SignalReasoning] = None
    if snapshot.current_price is not None:
        try:
            if caller is None:
                tech = snapshot.momentum_signal
                signal = "BUY" if tech == "BULLISH" and score >= 0 else "SELL" if tech == "BEARISH" and score < 0 else "HOLD"
                reasoning = SignalReasoning(signal=signal, confidence=0.55, justification=(
                    f"The technical regime is {tech.lower()} and the aggregate headline score is {score:.2f}. "
                    "The decision combines trend and momentum evidence with news direction. "
                    "Conflicting or incomplete evidence limits conviction, so this is decision support only."
                ))
            else:
                prompt = SIGNAL_USER.format(ticker=snapshot.ticker, indicators=snapshot.indicators, sentiment=score)
                raw = await caller(SIGNAL_SYSTEM, prompt)
                try:
                    reasoning = SignalReasoning.model_validate_json(raw)
                except Exception:
                    repaired = await caller(SIGNAL_SYSTEM, prompt + "\nReturn only schema-valid JSON; repair your previous response.")
                    reasoning = SignalReasoning.model_validate_json(repaired)
        except Exception as exc:
            logger.warning("Signal response validation failed: %s", exc)
    return EquityResearchResult(snapshot=snapshot, headline_sentiments=valid, invalid_headlines=invalid,
                                overall_sentiment_score=max(-1.0, min(1.0, score)), reasoning=reasoning)
