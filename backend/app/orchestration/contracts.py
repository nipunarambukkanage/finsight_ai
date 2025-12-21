"""
FinSight AI - Structured Workflow Contracts
Defines typed Pydantic models for all stateful agent transitions:
- ResearchOutput
- StrategySpecification
- ImplementationOutput
- QACheckResult
- BacktestResult
- ApprovalRecord
- ShadowSimulationResult
- RecommendationOutput
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

class RecommendationAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    NO_ACTION = "NO_ACTION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class ApprovalDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    PAUSE = "PAUSE"
    CANCEL = "CANCEL"
    RERUN = "RERUN"

class ResearchOutput(BaseModel):
    research_id: str
    ticker: str
    claims: List[str] = Field(default_factory=list)
    methodology: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StrategySpecification(BaseModel):
    strategy_id: str
    version: str = "1.0.0"
    hypothesis: str
    required_inputs: List[str] = Field(default_factory=lambda: ["OHLCV"])
    features: List[str] = Field(default_factory=list)
    entry_conditions: List[str] = Field(default_factory=list)
    exit_conditions: List[str] = Field(default_factory=list)
    risk_constraints: Dict[str, Any] = Field(default_factory=dict)
    holding_period: str = "5-10 trading days"
    source_references: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ImplementationOutput(BaseModel):
    strategy_id: str
    version: str = "1.0.0"
    source_code: str
    test_code: str
    dependencies: List[str] = Field(default_factory=lambda: ["numpy", "pandas"])
    static_check_result: Dict[str, Any] = Field(default_factory=dict)
    review_status: str = "pending_qa"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QACheckResult(BaseModel):
    passed: bool
    ast_valid: bool
    imports_valid: bool
    unit_tests_passed: bool
    invariants_passed: bool
    lookahead_passed: bool
    leakage_passed: bool
    details: List[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BacktestResult(BaseModel):
    strategy_id: str
    version: str = "1.0.0"
    snapshot_id: str
    train_period: str
    val_period: str
    test_period: str
    equity_curve: List[Dict[str, Any]] = Field(default_factory=list)
    trades: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    suspicious_flags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ApprovalRecord(BaseModel):
    approval_id: str
    workflow_id: str
    artifact_hash: str
    requested_by: str = "system"
    reviewed_by: Optional[str] = None
    decision: str = "PENDING"
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewed_at: Optional[datetime] = None

class ShadowSimulationResult(BaseModel):
    simulation_id: str
    strategy_id: str
    status: str = "ACTIVE"  # ACTIVE, PAUSED, COMPLETED
    virtual_portfolio: Dict[str, Any] = Field(default_factory=dict)
    hypothetical_orders: List[Dict[str, Any]] = Field(default_factory=list)
    simulated_fills: List[Dict[str, Any]] = Field(default_factory=list)
    slippage_incurred: float = 0.0
    simulated_pnl: float = 0.0
    current_exposure: float = 0.0
    is_simulation_only: bool = True
    disclaimer: str = "SIMULATION ONLY: No real orders executed or broker connections active."
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RecommendationOutput(BaseModel):
    ticker: str
    action: RecommendationAction
    confidence: float = Field(ge=0.0, le=1.0)
    strategy_id: str
    strategy_version: str
    time_horizon: str
    supporting_evidence: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    backtest_summary: Dict[str, Any] = Field(default_factory=dict)
    shadow_summary: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disclaimer: str = (
        "DECISION SUPPORT ONLY: FinSight AI does NOT execute trades or guarantee returns. "
        "All calculations and recommendations are quantitative models and should not be construed as investment advice."
    )
