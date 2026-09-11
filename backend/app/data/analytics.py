"""Columnar analytics adapter for Parquet snapshots.

Assessment calculations stay in Pandas for transparent fixtures. Platform
scale summaries use DuckDB SQL over Parquet and can be switched to Polars for
lazy pipelines without changing the application contract.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def summarize_parquet(path: str | Path) -> dict[str, Any]:
    """Return a deterministic snapshot summary without loading all rows in memory."""
    parquet_path = str(Path(path))
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("Install requirements-analytics.txt for DuckDB Parquet analytics") from exc
    connection = duckdb.connect(database=":memory:")
    try:
        row = connection.execute(
            "SELECT COUNT(*) AS record_count, MIN(timestamp) AS start_timestamp, "
            "MAX(timestamp) AS end_timestamp, AVG(close) AS mean_close "
            "FROM read_parquet(?)",
            [parquet_path],
        ).fetchone()
    finally:
        connection.close()
    return {"record_count": int(row[0]), "start_timestamp": str(row[1]), "end_timestamp": str(row[2]), "mean_close": float(row[3]) if row[3] is not None else None, "engine": "duckdb"}


def lazy_columns(path: str | Path, columns: list[str]):
    """Build a Polars lazy scan for callers that need a larger transformation graph."""
    try:
        import polars as pl
    except ImportError as exc:
        raise RuntimeError("Install requirements-analytics.txt for Polars lazy analytics") from exc
    return pl.scan_parquet(str(Path(path))).select(columns)
