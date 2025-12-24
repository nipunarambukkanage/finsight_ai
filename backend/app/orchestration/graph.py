"""
FinSight AI - LangGraph Stateful Orchestration Graph
Assembles the complete research, strategy, backtesting, human approval, and shadow trading graph.
"""

from typing import Dict, Any, Optional, AsyncGenerator
import uuid
import json
import asyncio
from datetime import datetime, timezone
from langgraph.graph import StateGraph, START, END

from backend.app.orchestration.state import WorkflowState
from backend.app.orchestration.contracts import ApprovalDecision
from backend.app.orchestration.nodes import (
    market_data_node,
    research_node,
    strategy_node,
    developer_node,
    qa_node,
    backtest_node,
    human_approval_node,
    shadow_trading_node,
    recommendation_node
)
from backend.app.orchestration.routes import route_after_qa, route_after_approval
from backend.app.approvals.service import approval_service
from backend.app.core.logging import logger

def build_research_graph() -> StateGraph:
    """Constructs the compiled LangGraph StateGraph with deterministic gates."""
    builder = StateGraph(WorkflowState)

    # Register Nodes
    builder.add_node("market_data", market_data_node)
    builder.add_node("research", research_node)
    builder.add_node("strategy", strategy_node)
    builder.add_node("developer", developer_node)
    builder.add_node("qa", qa_node)
    builder.add_node("backtest", backtest_node)
    builder.add_node("approval", human_approval_node)
    builder.add_node("shadow_trading", shadow_trading_node)
    builder.add_node("recommendation", recommendation_node)

    # Sequential Edges
    builder.add_edge(START, "market_data")
    builder.add_edge("market_data", "research")
    builder.add_edge("research", "strategy")
    builder.add_edge("strategy", "developer")
    builder.add_edge("developer", "qa")

    # Deterministic Gate: QA Validation
    builder.add_conditional_edges(
        "qa",
        route_after_qa,
        {
            "backtest": "backtest",
            "qa_failed": END
        }
    )

    builder.add_edge("backtest", "approval")

    # Deterministic Gate: Human Approval
    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "shadow_trading": "shadow_trading",
            "replan_strategy": "strategy",
            "rejected": END,
            "waiting_approval": END
        }
    )

    builder.add_edge("shadow_trading", "recommendation")
    builder.add_edge("recommendation", END)

    return builder.compile()

class WorkflowEngine:
    """Manages active workflows, checkpoints, event streaming, and human resumption."""

    def __init__(self):
        self.graph = build_research_graph()
        self.workflows: Dict[str, WorkflowState] = {}
        logger.info("Initialized LangGraph Research Workflow Engine.")

    async def start_workflow(self, ticker: str, workflow_id: Optional[str] = None) -> WorkflowState:
        """Starts a new stateful workflow. Runs Phase 1 up to Human Approval pause."""
        wid = workflow_id or f"wf-{uuid.uuid4().hex[:8]}"
        state = WorkflowState(
            workflow_id=wid,
            run_id=f"run-{uuid.uuid4().hex[:6]}",
            ticker=ticker.upper(),
            status="RUNNING",
            stage="init"
        )
        self.workflows[wid] = state
        logger.info(f"Initiated workflow {wid} for {ticker}")

        # Execute Phase 1 nodes sequentially up to human approval
        state = await market_data_node(state)
        state = await research_node(state)
        state = await strategy_node(state)
        state = await developer_node(state)
        state = await qa_node(state)

        if not state.qa_results.passed:
            state.status = "FAILED"
            self.workflows[wid] = state
            return state

        state = await backtest_node(state)
        state = await human_approval_node(state)

        self.workflows[wid] = state
        return state

    async def resume_workflow(
        self,
        workflow_id: str,
        reviewed_by: str = "senior_analyst",
        decision: str = "APPROVE",
        reason: Optional[str] = None
    ) -> WorkflowState:
        """Resumes workflow after human approval decision."""
        state = self.workflows.get(workflow_id)
        if not state:
            raise ValueError(f"Workflow '{workflow_id}' not found.")

        if state.status != "WAITING_APPROVAL":
            raise ValueError(f"Workflow is in '{state.status}' state, not waiting for approval.")

        # Process approval record
        if state.approval_record:
            appr_dec = ApprovalDecision(decision.upper())
            approval_service.process_decision(
                approval_id=state.approval_record.approval_id,
                reviewed_by=reviewed_by,
                decision=appr_dec,
                reason=reason
            )
            state.approval_record.decision = appr_dec.value
            state.approval_record.reviewed_by = reviewed_by
            state.approval_record.reason = reason

        if decision.upper() == "REJECT":
            state.status = "REJECTED"
            state.stage = "rejected"
            state.log_transition("approval_gate", "rejected", {"reviewed_by": reviewed_by, "reason": reason})
            self.workflows[workflow_id] = state
            return state

        # Phase 2: Shadow trading -> Final recommendation
        state.status = "RUNNING"
        state = await shadow_trading_node(state)
        state = await recommendation_node(state)

        self.workflows[workflow_id] = state
        return state

    def cancel_workflow(self, workflow_id: str) -> WorkflowState:
        state = self.workflows.get(workflow_id)
        if not state:
            raise ValueError(f"Workflow '{workflow_id}' not found.")
        state.status = "CANCELLED"
        state.log_transition("workflow_engine", "cancelled")
        return state

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        return self.workflows.get(workflow_id)

    async def stream_workflow_events(self, workflow_id: str) -> AsyncGenerator[str, None]:
        """Stream real-time Server-Sent Events (SSE) for workflow progression."""
        state = self.workflows.get(workflow_id)
        if not state:
            yield f"event: error\ndata: {json.dumps({'error': 'Workflow not found'})}\n\n"
            return

        for step in state.history:
            yield f"data: {json.dumps(step)}\n\n"
            await asyncio.sleep(0.05)

        # Send current snapshot
        yield f"event: snapshot\ndata: {json.dumps(state.model_dump(), default=str)}\n\n"

workflow_engine = WorkflowEngine()
