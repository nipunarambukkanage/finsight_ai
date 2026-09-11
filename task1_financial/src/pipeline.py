"""Real-data Task 1 pipeline with an explicit deterministic demo adapter.

The live adapter is the default. Demo data is labelled in provenance and can
only be selected explicitly or when ``allow_demo_fallback`` is enabled.
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd

from .contracts import DataProvenance, EquitySnapshot

logger = logging.getLogger(__name__)


def _safe_float(value: Any) -> Optional[float]:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def _sha256_frame(frame: pd.DataFrame) -> str:
    payload = frame.to_csv(index=True, date_format="%Y-%m-%dT%H:%M:%S%z").encode()
    return hashlib.sha256(payload).hexdigest()


def wilder_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """RSI using Wilder's initial mean and recursive smoothing."""
    prices = pd.to_numeric(prices, errors="coerce")
    delta = prices.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean()
    for i in range(period, len(prices)):
        if pd.notna(avg_gain.iloc[i - 1]):
            avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period
    result = pd.Series(np.nan, index=prices.index, dtype=float)
    zero_loss = avg_loss.eq(0) & avg_gain.gt(0)
    flat = avg_loss.eq(0) & avg_gain.eq(0)
    rs = avg_gain / avg_loss.replace(0, np.nan)
    result.loc[:] = 100.0 - 100.0 / (1.0 + rs)
    result[zero_loss] = 100.0
    result[flat] = 50.0
    return result


def add_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    """Add assessment indicators without TA-Lib/pandas-ta."""
    result = frame.copy()
    close = pd.to_numeric(result["close"], errors="coerce")
    result["sma_50"] = close.rolling(50, min_periods=50).mean()
    result["sma_200"] = close.rolling(200, min_periods=200).mean()
    result["rsi_14"] = wilder_rsi(close, 14)
    ema12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
    result["macd"] = ema12 - ema26
    result["macd_signal"] = result["macd"].ewm(span=9, adjust=False, min_periods=9).mean()
    result["macd_hist"] = result["macd"] - result["macd_signal"]
    result["bb_middle"] = close.rolling(20, min_periods=20).mean()
    result["bb_std"] = close.rolling(20, min_periods=20).std(ddof=0)
    result["bb_upper"] = result["bb_middle"] + 2.0 * result["bb_std"]
    result["bb_lower"] = result["bb_middle"] - 2.0 * result["bb_std"]
    return result


def momentum_signal(row: pd.Series) -> str:
    values = [row.get(key) for key in ("sma_50", "sma_200", "rsi_14", "macd", "macd_signal")]
    if any(pd.isna(value) for value in values):
        return "INSUFFICIENT_DATA"
    score = int(row["sma_50"] > row["sma_200"]) + int(row["macd"] > row["macd_signal"])
    score += int(45 <= row["rsi_14"] <= 70) - int(row["rsi_14"] > 75 or row["rsi_14"] < 30)
    return "BULLISH" if score >= 2 else "BEARISH" if score <= 0 else "NEUTRAL"


@dataclass
class MarketDataResult:
    bars: pd.DataFrame
    info: dict[str, Any]
    news: list[dict[str, Any]]
    provenance: DataProvenance
    limitations: list[str]


class YFinanceMarketAdapter:
    """Fetches live prices/news and normalizes library-version differences."""

    def fetch(self, ticker: str, years: int = 2, allow_demo_fallback: bool = False) -> MarketDataResult:
        ticker = ticker.strip().upper()
        limitations: list[str] = []
        try:
            import yfinance as yf

            end = datetime.now(timezone.utc).date() + timedelta(days=1)
            start = end - timedelta(days=365 * years + 3)
            raw = yf.download(
                ticker, start=start.isoformat(), end=end.isoformat(), interval="1d",
                auto_adjust=False, actions=True, progress=False, threads=False,
            )
            if raw is None or raw.empty:
                raise ValueError("provider returned no OHLCV rows")
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = [column[0] for column in raw.columns]
            columns = {str(column).lower().replace(" ", "_"): column for column in raw.columns}
            frame = pd.DataFrame(index=pd.to_datetime(raw.index, utc=True))
            for name in ("open", "high", "low", "close", "volume"):
                source = columns.get(name)
                if source is None:
                    raise ValueError(f"missing provider column: {name}")
                frame[name] = pd.to_numeric(raw[source], errors="coerce")



            for name in ("adj_close", "dividends", "stock_splits"):
                source = columns.get(name)
                if source is not None:
                    values = pd.to_numeric(raw[source], errors="coerce")
                    frame[name] = values.fillna(0.0) if name in {"dividends", "stock_splits"} else values
            before_clean = len(frame)
            frame = frame.dropna(subset=["open", "high", "low", "close", "volume"]).sort_index()
            frame = frame[(frame[["open", "high", "low", "close"]] > 0).all(axis=1)]
            frame = frame[frame["volume"] >= 0]
            quarantined = before_clean - len(frame)
            if quarantined:
                limitations.append(f"Quarantined {quarantined} malformed or incomplete OHLCV bars; no values were filled.")
            if len(frame) < 200:
                limitations.append(f"Only {len(frame)} valid bars were returned; 200-day indicators may be unavailable.")
            info: dict[str, Any] = {}
            try:
                info = yf.Ticker(ticker).info or {}
            except Exception as exc:
                limitations.append(f"Valuation metadata unavailable: {exc}")
            try:
                news = self._news(yf.Ticker(ticker).news or [])
            except Exception as exc:
                news = []
                limitations.append(f"Provider news unavailable: {exc}")
            if len(news) < 10:
                news = self._merge_news(news, self._rss_news(ticker))
            if len(news) < 10:
                limitations.append(f"Only {len(news)} distinct recent headlines were returned; assessment target is 10.")
            analytical_field = "adj_close" if "adj_close" in frame.columns else "close"
            action_columns = [name for name in ("dividends", "stock_splits") if name in frame.columns]
            action_hash = _sha256_frame(frame[action_columns]) if action_columns else None
            provenance = DataProvenance(
                provider="yfinance", ticker=ticker, retrieved_at=datetime.now(timezone.utc),
                start_date=str(frame.index.min().date()) if not frame.empty else None,
                end_date=str(frame.index.max().date()) if not frame.empty else None,
                adjusted=analytical_field == "adj_close",
                price_adjustment_policy="auto_adjust=False; adj_close retained for analytics",
                analytical_price_field=analytical_field,
                corporate_actions_sha256=action_hash,
                data_mode="live", dataset_sha256=_sha256_frame(frame),
            )
            return MarketDataResult(frame, info, news, provenance, limitations)
        except Exception as exc:
            if not allow_demo_fallback:
                logger.warning("Live market data failed for %s: %s", ticker, exc)
                return MarketDataResult(pd.DataFrame(), {}, [], DataProvenance(
                    provider="yfinance", ticker=ticker, retrieved_at=datetime.now(timezone.utc),
                    data_mode="live", adjusted=False,
                ), [f"Live provider unavailable: {exc}"])
            logger.warning("Using explicitly labelled demo fallback for %s: %s", ticker, exc)
            return self.demo(ticker, years)

    @staticmethod
    def _news(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in items:
            title = str(item.get("title") or item.get("content", {}).get("title") or "").strip()
            if not title or title.lower() in seen:
                continue
            seen.add(title.lower())
            normalized.append({
                "headline": title,
                "publisher": item.get("publisher") or item.get("content", {}).get("provider", {}).get("displayName"),
                "published_at": item.get("providerPublishTime") or item.get("content", {}).get("pubDate"),
                "url": item.get("link") or item.get("content", {}).get("canonicalUrl", {}).get("url"),
            })
        return normalized

    @staticmethod
    def _rss_news(ticker: str) -> list[dict[str, Any]]:
        try:
            import feedparser
            parsed = feedparser.parse(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US")
            return [{"headline": entry.get("title", ""), "publisher": "Yahoo Finance RSS", "published_at": entry.get("published"), "url": entry.get("link")} for entry in parsed.entries]
        except Exception as exc:
            logger.info("RSS fallback unavailable for %s: %s", ticker, exc)
            return []

    @staticmethod
    def _merge_news(primary: list[dict[str, Any]], secondary: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged, seen = [], set()
        for item in [*primary, *secondary]:
            key = str(item.get("headline", "")).strip().lower()
            if key and key not in seen:
                seen.add(key); merged.append(item)
        return merged

    @staticmethod
    def demo(ticker: str, years: int = 2) -> MarketDataResult:
        index = pd.bdate_range(end=pd.Timestamp.now(tz="UTC").normalize(), periods=365 * years)
        seed = int.from_bytes(hashlib.sha256(ticker.encode("utf-8")).digest()[:8], "big") % 2**32
        rng = np.random.default_rng(seed)
        close = 100.0 * np.exp(np.cumsum(rng.normal(0.00035, 0.018, len(index))))
        frame = pd.DataFrame({"close": close}, index=index)
        frame["open"] = frame["close"].shift(1).fillna(frame["close"])
        frame["high"] = frame[["open", "close"]].max(axis=1) * 1.006
        frame["low"] = frame[["open", "close"]].min(axis=1) * 0.994
        frame["volume"] = rng.integers(1_000_000, 20_000_000, len(index))
        info = {"symbol": ticker, "shortName": f"{ticker} Demo Corporation", "trailingPE": None}
        demo_headlines = [
            f"{ticker} reports strong growth in its latest demo quarter",
            f"Analysts assess {ticker} competition and margin risk",
            f"{ticker} announces record operating cash flow in demo filing",
            f"Supply chain updates add uncertainty for {ticker}",
            f"{ticker} outlook remains stable amid market volatility",
            f"Regulatory review could affect {ticker} expansion plans",
            f"{ticker} shares hold near the upper end of the demo range",
            f"Customer demand supports {ticker} service revenue growth",
            f"Cybersecurity investment remains a priority for {ticker}",
            f"{ticker} management reiterates disciplined capital allocation",
        ]
        news = [{"headline": headline, "publisher": "FinSight deterministic demo", "published_at": str(index.date()), "url": None} for headline, index in zip(demo_headlines, index[-10:])]
        provenance = DataProvenance(
            provider="deterministic-demo", ticker=ticker, retrieved_at=datetime.now(timezone.utc),
            start_date=str(index.min().date()), end_date=str(index.max().date()),
            adjusted=False, price_adjustment_policy="deterministic synthetic raw close",
            analytical_price_field="close", data_mode="demo", dataset_sha256=_sha256_frame(frame),
        )
        return MarketDataResult(frame, info, news, provenance, ["Synthetic demo data; no live provider response was available."])


def build_snapshot(result: MarketDataResult, evaluation_date: Optional[pd.Timestamp] = None) -> EquitySnapshot:
    if result.bars.empty:
        return EquitySnapshot(ticker=result.provenance.ticker, provenance=result.provenance, limitations=result.limitations)
    analytical = result.bars.copy()
    if "adj_close" in analytical.columns and analytical["adj_close"].notna().any():
        analytical["close"] = analytical["adj_close"].where(analytical["adj_close"].notna(), analytical["close"])
    frame = add_indicators(analytical)
    today = pd.Timestamp(evaluation_date) if evaluation_date is not None else frame.index.max()
    today = today.tz_localize("UTC") if today.tzinfo is None else today.tz_convert("UTC")
    frame = frame[frame.index <= today]
    if frame.empty:
        return EquitySnapshot(ticker=result.provenance.ticker, provenance=result.provenance,
                              limitations=[*result.limitations, "Evaluation date precedes the available observation range."])
    trailing = frame[frame.index >= today - pd.Timedelta(days=365)]
    year_start = pd.Timestamp(year=today.year, month=1, day=1, tz="UTC")
    prior = frame[frame.index < year_start]
    last = frame.iloc[-1]
    ytd = None if prior.empty else _safe_float((last["close"] / prior.iloc[-1]["close"]) - 1.0)
    indicators = {key: _safe_float(last.get(key)) for key in (
        "sma_50", "sma_200", "rsi_14", "macd", "macd_signal", "macd_hist",
        "bb_upper", "bb_middle", "bb_lower",
    )}
    pe = _safe_float(result.info.get("trailingPE") or result.info.get("trailingPe"))
    if pe is None:
        limitations = [*result.limitations, "Valuation metadata did not include a usable trailing P/E ratio."]
    else:
        limitations = result.limitations
    return EquitySnapshot(
        ticker=result.provenance.ticker, current_price=_safe_float(last["close"]),
        week_52_high=_safe_float(trailing["high"].max()), week_52_low=_safe_float(trailing["low"].min()),
        pe_ratio=pe, ytd_return=ytd, momentum_signal=momentum_signal(last), indicators=indicators,
        headlines=result.news[:10], provenance=result.provenance, limitations=limitations,
    )
