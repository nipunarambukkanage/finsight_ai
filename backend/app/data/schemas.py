"""
FinSight AI - Market Data & Parquet Schemas
Defines typed schemas for market data ingestion, cleaning, and analytical storage.
"""

from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

class DataProvenance(str, Enum):
    REAL = "REAL"
    SYNTHETIC = "SYNTHETIC"
    REPLAYED = "REPLAYED"
    DEMO_FALLBACK = "DEMO_FALLBACK"

class RawPriceRecord(BaseModel):
    ticker: str
    timestamp: str  # Can be ISO, epoch, or formatted string
    open: float
    high: float
    low: float
    close: float
    volume: float

class CleanedPriceRecord(BaseModel):
    ticker: str
    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    provenance: DataProvenance = DataProvenance.SYNTHETIC
    snapshot_id: str = "snap-default"

class DatasetSnapshotMetadata(BaseModel):
    snapshot_id: str
    ticker: str
    record_count: int
    start_date: str
    end_date: str
    provenance: DataProvenance
    parquet_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
