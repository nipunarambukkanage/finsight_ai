from __future__ import annotations

from typing import Optional, Literal
from datetime import date
import hashlib
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


class DocumentMetadata(BaseModel):
    document_id: str = Field(min_length=1)
    company: str = Field(min_length=1)
    filing_type: Literal["10-K", "10-Q", "8-K", "annual_report", "unknown"] = "unknown"
    filing_date: Optional[date] = None
    page: Optional[int] = Field(default=None, ge=1)
    section: Optional[str] = None
    source_url: Optional[str] = None
    source_sha256: Optional[str] = None


def excerpt_sha256(excerpt: str) -> str:
    return hashlib.sha256(excerpt.encode("utf-8")).hexdigest()


class GroundingCheck(BaseModel):
    example_id: str
    valid_json: bool
    evidence_quotes_valid: bool
    document_references_valid: bool
    abstention_correct: bool
    hallucinated: bool
