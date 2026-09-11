"""
FinSight AI - Workflow State Definition
Maintains explicit typed state across all LangGraph nodes and resumption boundaries.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from backend.app.orchestration.contracts import (
    ResearchOutput,
    StrategySpecification,
    ImplementationOutput,
    QACheckResult,
    BacktestResult,
    ApprovalRecord,
    ShadowSimulationResult,
    RecommendationOutput
)

class WorkflowState(BaseModel):
    workflow_id: str
    run_id: str
    ticker: str
    owner_id: str = "demo_analyst"
    status: str = "PENDING"
    stage: str = "init"


    research_output: Optional[ResearchOutput] = None
    strategy_spec: Optional[StrategySpecification] = None
    candidate_code: Optional[ImplementationOutput] = None
    qa_results: Optional[QACheckResult] = None
    backtest_result: Optional[BacktestResult] = None
    approval_record: Optional[ApprovalRecord] = None
    shadow_result: Optional[ShadowSimulationResult] = None
    recommendation: Optional[RecommendationOutput] = None


    history: List[Dict[str, Any]] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 2
    error_message: Optional[str] = None
    interrupt_payload: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def log_transition(self, node_name: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Append an audit transition to history."""
        step = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "node": node_name,
            "status": status,
            "details": details or {}
        }
        self.history.append(step)
        self.updated_at = datetime.now(timezone.utc)
