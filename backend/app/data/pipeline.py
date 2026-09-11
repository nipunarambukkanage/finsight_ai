"""
FinSight AI - Reproducible Market Data Pipeline
Pipeline: Source Data -> Raw -> Cleaned -> Analytical Parquet -> Research & Backtesting.
"""

from typing import List, Optional, Iterator
import os
import uuid
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from pathlib import Path

from backend.app.data.schemas import (
    DataProvenance, RawPriceRecord, CleanedPriceRecord, DatasetSnapshotMetadata
)
from backend.app.core.logging import logger

DATA_DIR = Path("data/analytical")

class MarketDataPipeline:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or DATA_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def clean_records(
        self,
        records: List[RawPriceRecord],
        provenance: DataProvenance = DataProvenance.SYNTHETIC,
        snapshot_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Cleans raw price records:
        - Parses & normalizes timestamps to UTC
        - Eliminates duplicates
        - Sorts chronologically
        - Validates positive OHLC values
        - Quarantines malformed bars without inventing missing observations
        """
        if not records:
            return pd.DataFrame()

        snap_id = snapshot_id or f"snap-{uuid.uuid4().hex[:8]}"

        rows = []
        rejected = 0
        for r in records:

            try:
                if isinstance(r.timestamp, str):
                    ts = pd.to_datetime(r.timestamp, utc=True)
                else:
                    ts = pd.to_datetime(r.timestamp, unit='s', utc=True)
                if pd.isna(ts):
                    rejected += 1
                    continue
            except Exception:
                rejected += 1
                continue

            try:
                open_p, high_p, low_p, close_p, volume = map(float, (r.open, r.high, r.low, r.close, r.volume))
                if not np.isfinite([open_p, high_p, low_p, close_p, volume]).all() or min(open_p, high_p, low_p, close_p) <= 0 or volume < 0:
                    rejected += 1
                    continue
                if high_p < max(open_p, close_p) or low_p > min(open_p, close_p):
                    rejected += 1
                    continue
            except (TypeError, ValueError):
                rejected += 1
                continue
            rows.append({
                "ticker": r.ticker.upper(), "timestamp": ts,
                "open": open_p, "high": high_p, "low": low_p, "close": close_p,
                "volume": volume, "provenance": provenance.value, "snapshot_id": snap_id
            })

        df = pd.DataFrame(rows)
        if df.empty:
            return df
        if rejected:
            logger.warning("Quarantined %d malformed market bars", rejected)


        df = df.drop_duplicates(subset=["ticker", "timestamp"])


        df = df.sort_values(by="timestamp").reset_index(drop=True)




        df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
        df["volume"] = df["volume"].fillna(0.0)


        df["high"] = df[["open", "high", "low", "close"]].max(axis=1)
        df["low"] = df[["open", "high", "low", "close"]].min(axis=1)

        return df

    def save_analytical_parquet(
        self,
        df: pd.DataFrame,
        ticker: str,
        snapshot_id: str,
        provenance: DataProvenance = DataProvenance.SYNTHETIC
    ) -> DatasetSnapshotMetadata:
        """Persist cleaned analytical data to Parquet partitioned by ticker."""
        ticker = ticker.upper()
        ticker_dir = self.storage_dir / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)

        file_path = ticker_dir / f"{snapshot_id}.parquet"
        df.to_parquet(file_path, engine="pyarrow", index=False)

        start_date = df["timestamp"].min().strftime("%Y-%m-%d")
        end_date = df["timestamp"].max().strftime("%Y-%m-%d")

        meta = DatasetSnapshotMetadata(
            snapshot_id=snapshot_id,
            ticker=ticker,
            record_count=len(df),
            start_date=start_date,
            end_date=end_date,
            provenance=provenance,
            parquet_path=str(file_path)
        )
        logger.info(f"Saved analytical dataset snapshot {snapshot_id} for {ticker} ({len(df)} bars) to {file_path}")
        return meta

    def load_analytical_parquet(self, ticker: str, snapshot_id: Optional[str] = None) -> pd.DataFrame:
        """Loads historical analytical data from Parquet."""
        ticker = ticker.upper()
        ticker_dir = self.storage_dir / ticker
        if not ticker_dir.exists():
            return pd.DataFrame()

        if snapshot_id:
            file_path = ticker_dir / f"{snapshot_id}.parquet"
            if file_path.exists():
                return pd.read_parquet(file_path, engine="pyarrow")


        parquet_files = sorted(ticker_dir.glob("*.parquet"), key=os.path.getmtime, reverse=True)
        if parquet_files:
            return pd.read_parquet(parquet_files[0], engine="pyarrow")
        return pd.DataFrame()

    def generate_synthetic_historical_dataset(
        self,
        ticker: str,
        days: int = 252,
        base_price: float = 150.0,
        volatility: float = 0.25,
        drift: float = 0.15
    ) -> DatasetSnapshotMetadata:
        """Generates deterministic synthetic geometric Brownian motion analytical dataset and persists to Parquet."""
        seed = sum(ord(c) for c in ticker)
        rng = np.random.RandomState(seed)
        dt = 1.0 / 252.0

        dates = pd.date_range(end=datetime.now(timezone.utc), periods=days, freq="B")
        prices = [base_price]
        for _ in range(1, days):
            dW = rng.normal(0, np.sqrt(dt))
            ret = (drift - 0.5 * volatility**2) * dt + volatility * dW
            prices.append(prices[-1] * np.exp(ret))

        raw_records = []
        for i, dt_val in enumerate(dates):
            close_p = prices[i]
            day_vol = rng.uniform(0.005, 0.02) * close_p
            high_p = close_p + day_vol
            low_p = max(0.5, close_p - day_vol)
            open_p = low_p + rng.uniform(0.2, 0.8) * (high_p - low_p)
            volume = float(rng.randint(5_000_000, 80_000_000))

            raw_records.append(RawPriceRecord(
                ticker=ticker,
                timestamp=dt_val.isoformat(),
                open=round(open_p, 2),
                high=round(high_p, 2),
                low=round(low_p, 2),
                close=round(close_p, 2),
                volume=volume
            ))

        snap_id = f"synth-{ticker.lower()}-{uuid.uuid4().hex[:6]}"
        df = self.clean_records(raw_records, provenance=DataProvenance.SYNTHETIC, snapshot_id=snap_id)
        return self.save_analytical_parquet(df, ticker=ticker, snapshot_id=snap_id, provenance=DataProvenance.SYNTHETIC)

    def replay_dataset(self, df: pd.DataFrame) -> Iterator[CleanedPriceRecord]:
        """Replay mode: yields cleaned price records chronologically for simulation."""
        for _, row in df.iterrows():
            yield CleanedPriceRecord(
                ticker=row["ticker"],
                timestamp=row["timestamp"].to_pydatetime() if hasattr(row["timestamp"], "to_pydatetime") else row["timestamp"],
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
                provenance=DataProvenance(row.get("provenance", DataProvenance.REPLAYED.value)),
                snapshot_id=str(row.get("snapshot_id", "snap-replay"))
            )

market_data_pipeline = MarketDataPipeline()
