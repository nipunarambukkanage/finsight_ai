"""Stable contracts shared by the Task 1 data and LLM layers."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class SentimentLabel(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class HeadlineSentiment(BaseModel):
    headline: str = Field(min_length=1)
    sentiment: SentimentLabel
    confidence: float = Field(ge=0.0, le=1.0)
    brief_reason: str = Field(min_length=1, max_length=500)


class SignalDecision(str, Enum):
    buy = "BUY"
    hold = "HOLD"
    sell = "SELL"


class SignalReasoning(BaseModel):
    signal: SignalDecision
    confidence: float = Field(ge=0.0, le=1.0)
    justification: str = Field(min_length=1)

    @field_validator("justification")
    @classmethod
    def require_brief_explanation(cls, value: str) -> str:
        normalized = value.replace("! ", ". ").replace("? ", ". ")
        sentences = [part.strip() for part in normalized.split(". ") if part.strip()]
        if not 3 <= len(sentences) <= 5:
            raise ValueError("signal explanation must contain three to five sentences")
        return value


class DataProvenance(BaseModel):
    provider: str
    ticker: str
    retrieved_at: datetime
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    adjusted: bool = False
    price_adjustment_policy: str = "raw_close"
    analytical_price_field: str = "close"
    corporate_actions_sha256: Optional[str] = None
    data_mode: str = "live"
    dataset_sha256: Optional[str] = None


class EquitySnapshot(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    pe_ratio: Optional[float] = None
    ytd_return: Optional[float] = None
    momentum_signal: str = "INSUFFICIENT_DATA"
    indicators: dict[str, Optional[float]] = Field(default_factory=dict)
    headlines: list[dict[str, Any]] = Field(default_factory=list)
    provenance: DataProvenance
    limitations: list[str] = Field(default_factory=list)


class EquityResearchResult(BaseModel):
    snapshot: EquitySnapshot
    headline_sentiments: list[HeadlineSentiment] = Field(default_factory=list)
    invalid_headlines: int = 0
    overall_sentiment_score: float = Field(ge=-1.0, le=1.0)
    reasoning: Optional[SignalReasoning] = None
    report_markdown: Optional[str] = None
