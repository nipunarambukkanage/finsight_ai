"""
FinSight AI - Deterministic Equity Backtesting Engine
Features:
- Chronological Train / Validation / Out-of-Sample Test splits
- Explicit non-anticipative trade execution (Signal_t -> Fill_{t+1})
- Transaction costs (bps), slippage (bps), and exchange fees
- Complete trade ledger and equity curve tracking
- Anomaly detection (suspicious Sharpe, impossible fills, zero-loss flags)
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
import math
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from backend.app.orchestration.contracts import BacktestResult
from backend.app.analytics.engine import QuantitativeAnalyticsEngine
from backend.app.core.logging import logger

class DeterministicBacktestEngine:

    @staticmethod
    def split_chronological(df: pd.DataFrame, train_ratio: float = 0.6, val_ratio: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Strictly chronological train/validation/out-of-sample test partitioning."""
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()
        return train_df, val_df, test_df

    @classmethod
    def run_backtest(
        cls,
        df: pd.DataFrame,
        signals: np.ndarray,
        ticker: str = "AAPL",
        strategy_id: str = "strat-1",
        version: str = "1.0.0",
        snapshot_id: str = "snap-default",
        initial_capital: float = 100_000.0,
        cost_bps: float = 5.0,
        slippage_bps: float = 3.0,
        fee_per_share: float = 0.005,
        max_position_pct: float = 0.95
    ) -> BacktestResult:
        """
        Executes a non-anticipative bar-by-bar backtest over the out-of-sample / full evaluation series.
        """
        if len(df) < 10 or len(signals) != len(df):
            raise ValueError(f"Insufficient data or signal length mismatch: df={len(df)}, signals={len(signals)}")


        train_df, val_df, test_df = cls.split_chronological(df)
        train_range = f"{train_df['timestamp'].min().strftime('%Y-%m-%d')} to {train_df['timestamp'].max().strftime('%Y-%m-%d')}"
        val_range = f"{val_df['timestamp'].min().strftime('%Y-%m-%d')} to {val_df['timestamp'].max().strftime('%Y-%m-%d')}"
        test_range = f"{test_df['timestamp'].min().strftime('%Y-%m-%d')} to {test_df['timestamp'].max().strftime('%Y-%m-%d')}"

        cash = initial_capital
        position_shares = 0.0
        equity_curve: List[Dict[str, Any]] = []
        trades: List[Dict[str, Any]] = []
        suspicious_flags: List[str] = []

        total_costs_paid = 0.0
        total_slippage_incurred = 0.0
        total_fees_paid = 0.0
        volume_traded = 0.0

        current_trade: Optional[Dict[str, Any]] = None




        eval_start = len(train_df) + len(val_df)
        for i in range(len(df)):
            row = df.iloc[i]
            ts = row["timestamp"]
            ts_str = ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts)
            close_p = float(row["close"])
            open_p = float(row["open"])
            high_p = float(row["high"])
            low_p = float(row["low"])


            if i >= eval_start and i > 0:
                sig = signals[i - 1]


                if sig > 0 and position_shares == 0.0:
                    fill_price = open_p * (1.0 + (slippage_bps / 10000.0))


                    if fill_price > high_p:
                        suspicious_flags.append(f"Entry open-plus-slippage exceeded reported high at {ts_str}")

                    target_alloc = cash * max_position_pct
                    shares_to_buy = math.floor(target_alloc / fill_price)
                    if shares_to_buy > 0:
                        trade_val = shares_to_buy * fill_price
                        comm = QuantitativeAnalyticsEngine.calculate_transaction_costs(trade_val, cost_bps)
                        fees = QuantitativeAnalyticsEngine.calculate_exchange_fees(shares_to_buy, fee_per_share)
                        slip = QuantitativeAnalyticsEngine.calculate_slippage(trade_val, slippage_bps)

                        total_cost = comm + fees
                        cash -= (trade_val + total_cost)
                        position_shares = shares_to_buy
                        total_costs_paid += comm
                        total_fees_paid += fees
                        total_slippage_incurred += slip
                        volume_traded += trade_val

                        current_trade = {
                            "trade_id": f"T-{len(trades)+1}",
                            "ticker": ticker,
                            "side": "BUY",
                            "entry_time": ts_str,
                            "entry_price": round(fill_price, 2),
                            "shares": shares_to_buy,
                            "entry_costs": round(total_cost, 2)
                        }


                elif sig <= 0 and position_shares > 0.0:
                    fill_price = open_p * (1.0 - (slippage_bps / 10000.0))
                    if fill_price < low_p:
                        suspicious_flags.append(f"Exit open-minus-slippage fell below reported low at {ts_str}")

                    trade_val = position_shares * fill_price
                    comm = QuantitativeAnalyticsEngine.calculate_transaction_costs(trade_val, cost_bps)
                    fees = QuantitativeAnalyticsEngine.calculate_exchange_fees(position_shares, fee_per_share)
                    slip = QuantitativeAnalyticsEngine.calculate_slippage(trade_val, slippage_bps)

                    total_cost = comm + fees
                    cash += (trade_val - total_cost)
                    total_costs_paid += comm
                    total_fees_paid += fees
                    total_slippage_incurred += slip
                    volume_traded += trade_val

                    if current_trade:
                        pnl_calc = QuantitativeAnalyticsEngine.calculate_trade_pnl(
                            entry_price=current_trade["entry_price"],
                            exit_price=fill_price,
                            shares=current_trade["shares"],
                            is_long=True,
                            costs=current_trade["entry_costs"] + total_cost
                        )
                        current_trade.update({
                            "exit_time": ts_str,
                            "exit_price": round(fill_price, 2),
                            "gross_pnl": pnl_calc["gross_pnl"],
                            "net_pnl": pnl_calc["net_pnl"],
                            "return_pct": pnl_calc["return_pct"],
                            "exit_costs": round(total_cost, 2),
                            "total_costs": round(current_trade["entry_costs"] + total_cost, 2)
                        })
                        trades.append(current_trade)
                        current_trade = None

                    position_shares = 0.0


            port_val = cash + (position_shares * close_p)
            equity_curve.append({
                "date": ts_str,
                "equity": round(port_val, 2),
                "cash": round(cash, 2),
                "position_shares": position_shares,
                "benchmark_price": close_p
            })


        eval_curve = equity_curve[eval_start:]
        eq_series = [e["equity"] for e in eval_curve]
        daily_rets = QuantitativeAnalyticsEngine.calculate_daily_returns(eq_series)
        bench_series = [e["benchmark_price"] for e in eval_curve]
        bench_rets = QuantitativeAnalyticsEngine.calculate_daily_returns(bench_series)


        tot_return = (eq_series[-1] - initial_capital) / initial_capital
        ann_vol = QuantitativeAnalyticsEngine.calculate_annualized_volatility(daily_rets)
        sharpe = QuantitativeAnalyticsEngine.calculate_sharpe_ratio(daily_rets)
        sortino = QuantitativeAnalyticsEngine.calculate_sortino_ratio(daily_rets)
        mdd = QuantitativeAnalyticsEngine.calculate_max_drawdown(eq_series)

        pnls = [t["net_pnl"] for t in trades if "net_pnl" in t]
        hit_rate = QuantitativeAnalyticsEngine.calculate_hit_rate(pnls)
        turnover = QuantitativeAnalyticsEngine.calculate_turnover(volume_traded, initial_capital)
        bench_comp = QuantitativeAnalyticsEngine.calculate_benchmark_comparison(daily_rets, bench_rets)


        if sharpe > 4.5:
            suspicious_flags.append(f"WARNING: Suspiciously high Sharpe Ratio ({sharpe:.2f}). Check for look-ahead bias or overfitting.")
        if len(trades) > 5 and hit_rate >= 0.95:
            suspicious_flags.append(f"WARNING: Unrealistically high hit rate ({hit_rate*100:.1f}%). Possible data leakage.")
        if mdd == 0.0 and len(trades) > 3:
            suspicious_flags.append("WARNING: Zero drawdown recorded. Invariant violation check recommended.")

        metrics = {
            "initial_capital": initial_capital,
            "ending_equity": round(eq_series[-1], 2),
            "total_return": round(float(tot_return), 4),
            "annualized_return": round(float(np.mean(daily_rets) * 252), 4) if len(daily_rets) > 0 else 0.0,
            "annualized_volatility": round(float(ann_vol), 4),
            "sharpe_ratio": round(float(sharpe), 2),
            "sortino_ratio": round(float(sortino), 2),
            "max_drawdown": round(float(mdd), 4),
            "total_trades": len(trades),
            "hit_rate": hit_rate,
            "turnover": turnover,
            "total_transaction_costs": round(float(total_costs_paid), 2),
            "total_slippage_incurred": round(float(total_slippage_incurred), 2),
            "total_exchange_fees": round(float(total_fees_paid), 2),
            "alpha": bench_comp["alpha"],
            "beta": bench_comp["beta"],
            "information_ratio": bench_comp["information_ratio"]
        }

        return BacktestResult(
            strategy_id=strategy_id,
            version=version,
            snapshot_id=snapshot_id,
            train_period=train_range,
            val_period=val_range,
            test_period=test_range,
            equity_curve=equity_curve,
            trades=trades,
            metrics=metrics,
            suspicious_flags=list(set(suspicious_flags))
        )

backtest_engine = DeterministicBacktestEngine()
