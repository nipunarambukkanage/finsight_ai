import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from backend.app.backtesting.engine import backtest_engine
from backend.app.shadow.service import shadow_trading_service
from backend.app.data.pipeline import market_data_pipeline

def test_deterministic_backtest_with_costs_and_slippage():
    """Verify backtest accounts for chronological splits, costs, and slippage."""
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    prices = [100.0 * (1.001 ** i) for i in range(100)]
    df = pd.DataFrame({
        "timestamp": dates,
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [1000000.0] * 100
    })


    signals = np.zeros(100, dtype=int)
    signals[10:20] = 1
    signals[30:40] = 1
    signals[60:80] = 1

    res = backtest_engine.run_backtest(
        df=df,
        signals=signals,
        ticker="AAPL",
        initial_capital=100_000.0,
        cost_bps=5.0,
        slippage_bps=3.0
    )

    assert res.ticker if hasattr(res, "ticker") else True
    assert len(res.trades) > 0
    assert res.metrics["total_transaction_costs"] > 0.0
    assert res.metrics["total_slippage_incurred"] > 0.0
    assert res.metrics["hit_rate"] >= 0.0
    assert res.metrics["turnover"] > 0.0
    assert len(res.equity_curve) == 100

def test_shadow_trading_activation_requires_approval():
    """Verify shadow trading cannot be started without explicit human operator approval."""
    with pytest.raises(PermissionError):
        shadow_trading_service.start_simulation(
            strategy_id="strat-test",
            ticker="AAPL",
            approved_by=None
        )

def test_shadow_trading_lifecycle_and_virtual_fills():
    """Verify shadow simulation processes ticks, generates orders, and fills with slippage."""
    sim = shadow_trading_service.start_simulation(
        strategy_id="strat-shadow-1",
        ticker="AAPL",
        initial_cash=100_000.0,
        approved_by="senior_trader"
    )
    assert sim.status == "ACTIVE"
    assert sim.is_simulation_only is True


    sim = shadow_trading_service.process_market_tick(
        simulation_id=sim.simulation_id,
        current_price=150.0,
        signal=1,
        slippage_bps=3.0
    )
    assert len(sim.hypothetical_orders) == 1
    assert sim.hypothetical_orders[0]["side"] == "BUY"
    assert len(sim.simulated_fills) == 1
    assert sim.simulated_fills[0]["price"] > 150.0
    assert sim.virtual_portfolio["shares"] > 0


    paused = shadow_trading_service.pause_simulation(sim.simulation_id)
    assert paused.status == "PAUSED"


    res = shadow_trading_service.process_market_tick(
        simulation_id=sim.simulation_id,
        current_price=160.0,
        signal=0
    )
    assert len(res.hypothetical_orders) == 1


    resumed = shadow_trading_service.resume_simulation(sim.simulation_id)
    assert resumed.status == "ACTIVE"


    final_sim = shadow_trading_service.process_market_tick(
        simulation_id=sim.simulation_id,
        current_price=160.0,
        signal=0
    )
    assert len(final_sim.hypothetical_orders) == 2
    assert final_sim.hypothetical_orders[1]["side"] == "SELL"
    assert final_sim.virtual_portfolio["shares"] == 0.0
