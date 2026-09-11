from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    category: Literal["liquidity", "leverage", "customer_concentration", "competition", "regulation", "cybersecurity", "supply_chain", "insufficient_evidence"]
    explanation: str = Field(min_length=1)
    supporting_quote: Optional[str] = None
    document_id: Optional[str] = None
    abstain: bool = False


class FilingRiskOutput(BaseModel):
    risks: list[RiskItem] = Field(default_factory=list)
    abstain: bool = False
    confidence: float = Field(ge=0.0, le=1.0)


class FilingExample(BaseModel):
    example_id: str
    source_document_id: str
    topic: str
    system: str
    user: str
    assistant: FilingRiskOutput
