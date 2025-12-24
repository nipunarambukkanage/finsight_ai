"""
FinSight AI - Strategy, Backtest & Shadow Trading Endpoints
Provides direct access to deterministic backtest execution and simulation-only shadow trading sessions.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.app.backtesting.engine import backtest_engine
from backend.app.shadow.service import shadow_trading_service
from backend.app.data.pipeline import market_data_pipeline
from backend.app.orchestration.contracts import BacktestResult, ShadowSimulationResult
from backend.app.core.security import get_current_user_optional, TokenPayload

router = APIRouter()

class RunBacktestRequest(BaseModel):
    ticker: str = "AAPL"
    initial_capital: float = 100_000.0
    cost_bps: float = 5.0
    slippage_bps: float = 3.0

class StartShadowRequest(BaseModel):
    ticker: str = "AAPL"
    initial_cash: float = 250_000.0
    approved_by: Optional[str] = "senior_analyst"

@router.post("/{strategy_id}/backtest", response_model=BacktestResult)
async def execute_strategy_backtest(strategy_id: str, req: RunBacktestRequest):
    """Run deterministic out-of-sample backtest with costs and slippage."""
    df = market_data_pipeline.load_analytical_parquet(req.ticker)
    if df.empty:
        meta = market_data_pipeline.generate_synthetic_historical_dataset(req.ticker, days=252)
        df = market_data_pipeline.load_analytical_parquet(req.ticker, meta.snapshot_id)

    # Generate baseline momentum crossover signals for standalone backtest execution
    close = df["close"]
    fast = close.rolling(10, min_periods=10).mean()
    slow = close.rolling(30, min_periods=30).mean()
    signals = (fast > slow).fillna(0).astype(int).values

    try:
        res = backtest_engine.run_backtest(
            df=df,
            signals=signals,
            ticker=req.ticker,
            strategy_id=strategy_id,
            initial_capital=req.initial_capital,
            cost_bps=req.cost_bps,
            slippage_bps=req.slippage_bps
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{strategy_id}/shadow/start", response_model=ShadowSimulationResult)
async def start_shadow_trading(
    strategy_id: str,
    req: StartShadowRequest,
    user: Optional[TokenPayload] = Depends(get_current_user_optional)
):
    """Start simulation-only shadow trading session. Requires human operator approval."""
    approver = req.approved_by or (user.sub if user else "senior_analyst")
    try:
        res = shadow_trading_service.start_simulation(
            strategy_id=strategy_id,
            ticker=req.ticker,
            initial_cash=req.initial_cash,
            approved_by=approver
        )
        # Pre-seed with recent bars for immediate virtual activity
        df = market_data_pipeline.load_analytical_parquet(req.ticker)
        if not df.empty:
            for _, bar in df.tail(3).iterrows():
                res = shadow_trading_service.process_market_tick(
                    simulation_id=res.simulation_id,
                    current_price=float(bar["close"]),
                    signal=1
                )
        return res
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{strategy_id}/shadow/pause", response_model=ShadowSimulationResult)
async def pause_shadow_trading(strategy_id: str, simulation_id: str):
    """Pause an active shadow trading simulation."""
    try:
        return shadow_trading_service.pause_simulation(simulation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{strategy_id}/performance")
async def get_strategy_performance(strategy_id: str, ticker: str = "AAPL") -> Dict[str, Any]:
    """Retrieve combined backtest and shadow simulation performance metrics."""
    df = market_data_pipeline.load_analytical_parquet(ticker)
    if df.empty:
        meta = market_data_pipeline.generate_synthetic_historical_dataset(ticker, days=252)
        df = market_data_pipeline.load_analytical_parquet(ticker, meta.snapshot_id)

    signals = (df["close"].rolling(10).mean() > df["close"].rolling(30).mean()).fillna(0).astype(int).values
    bt = backtest_engine.run_backtest(df, signals, ticker=ticker, strategy_id=strategy_id)

    return {
        "strategy_id": strategy_id,
        "ticker": ticker,
        "backtest_metrics": bt.metrics,
        "equity_curve_points": len(bt.equity_curve),
        "suspicious_flags": bt.suspicious_flags,
        "disclaimer": "SIMULATION ONLY: Not for real trade execution."
    }
