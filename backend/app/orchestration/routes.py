"""
FinSight AI - Conditional Workflow Routing & Deterministic Gates
Enforces mandatory validation checks before permitting state transitions.
"""

from backend.app.orchestration.state import WorkflowState
from backend.app.core.logging import logger

def route_after_qa(state: WorkflowState) -> str:
    """Deterministic Gate: Candidate code MUST pass all QA checks before backtesting."""
    if state.qa_results and state.qa_results.passed:
        logger.info(f"Gate QA -> Backtest: PASSED for workflow {state.workflow_id}")
        return "backtest"
    
    logger.warning(f"Gate QA -> Backtest: BLOCKED (QA checks failed) for workflow {state.workflow_id}")
    return "qa_failed"

def route_after_approval(state: WorkflowState) -> str:
    """Deterministic Gate: Human Operator MUST approve backtest before shadow trading."""
    if not state.approval_record:
        logger.info(f"Gate Approval -> Shadow: Pausing for approval in workflow {state.workflow_id}")
        return "waiting_approval"

    if state.approval_record.decision == "APPROVE":
        logger.info(f"Gate Approval -> Shadow: APPROVED by {state.approval_record.reviewed_by}")
        return "shadow_trading"
    elif state.approval_record.decision == "REJECT":
        logger.warning(f"Gate Approval -> Shadow: REJECTED by {state.approval_record.reviewed_by}")
        return "rejected"
    elif state.approval_record.decision == "REQUEST_CHANGES":
        logger.info(f"Gate Approval -> Strategy: Changes requested by {state.approval_record.reviewed_by}")
        return "replan_strategy"
    else:
        return "waiting_approval"
