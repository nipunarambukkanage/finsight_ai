import pytest
import numpy as np
from backend.app.analytics.engine import QuantitativeAnalyticsEngine

def test_daily_returns():
    prices = [100.0, 105.0, 102.9, 110.0]
    returns = QuantitativeAnalyticsEngine.calculate_daily_returns(prices)
    assert len(returns) == 3
    assert pytest.approx(returns[0], 0.0001) == 0.05
    assert pytest.approx(returns[1], 0.0001) == (102.9 - 105.0) / 105.0

def test_cumulative_returns():
    returns = np.array([0.05, -0.02, 0.07])
    cum_returns = QuantitativeAnalyticsEngine.calculate_cumulative_returns(returns)
    assert len(cum_returns) == 3
    expected_final = (1.05 * 0.98 * 1.07) - 1.0
    assert pytest.approx(cum_returns[-1], 0.0001) == expected_final

def test_annualized_volatility():

    constant_returns = np.array([0.01, 0.01, 0.01, 0.01, 0.01])
    vol = QuantitativeAnalyticsEngine.calculate_annualized_volatility(constant_returns)
    assert vol == 0.0


    np.random.seed(42)
    returns = np.random.normal(0.001, 0.015, 252)
    vol = QuantitativeAnalyticsEngine.calculate_annualized_volatility(returns)
    assert 0.15 < vol < 0.35

def test_sharpe_and_sortino_ratio():
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.01, 252)
    sharpe = QuantitativeAnalyticsEngine.calculate_sharpe_ratio(returns, risk_free_rate=0.04)
    assert isinstance(sharpe, float)

    sortino = QuantitativeAnalyticsEngine.calculate_sortino_ratio(returns, risk_free_rate=0.04)
    assert isinstance(sortino, float)

def test_max_drawdown():

    prices = [100.0, 110.0, 120.0, 105.0, 90.0, 115.0]
    mdd = QuantitativeAnalyticsEngine.calculate_max_drawdown(prices)
    assert pytest.approx(mdd, 0.0001) == -0.25

def test_beta():
    asset = np.array([0.02, 0.04, -0.01, 0.03, -0.02])
    bench = np.array([0.01, 0.02, -0.005, 0.015, -0.01])
    beta = QuantitativeAnalyticsEngine.calculate_beta(asset, bench)
    assert pytest.approx(beta, 0.01) == 2.0

def test_var_and_cvar():
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.015, 500)
    var_95 = QuantitativeAnalyticsEngine.calculate_var(returns, 0.95, "historical")
    var_99 = QuantitativeAnalyticsEngine.calculate_var(returns, 0.99, "historical")
    cvar_95 = QuantitativeAnalyticsEngine.calculate_cvar(returns, 0.95)

    assert var_95 > 0.0
    assert var_99 > var_95
    assert cvar_95 >= var_95

def test_rsi_bounds():

    prices = [100 + i * 2 for i in range(30)]
    rsi = QuantitativeAnalyticsEngine.calculate_rsi(prices, period=14)
    assert rsi is not None
    assert 0.0 <= rsi <= 100.0
    assert rsi > 70.0

def test_macd_and_bollinger():
    np.random.seed(42)
    prices = list(np.cumprod(1 + np.random.normal(0.001, 0.01, 60)) * 100)
    macd = QuantitativeAnalyticsEngine.calculate_macd(prices)
    assert "macd" in macd and "macd_signal" in macd and "macd_hist" in macd
    assert macd["macd"] is not None

    bb = QuantitativeAnalyticsEngine.calculate_bollinger_bands(prices)
    assert bb["bb_upper"] > bb["bb_middle"] > bb["bb_lower"]
