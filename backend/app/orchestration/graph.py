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
from backend.app.orchestration.checkpoint import local_checkpointer, local_store

def _node_adapter(node):
    """Adapt the domain's Pydantic state nodes to LangGraph update semantics."""
    async def wrapped(state):
        current = state if isinstance(state, WorkflowState) else WorkflowState.model_validate(state)
        updated = await node(current)
        return updated.model_dump()
    return wrapped


def _qa_route(state) -> str:
    return route_after_qa(state if isinstance(state, WorkflowState) else WorkflowState.model_validate(state))


def _approval_route(state) -> str:
    return route_after_approval(state if isinstance(state, WorkflowState) else WorkflowState.model_validate(state))


def build_research_graph(checkpointer=None, store=None):
    """Construct and compile the LangGraph with deterministic domain gates."""
    builder = StateGraph(WorkflowState)


    builder.add_node("market_data", _node_adapter(market_data_node))
    builder.add_node("research", _node_adapter(research_node))
    builder.add_node("strategy", _node_adapter(strategy_node))
    builder.add_node("developer", _node_adapter(developer_node))
    builder.add_node("qa", _node_adapter(qa_node))
    builder.add_node("backtest", _node_adapter(backtest_node))
    builder.add_node("approval", _node_adapter(human_approval_node))
    builder.add_node("shadow_trading", _node_adapter(shadow_trading_node))
    builder.add_node("recommendation", _node_adapter(recommendation_node))


    builder.add_edge(START, "market_data")
    builder.add_edge("market_data", "research")
    builder.add_edge("research", "strategy")
    builder.add_edge("strategy", "developer")
    builder.add_edge("developer", "qa")


    builder.add_conditional_edges(
        "qa",
        _qa_route,
        {
            "backtest": "backtest",
            "qa_failed": END
        }
    )

    builder.add_edge("backtest", "approval")


    builder.add_conditional_edges(
        "approval",
        _approval_route,
        {
            "shadow_trading": "shadow_trading",
            "replan_strategy": "strategy",
            "rejected": END,
            "waiting_approval": END
        }
    )

    builder.add_edge("shadow_trading", "recommendation")
    builder.add_edge("recommendation", END)

    return builder.compile(checkpointer=checkpointer, store=store)

class WorkflowEngine:
    """Manages active workflows, checkpoints, event streaming, and human resumption."""

    def __init__(self):



        self.checkpointer = local_checkpointer()
        self.store = local_store()
        self.graph = build_research_graph(self.checkpointer, self.store)
        self.workflows: Dict[str, WorkflowState] = {}
        logger.info("Initialized LangGraph Research Workflow Engine.")

    async def start_workflow(self, ticker: str, workflow_id: Optional[str] = None, owner_id: str = "demo_analyst") -> WorkflowState:
        """Starts a new stateful workflow. Runs Phase 1 up to Human Approval pause."""
        wid = workflow_id or f"wf-{uuid.uuid4().hex[:8]}"
        state = WorkflowState(
            workflow_id=wid,
            run_id=f"run-{uuid.uuid4().hex[:6]}",
            ticker=ticker.upper(),
            owner_id=owner_id,
            status="RUNNING",
            stage="init"
        )
        self.workflows[wid] = state
        logger.info(f"Initiated workflow {wid} for {ticker}")




        try:
            result = await self.graph.ainvoke(
                state.model_dump(),
                config={"configurable": {"thread_id": wid}},
            )
            state = WorkflowState.model_validate(result)
        except Exception as exc:




            logger.exception("Compiled graph failed for %s; using domain-node compatibility path", wid)
            try:
                state = await market_data_node(state)
                state = await research_node(state)
                state = await strategy_node(state)
                state = await developer_node(state)
                state = await qa_node(state)
                if state.qa_results and state.qa_results.passed:
                    state = await backtest_node(state)
                    state = await human_approval_node(state)
                else:
                    state.status = "FAILED"
            except Exception as fallback_exc:
                state.status = "FAILED"
                state.error_message = f"Compiled graph: {exc}; compatibility path: {fallback_exc}"

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


        yield f"event: snapshot\ndata: {json.dumps(state.model_dump(), default=str)}\n\n"

workflow_engine = WorkflowEngine()
