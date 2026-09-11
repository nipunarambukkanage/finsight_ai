"""
FinSight AI - Market Data Service & Realistic Sample Data Generator
Provides high-fidelity deterministic market data for AAPL, MSFT, NVDA, GOOGL, AMZN, TSLA, and SPY.
Supports pluggable real market adapters (e.g. Polygon.io, AlphaVantage, IEX Cloud) via BaseMarketProvider interface.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import math
import numpy as np
from backend.app.models.schemas import (
    StockOverview, PriceBar, TechnicalIndicators, RiskStatistics, StockDetailResponse
)
from backend.app.analytics.engine import QuantitativeAnalyticsEngine

class BaseMarketDataProvider:
    async def get_overview(self, ticker: str) -> Optional[StockOverview]:
        raise NotImplementedError
    async def get_prices(self, ticker: str, days: int = 252) -> List[PriceBar]:
        raise NotImplementedError
    async def get_detail(self, ticker: str) -> Optional[StockDetailResponse]:
        raise NotImplementedError

class DeterministicDemoMarketProvider(BaseMarketDataProvider):
    """
    High-fidelity deterministic institutional market data provider.
    Generates realistic multi-month price paths, fundamentals, and financials for key tickers.
    """

    COMPANIES: Dict[str, Dict[str, Any]] = {
        "AAPL": {
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "base_price": 235.50,
            "market_cap": 3580000000000.0,
            "pe_ratio": 34.2,
            "forward_pe": 29.8,
            "dividend_yield": 0.44,
            "beta": 1.08,
            "week_52_high": 245.30,
            "week_52_low": 164.08,
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories, and sells a variety of related services, including AppleCare, Apple Pay, and subscription services.",
            "volatility": 0.22,
            "drift": 0.18,
            "financials": {
                "revenue_ttm": 391035000000.0,
                "gross_margin": 0.462,
                "operating_margin": 0.315,
                "net_margin": 0.240,
                "eps_ttm": 6.08,
                "fcf_ttm": 108800000000.0,
                "debt_to_equity": 1.52,
                "roe": 1.47,
                "current_ratio": 0.99
            }
        },
        "MSFT": {
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "industry": "Software - Infrastructure",
            "base_price": 428.20,
            "market_cap": 3180000000000.0,
            "pe_ratio": 36.1,
            "forward_pe": 31.4,
            "dividend_yield": 0.72,
            "beta": 0.92,
            "week_52_high": 468.35,
            "week_52_low": 309.45,
            "description": "Microsoft Corporation develops and supports software, services, devices and solutions. Its segments include Productivity and Business Processes, Intelligent Cloud, and More Personal Computing, driving massive Azure AI enterprise adoption.",
            "volatility": 0.24,
            "drift": 0.22,
            "financials": {
                "revenue_ttm": 245120000000.0,
                "gross_margin": 0.698,
                "operating_margin": 0.446,
                "net_margin": 0.354,
                "eps_ttm": 11.80,
                "fcf_ttm": 74070000000.0,
                "debt_to_equity": 0.42,
                "roe": 0.38,
                "current_ratio": 1.25
            }
        },
        "NVDA": {
            "name": "NVIDIA Corporation",
            "sector": "Technology",
            "industry": "Semiconductors",
            "base_price": 128.80,
            "market_cap": 3160000000000.0,
            "pe_ratio": 52.4,
            "forward_pe": 38.6,
            "dividend_yield": 0.03,
            "beta": 1.68,
            "week_52_high": 140.76,
            "week_52_low": 45.11,
            "description": "NVIDIA Corporation designs graphics processing units for gaming and professional markets, as well as system on a chip units for the mobile computing and automotive market. It is the dominant accelerated computing hardware and CUDA software provider powering global GenAI workloads.",
            "volatility": 0.45,
            "drift": 0.75,
            "financials": {
                "revenue_ttm": 96310000000.0,
                "gross_margin": 0.753,
                "operating_margin": 0.618,
                "net_margin": 0.534,
                "eps_ttm": 2.45,
                "fcf_ttm": 46800000000.0,
                "debt_to_equity": 0.17,
                "roe": 1.15,
                "current_ratio": 3.84
            }
        },
        "GOOGL": {
            "name": "Alphabet Inc.",
            "sector": "Communication Services",
            "industry": "Internet Content & Information",
            "base_price": 182.40,
            "market_cap": 2260000000000.0,
            "pe_ratio": 24.8,
            "forward_pe": 21.2,
            "dividend_yield": 0.44,
            "beta": 1.05,
            "week_52_high": 193.31,
            "week_52_low": 129.40,
            "description": "Alphabet Inc. offers products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America. It operates through Google Services, Google Cloud, and Other Bets, with core engines in Search, YouTube, and Gemini AI.",
            "volatility": 0.26,
            "drift": 0.28,
            "financials": {
                "revenue_ttm": 328280000000.0,
                "gross_margin": 0.574,
                "operating_margin": 0.320,
                "net_margin": 0.271,
                "eps_ttm": 7.34,
                "fcf_ttm": 69500000000.0,
                "debt_to_equity": 0.09,
                "roe": 0.29,
                "current_ratio": 2.05
            }
        },
        "AMZN": {
            "name": "Amazon.com Inc.",
            "sector": "Consumer Cyclical",
            "industry": "Internet Retail",
            "base_price": 194.20,
            "market_cap": 2040000000000.0,
            "pe_ratio": 44.5,
            "forward_pe": 33.1,
            "dividend_yield": 0.0,
            "beta": 1.14,
            "week_52_high": 201.20,
            "week_52_low": 118.35,
            "description": "Amazon.com, Inc. focuses on retail sale of consumer products and subscriptions through online and physical stores, as well as AWS cloud infrastructure, digital streaming, and advertising services.",
            "volatility": 0.29,
            "drift": 0.32,
            "financials": {
                "revenue_ttm": 604330000000.0,
                "gross_margin": 0.488,
                "operating_margin": 0.091,
                "net_margin": 0.073,
                "eps_ttm": 4.36,
                "fcf_ttm": 53000000000.0,
                "debt_to_equity": 0.58,
                "roe": 0.21,
                "current_ratio": 1.05
            }
        },
        "TSLA": {
            "name": "Tesla Inc.",
            "sector": "Consumer Cyclical",
            "industry": "Auto Manufacturers",
            "base_price": 242.10,
            "market_cap": 770000000000.0,
            "pe_ratio": 68.3,
            "forward_pe": 54.0,
            "dividend_yield": 0.0,
            "beta": 2.12,
            "week_52_high": 271.00,
            "week_52_low": 138.80,
            "description": "Tesla, Inc. designs, develops, manufactures, sells, and leases electric vehicles, energy generation and storage systems, and offers services related to its products including Full Self-Driving and AI robotics.",
            "volatility": 0.52,
            "drift": 0.15,
            "financials": {
                "revenue_ttm": 97150000000.0,
                "gross_margin": 0.182,
                "operating_margin": 0.075,
                "net_margin": 0.125,
                "eps_ttm": 3.55,
                "fcf_ttm": 3600000000.0,
                "debt_to_equity": 0.11,
                "roe": 0.21,
                "current_ratio": 1.73
            }
        },
        "SPY": {
            "name": "SPDR S&P 500 ETF Trust",
            "sector": "Index Benchmark",
            "industry": "Exchange Traded Fund",
            "base_price": 558.40,
            "market_cap": 580000000000.0,
            "pe_ratio": 27.2,
            "forward_pe": 23.5,
            "dividend_yield": 1.25,
            "beta": 1.0,
            "week_52_high": 565.16,
            "week_52_low": 420.18,
            "description": "Benchmark index tracking the performance of 500 leading large-cap U.S. equities.",
            "volatility": 0.14,
            "drift": 0.15,
            "financials": {}
        }
    }

    def __init__(self):
        self._price_cache: Dict[str, List[PriceBar]] = {}
        self._generate_all_sample_prices()

    def _generate_all_sample_prices(self):
        """Generate deterministic Geometric Brownian Motion prices for all tickers."""
        np.random.seed(42)
        end_date = datetime(2025, 1, 15)

        for ticker, meta in self.COMPANIES.items():
            days = 252
            dt = 1.0 / 252.0
            drift = meta.get("drift", 0.15)
            vol = meta.get("volatility", 0.25)
            base_p = meta.get("base_price", 100.0)


            rand_shocks = np.random.normal(0, 1, days)
            returns = (drift - 0.5 * vol**2) * dt + vol * np.sqrt(dt) * rand_shocks


            price_series = [base_p]
            for r in reversed(returns):
                prev = price_series[-1] / (1.0 + r)
                price_series.append(prev)
            price_series.reverse()
            price_series = price_series[1:]

            bars: List[PriceBar] = []
            for i, p in enumerate(price_series):
                date_str = (end_date - timedelta(days=(days - i) * 7 // 5)).strftime("%Y-%m-%d")
                daily_noise = np.random.uniform(0.005, 0.02)
                h = round(p * (1.0 + daily_noise), 2)
                l = round(p * (1.0 - daily_noise), 2)
                o = round(p * (1.0 + np.random.uniform(-0.005, 0.005)), 2)
                c = round(p, 2)
                vol_base = 25000000 if ticker != "SPY" else 65000000
                v = float(int(vol_base * np.random.uniform(0.7, 1.4)))

                bars.append(PriceBar(
                    date=date_str,
                    open=o,
                    high=max(h, o, c),
                    low=min(l, o, c),
                    close=c,
                    volume=v
                ))

            self._price_cache[ticker] = bars

    async def get_overview(self, ticker: str) -> Optional[StockOverview]:
        t = ticker.upper()
        if t not in self.COMPANIES:
            return None
        meta = self.COMPANIES[t]
        bars = self._price_cache.get(t, [])
        curr_price = bars[-1].close if bars else meta["base_price"]
        prev_price = bars[-2].close if len(bars) > 1 else curr_price
        change_pct = round(((curr_price - prev_price) / prev_price) * 100.0, 2)

        return StockOverview(
            ticker=t,
            name=meta["name"],
            sector=meta["sector"],
            industry=meta["industry"],
            current_price=curr_price,
            change_percent=change_pct,
            market_cap=meta["market_cap"],
            pe_ratio=meta.get("pe_ratio"),
            forward_pe=meta.get("forward_pe"),
            dividend_yield=meta.get("dividend_yield"),
            beta=meta.get("beta", 1.0),
            week_52_high=meta["week_52_high"],
            week_52_low=meta["week_52_low"],
            description=meta["description"]
        )

    async def get_prices(self, ticker: str, days: int = 252) -> List[PriceBar]:
        t = ticker.upper()
        bars = self._price_cache.get(t, [])
        return bars[-days:] if bars else []

    async def get_detail(self, ticker: str) -> Optional[StockDetailResponse]:
        t = ticker.upper()
        overview = await self.get_overview(t)
        if not overview:
            return None

        bars = await self.get_prices(t)
        closes = [b.close for b in bars]
        returns = QuantitativeAnalyticsEngine.calculate_daily_returns(closes)


        spy_bars = await self.get_prices("SPY")
        spy_closes = [b.close for b in spy_bars]
        spy_returns = QuantitativeAnalyticsEngine.calculate_daily_returns(spy_closes)


        ann_vol = QuantitativeAnalyticsEngine.calculate_annualized_volatility(returns)
        sharpe = QuantitativeAnalyticsEngine.calculate_sharpe_ratio(returns)
        sortino = QuantitativeAnalyticsEngine.calculate_sortino_ratio(returns)
        mdd = QuantitativeAnalyticsEngine.calculate_max_drawdown(closes)
        beta = QuantitativeAnalyticsEngine.calculate_beta(returns, spy_returns)
        var_95 = QuantitativeAnalyticsEngine.calculate_var(returns, 0.95, "historical")
        var_99 = QuantitativeAnalyticsEngine.calculate_var(returns, 0.99, "historical")
        cvar_95 = QuantitativeAnalyticsEngine.calculate_cvar(returns, 0.95)


        rsi_val = QuantitativeAnalyticsEngine.calculate_rsi(closes)
        macd_dict = QuantitativeAnalyticsEngine.calculate_macd(closes)
        bb_dict = QuantitativeAnalyticsEngine.calculate_bollinger_bands(closes)
        sma_20 = round(float(np.mean(closes[-20:])), 2) if len(closes) >= 20 else None
        sma_50 = round(float(np.mean(closes[-50:])), 2) if len(closes) >= 50 else None
        sma_200 = round(float(np.mean(closes[-200:])), 2) if len(closes) >= 200 else None

        technicals = TechnicalIndicators(
            rsi=rsi_val,
            macd=macd_dict["macd"],
            macd_signal=macd_dict["macd_signal"],
            macd_hist=macd_dict["macd_hist"],
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
            bb_upper=bb_dict["bb_upper"],
            bb_middle=bb_dict["bb_middle"],
            bb_lower=bb_dict["bb_lower"]
        )

        risk_stats = RiskStatistics(
            annualized_volatility=round(ann_vol, 4),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            max_drawdown=round(mdd, 4),
            beta=round(beta, 2),
            var_95_daily=round(var_95, 4),
            var_99_daily=round(var_99, 4),
            cvar_95_daily=round(cvar_95, 4)
        )

        fundamentals = self.COMPANIES[t].get("financials", {})

        return StockDetailResponse(
            overview=overview,
            prices=bars,
            technicals=technicals,
            risk_stats=risk_stats,
            fundamentals=fundamentals,
            is_simulated=True
        )

    def get_all_tickers(self) -> List[str]:
        return [t for t in self.COMPANIES.keys() if t != "SPY"]

market_data_service = DeterministicDemoMarketProvider()
