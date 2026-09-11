"""
FinSight AI - Quantitative Financial Analytics Engine
Implements deterministic, production-grade quantitative finance formulas:
- Daily & Cumulative Returns
- Annualized & Rolling Volatility
- Sharpe Ratio & Sortino Ratio
- Maximum Drawdown (MDD)
- Beta (vs Market Benchmark)
- Correlation & Covariance Matrix
- Historical & Parametric Value at Risk (VaR 95% / 99%)
- Expected Shortfall / Conditional VaR (CVaR)
- Technical Indicators: RSI (14), MACD (12, 26, 9), Bollinger Bands (20, 2 std)
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd

class QuantitativeAnalyticsEngine:

    @staticmethod
    def calculate_daily_returns(prices: List[float]) -> np.ndarray:
        """Calculate percentage daily returns from a price series."""
        if len(prices) < 2:
            return np.array([])
        p = np.array(prices, dtype=np.float64)
        returns = (p[1:] - p[:-1]) / p[:-1]
        return returns

    @staticmethod
    def calculate_cumulative_returns(returns: np.ndarray) -> np.ndarray:
        """Calculate cumulative compound returns from daily returns."""
        if len(returns) == 0:
            return np.array([])
        return np.cumprod(1.0 + returns) - 1.0

    @staticmethod
    def calculate_annualized_volatility(returns: np.ndarray, trading_days: int = 252) -> float:
        """
        Calculate annualized volatility from daily returns.
        Formula: sigma_ann = sigma_daily * sqrt(252)
        """
        if len(returns) < 2:
            return 0.0
        daily_std = float(np.std(returns, ddof=1))
        return float(daily_std * np.sqrt(trading_days))

    @staticmethod
    def calculate_rolling_volatility(prices: List[float], window: int = 20, trading_days: int = 252) -> List[float]:
        """Calculate rolling annualized volatility over a given window."""
        if len(prices) <= window:
            return [0.0] * len(prices)
        returns = pd.Series(prices).pct_change().dropna()
        rolling_std = returns.rolling(window=window).std() * np.sqrt(trading_days)
        result = [0.0] * (len(prices) - len(rolling_std)) + [0.0 if np.isnan(x) else round(float(x), 4) for x in rolling_std]
        return result

    @staticmethod
    def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.04, trading_days: int = 252) -> float:
        """
        Calculate annualized Sharpe Ratio.
        Formula: (Annualized Return - Risk Free Rate) / Annualized Volatility
        """
        if len(returns) < 2:
            return 0.0
        ann_return = float(np.mean(returns) * trading_days)
        ann_vol = float(np.std(returns, ddof=1) * np.sqrt(trading_days))
        if ann_vol == 0:
            return 0.0
        return float((ann_return - risk_free_rate) / ann_vol)

    @staticmethod
    def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.04, trading_days: int = 252) -> float:
        """
        Calculate Sortino Ratio measuring return against downside volatility.
        Formula: (Annualized Return - Risk Free Rate) / Annualized Downside Deviation
        """
        if len(returns) < 2:
            return 0.0
        ann_return = float(np.mean(returns) * trading_days)
        downside_returns = returns[returns < 0]
        if len(downside_returns) < 2:
            return 0.0
        downside_dev = float(np.std(downside_returns, ddof=1) * np.sqrt(trading_days))
        if downside_dev == 0:
            return 0.0
        return float((ann_return - risk_free_rate) / downside_dev)

    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> float:
        """
        Calculate Maximum Drawdown (MDD) from peak to trough.
        Formula: max((Peak - Price) / Peak)
        """
        if len(prices) < 2:
            return 0.0
        p = np.array(prices, dtype=np.float64)
        peak = np.maximum.accumulate(p)
        drawdowns = (p - peak) / peak
        return float(np.min(drawdowns))

    @staticmethod
    def calculate_beta(asset_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
        """
        Calculate asset Beta relative to benchmark.
        Formula: Cov(asset, benchmark) / Var(benchmark)
        """
        min_len = min(len(asset_returns), len(benchmark_returns))
        if min_len < 2:
            return 1.0
        r_a = asset_returns[-min_len:]
        r_b = benchmark_returns[-min_len:]
        var_b = np.var(r_b, ddof=1)
        if var_b == 0:
            return 1.0
        cov_ab = np.cov(r_a, r_b)[0, 1]
        return float(cov_ab / var_b)

    @staticmethod
    def calculate_correlation_matrix(tickers: List[str], returns_dict: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Calculate pairwise Pearson correlation matrix among ticker daily returns."""
        min_len = min((len(r) for r in returns_dict.values() if len(r) > 0), default=0)
        if min_len < 2:
            size = len(tickers)
            return {"tickers": tickers, "matrix": np.eye(size).tolist()}

        df = pd.DataFrame({t: returns_dict[t][-min_len:] for t in tickers if t in returns_dict})
        corr_matrix = df.corr().fillna(0.0).values.tolist()
        return {
            "tickers": tickers,
            "matrix": [[round(val, 4) for val in row] for row in corr_matrix]
        }

    @staticmethod
    def calculate_var(returns: np.ndarray, confidence: float = 0.95, method: str = "historical") -> float:
        """
        Calculate 1-day Value at Risk (VaR).
        Returned as positive percentage representing maximum potential loss at confidence level.
        """
        if len(returns) < 5:
            return 0.0
        if method == "historical":

            percentile = (1.0 - confidence) * 100.0
            var_val = -np.percentile(returns, percentile)
            return float(max(0.0, var_val))
        elif method == "parametric":
            mean = np.mean(returns)
            std = np.std(returns, ddof=1)

            z = 1.64485 if abs(confidence - 0.95) < 0.01 else 2.32635
            var_val = -(mean - z * std)
            return float(max(0.0, var_val))
        return 0.0

    @staticmethod
    def calculate_cvar(returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Calculate Expected Shortfall (Conditional VaR, CVaR).
        Average loss conditioned on loss being strictly greater than VaR.
        """
        if len(returns) < 5:
            return 0.0
        percentile = (1.0 - confidence) * 100.0
        cutoff = np.percentile(returns, percentile)
        tail_losses = returns[returns <= cutoff]
        if len(tail_losses) == 0:
            return float(max(0.0, -cutoff))
        return float(max(0.0, -np.mean(tail_losses)))

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI).
        Standard Wilder formula with smoothing.
        """
        if len(prices) <= period:
            return None
        series = pd.Series(prices, dtype=np.float64)
        delta = series.diff().dropna()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()


        for i in range(period, len(gain)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period

        rs = avg_gain / avg_loss.replace(0, 1e-9)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        last_val = rsi.iloc[-1]
        return round(float(last_val), 2) if not np.isnan(last_val) else 50.0

    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Optional[float]]:
        """
        Calculate MACD, Signal line, and MACD Histogram.
        """
        if len(prices) <= slow + signal:
            return {"macd": None, "macd_signal": None, "macd_hist": None}
        s = pd.Series(prices, dtype=np.float64)
        ema_fast = s.ewm(span=fast, adjust=False).mean()
        ema_slow = s.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        macd_hist = macd_line - signal_line

        return {
            "macd": round(float(macd_line.iloc[-1]), 4),
            "macd_signal": round(float(signal_line.iloc[-1]), 4),
            "macd_hist": round(float(macd_hist.iloc[-1]), 4)
        }

    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, num_std: float = 2.0) -> Dict[str, Optional[float]]:
        """
        Calculate Bollinger Bands (Upper, Middle, Lower).
        """
        if len(prices) < period:
            return {"bb_upper": None, "bb_middle": None, "bb_lower": None}
        s = pd.Series(prices, dtype=np.float64)
        middle = s.rolling(window=period).mean()
        std = s.rolling(window=period).std()
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)

        return {
            "bb_upper": round(float(upper.iloc[-1]), 2),
            "bb_middle": round(float(middle.iloc[-1]), 2),
            "bb_lower": round(float(lower.iloc[-1]), 2)
        }

    @staticmethod
    def calculate_hit_rate(trade_pnls: List[float]) -> float:
        """Calculate hit rate (% winning trades)."""
        if not trade_pnls:
            return 0.0
        wins = sum(1 for p in trade_pnls if p > 0)
        return round(float(wins / len(trade_pnls)), 4)

    @staticmethod
    def calculate_turnover(total_volume_traded: float, portfolio_value: float) -> float:
        """Calculate annualized portfolio turnover ratio."""
        if portfolio_value <= 0:
            return 0.0
        return round(float(total_volume_traded / portfolio_value), 4)

    @staticmethod
    def calculate_exposure(long_val: float, short_val: float, portfolio_value: float) -> Dict[str, float]:
        """Calculate gross and net portfolio exposure percentages."""
        if portfolio_value <= 0:
            return {"gross_exposure": 0.0, "net_exposure": 0.0}
        gross = (abs(long_val) + abs(short_val)) / portfolio_value
        net = (long_val - abs(short_val)) / portfolio_value
        return {
            "gross_exposure": round(float(gross), 4),
            "net_exposure": round(float(net), 4)
        }

    @staticmethod
    def calculate_transaction_costs(trade_value: float, bps: float = 5.0) -> float:
        """Calculate transaction costs based on basis points."""
        return round(float(trade_value * (bps / 10000.0)), 2)

    @staticmethod
    def calculate_slippage(trade_value: float, slippage_bps: float = 3.0) -> float:
        """Calculate estimated slippage impact."""
        return round(float(trade_value * (slippage_bps / 10000.0)), 2)

    @staticmethod
    def calculate_exchange_fees(shares: float, fee_per_share: float = 0.005) -> float:
        """Calculate exchange and clearing fees per share."""
        return round(float(shares * fee_per_share), 2)

    @staticmethod
    def calculate_trade_pnl(
        entry_price: float,
        exit_price: float,
        shares: float,
        is_long: bool = True,
        costs: float = 0.0
    ) -> Dict[str, float]:
        """Calculate trade-level gross and net P&L."""
        if is_long:
            gross_pnl = (exit_price - entry_price) * shares
        else:
            gross_pnl = (entry_price - exit_price) * shares
        net_pnl = gross_pnl - costs
        ret_pct = (net_pnl / (entry_price * shares)) if (entry_price * shares) > 0 else 0.0
        return {
            "gross_pnl": round(float(gross_pnl), 2),
            "net_pnl": round(float(net_pnl), 2),
            "return_pct": round(float(ret_pct), 4),
            "costs": round(float(costs), 2)
        }

    @staticmethod
    def calculate_benchmark_comparison(
        strategy_returns: np.ndarray,
        benchmark_returns: np.ndarray,
        risk_free_rate: float = 0.04,
        trading_days: int = 252
    ) -> Dict[str, Any]:
        """Calculate Jensen's Alpha, Beta, Tracking Error, and Information Ratio."""
        min_len = min(len(strategy_returns), len(benchmark_returns))
        if min_len < 5:
            return {
                "alpha": 0.0,
                "beta": 1.0,
                "tracking_error": 0.0,
                "information_ratio": 0.0
            }
        r_s = strategy_returns[-min_len:]
        r_b = benchmark_returns[-min_len:]

        var_b = np.var(r_b, ddof=1)
        beta = float(np.cov(r_s, r_b)[0, 1] / var_b) if var_b > 0 else 1.0

        ann_rs = float(np.mean(r_s) * trading_days)
        ann_rb = float(np.mean(r_b) * trading_days)
        alpha = ann_rs - (risk_free_rate + beta * (ann_rb - risk_free_rate))

        diff = r_s - r_b
        te = float(np.std(diff, ddof=1) * np.sqrt(trading_days))
        ir = float(np.mean(diff) * trading_days / te) if te > 0 else 0.0

        return {
            "alpha": round(float(alpha), 4),
            "beta": round(float(beta), 4),
            "tracking_error": round(float(te), 4),
            "information_ratio": round(float(ir), 4)
        }
