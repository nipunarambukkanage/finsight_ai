import pytest
from backend.app.ml.engine import MachineLearningStockEngine
from backend.app.agents.research_agent import research_agent
from backend.app.models.schemas import ResearchAgentRequest
from backend.app.services.market_data import market_data_service

@pytest.mark.asyncio
async def test_ml_stock_engine():
    bars = await market_data_service.get_prices("AAPL", days=200)
    assert len(bars) == 200

    metrics = MachineLearningStockEngine.train_and_evaluate(
        price_bars=bars,
        model_type="random_forest",
        test_size=0.2,
        horizon_days=5
    )

    assert metrics.accuracy > 0.0
    assert 0.0 <= metrics.precision <= 1.0
    assert 0.0 <= metrics.recall <= 1.0
    assert metrics.train_samples > metrics.test_samples
    assert len(metrics.confusion_matrix) == 2
    assert len(metrics.methodology_warnings) >= 2

@pytest.mark.asyncio
async def test_multi_stage_research_agent():
    req = ResearchAgentRequest(ticker="NVDA")
    report = await research_agent.run_research(req)

    assert report.ticker == "NVDA"
    assert "Institutional Investment Intelligence Brief" in report.title
    assert len(report.execution_trace) == 8
    # Verify all 8 stages completed
    for step in report.execution_trace:
        assert step.status == "completed"
        assert step.findings_summary is not None
    
    assert "Bull Case" in report.full_markdown
    assert "Base Case" in report.full_markdown
    assert "Bear Case" in report.full_markdown
    assert report.evidence_coverage > 0.9
    assert report.ai_confidence > 0.8
