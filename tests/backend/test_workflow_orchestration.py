import pytest
from backend.app.orchestration.graph import workflow_engine
from backend.app.orchestration.contracts import ApprovalDecision, RecommendationAction

@pytest.mark.asyncio
async def test_workflow_phase1_and_human_approval_pause():
    """Test workflow runs from market data through backtest and pauses at WAITING_APPROVAL."""
    state = await workflow_engine.start_workflow(ticker="AAPL")

    assert state.workflow_id is not None
    assert state.ticker == "AAPL"
    assert state.status == "WAITING_APPROVAL"
    assert state.stage == "human_approval"


    assert state.research_output is not None
    assert state.research_output.ticker == "AAPL"
    assert len(state.research_output.sources) > 0
    assert state.research_output.confidence > 0.8

    assert state.strategy_spec is not None
    assert state.strategy_spec.strategy_id.startswith("strat-")

    assert state.candidate_code is not None
    assert "class CandidateStrategy" in state.candidate_code.source_code

    assert state.qa_results is not None
    assert state.qa_results.passed is True
    assert state.qa_results.lookahead_passed is True

    assert state.backtest_result is not None
    assert "sharpe_ratio" in state.backtest_result.metrics
    assert len(state.backtest_result.equity_curve) > 0

    assert state.approval_record is not None
    assert state.approval_record.decision == "PENDING"
    assert len(state.approval_record.artifact_hash) == 64

@pytest.mark.asyncio
async def test_workflow_resume_approval():
    """Test resuming an interrupted workflow with human approval advances to shadow trading and recommendation."""
    state = await workflow_engine.start_workflow(ticker="MSFT")
    wid = state.workflow_id
    assert state.status == "WAITING_APPROVAL"

    resumed_state = await workflow_engine.resume_workflow(
        workflow_id=wid,
        reviewed_by="senior_trader",
        decision="APPROVE",
        reason="Backtest metrics and Sharpe ratio meet institutional criteria."
    )

    assert resumed_state.status == "COMPLETED"
    assert resumed_state.stage == "recommendation"
    assert resumed_state.shadow_result is not None
    assert resumed_state.shadow_result.is_simulation_only is True
    assert resumed_state.recommendation is not None
    assert resumed_state.recommendation.action in [RecommendationAction.BUY, RecommendationAction.HOLD, RecommendationAction.SELL]
    assert "DECISION SUPPORT ONLY" in resumed_state.recommendation.disclaimer

@pytest.mark.asyncio
async def test_workflow_resume_rejection():
    """Test resuming an interrupted workflow with rejection halts before shadow trading."""
    state = await workflow_engine.start_workflow(ticker="NVDA")
    wid = state.workflow_id

    resumed_state = await workflow_engine.resume_workflow(
        workflow_id=wid,
        reviewed_by="risk_manager",
        decision="REJECT",
        reason="Drawdown risk exceeds fund constraints."
    )

    assert resumed_state.status == "REJECTED"
    assert resumed_state.shadow_result is None
    assert resumed_state.recommendation is None
