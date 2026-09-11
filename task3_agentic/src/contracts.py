from __future__ import annotations

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class ToolCallRecord(BaseModel):
    trace_id: str
    agent: str
    tool: str
    arguments: dict[str, Any]
    output_preview: str = Field(max_length=200)
    output_artifact: Optional[str] = None
    duration_ms: float = Field(ge=0)
    status: Literal["ok", "error", "cache"]


class DataBrief(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    period: str
    annualized_volatility: Optional[float] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    indicators: dict[str, Optional[float]] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)
    source: str


class ClarificationRequest(BaseModel):
    question: str
    requested_fields: list[str]
    headlines: list[str] = Field(default_factory=list)


class ClarificationResponse(BaseModel):
    request: ClarificationRequest
    answer: dict[str, Any]
    source: str


class RiskEvidence(BaseModel):
    title: str
    evidence: str
    source_url: Optional[str] = None
    severity: Literal["high", "medium", "low"] = "medium"


class ResearchBrief(BaseModel):
    ticker: str
    generated_at: str
    financial_health_summary: str
    top_three_risks: list[RiskEvidence] = Field(min_length=3, max_length=3)
    hedge_strategy_recommendation: str
    data_brief: DataBrief
    handoff_trace: list[dict[str, Any]] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    cached: bool = False
    incomplete: bool = False
    run_metadata: dict[str, Any] = Field(default_factory=dict)
