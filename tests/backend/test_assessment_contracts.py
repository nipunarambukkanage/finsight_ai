"""Fast deterministic tests for the assessment packages."""

import pandas as pd
import pytest
from pathlib import Path

from task1_financial.src.pipeline import add_indicators, wilder_rsi
from task2_genai.src.dataset import build_fixture_dataset, split_source_disjoint, validate_example
from task2_genai.src.contracts import FilingExample, FilingRiskOutput, RiskItem
from task3_agentic.src.agent import _choose_next_action
from task3_agentic.src.tools import AgentRole, AuthorizedTools
from backend.app.data.pipeline import MarketDataPipeline
from backend.app.data.schemas import RawPriceRecord, DataProvenance
from backend.app.persistence.runs import RunRepository


def test_task1_indicators_have_documented_warmup_and_flat_rsi():
    prices = pd.Series([100.0] * 240)
    indicators = add_indicators(pd.DataFrame({"close": prices}))
    assert indicators["sma_50"].iloc[48] != indicators["sma_50"].iloc[48]
    assert indicators["sma_200"].iloc[-1] == 100.0
    assert wilder_rsi(prices).iloc[-1] == 50.0


def test_task1_rsi_direction_and_population_bollinger_std():
    rising = pd.Series([float(i) for i in range(1, 40)])
    falling = pd.Series([float(40 - i) for i in range(39)])
    assert wilder_rsi(rising).iloc[-1] == 100.0
    assert wilder_rsi(falling).iloc[-1] == 0.0
    frame = add_indicators(pd.DataFrame({"close": rising}))
    expected = rising.iloc[-20:].std(ddof=0)
    assert frame["bb_std"].iloc[-1] == pytest.approx(expected)


def test_task2_fixture_is_source_disjoint_and_balanced():
    examples = build_fixture_dataset(200)
    splits = split_source_disjoint(examples)
    assert {key: len(value) for key, value in splits.items()} == {"train": 160, "validation": 20, "test": 20}
    assert sum(example.assistant.abstain for example in examples) == 40
    assert all(validate_example(example)[0] for example in examples)
    assert not set(x.source_document_id for x in splits["train"]) & set(x.source_document_id for x in splits["test"])


def test_task2_rejects_fabricated_supporting_quote():
    example = FilingExample(
        example_id="bad", source_document_id="doc-1", topic="liquidity", system="system",
        user="Document: doc-1\nFiling excerpt:\nCash is $10.",
        assistant=FilingRiskOutput(risks=[RiskItem(category="liquidity", explanation="risk", supporting_quote="Debt is $50.", document_id="doc-1")], confidence=0.8),
    )
    ok, errors = validate_example(example)
    assert not ok
    assert any("exact excerpt" in error for error in errors)


def test_task3_role_restriction_and_observation_routing():
    tools = AuthorizedTools(AgentRole.DATA_ANALYST)
    with pytest.raises(PermissionError):
        tools.get_news("AAPL", 10)
    assert _choose_next_action({}, set()) == "price"
    assert _choose_next_action({"price": {}}, {"price"}) == "volatility"
    assert _choose_next_action({"price": {}, "volatility": 0.2, "news": []}, {"price", "volatility", "news"}) == "sentiment"


def test_market_pipeline_quarantines_malformed_bars_without_filling(tmp_path):
    pipeline = MarketDataPipeline(storage_dir=tmp_path / "analytical")
    rows = [
        RawPriceRecord(ticker="TEST", timestamp="2026-01-01T00:00:00Z", open=10, high=11, low=9, close=10.5, volume=100),
        RawPriceRecord(ticker="TEST", timestamp="2026-01-02T00:00:00Z", open=10, high=9, low=9, close=10, volume=100),
    ]
    frame = pipeline.clean_records(rows, provenance=DataProvenance.REAL)
    assert len(frame) == 1
    assert frame.iloc[0]["high"] == 11


def test_run_repository_claim_and_terminal_cleanup(tmp_path):
    repository = RunRepository(tmp_path / "runs.sqlite3")
    created = repository.create("AAPL", idempotency_key="test-key")
    claimed = repository.claim(created["run_id"], "worker-1")
    assert claimed and claimed["lease_owner"] == "worker-1"
    completed = repository.update(created["run_id"], "COMPLETED", {"report": {"ok": True}})
    assert completed["lease_owner"] is None
    assert repository.create("AAPL", idempotency_key="test-key")["run_id"] == created["run_id"]
    pending = repository.pending_outbox()
    assert {event["topic"] for event in pending} >= {"run.created", "run.claimed", "run.completed"}
    assert repository.mark_outbox(pending[0]["event_id"], published=True)
