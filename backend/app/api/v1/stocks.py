from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.app.models.schemas import StockOverview, PriceBar, StockDetailResponse
from backend.app.services.market_data import market_data_service

router = APIRouter()

@router.get("/", response_model=List[StockOverview])
async def list_stocks():
    """Retrieve market overview for all tracked tickers."""
    tickers = market_data_service.get_all_tickers()
    results = []
    for t in tickers:
        ov = await market_data_service.get_overview(t)
        if ov:
            results.append(ov)
    return results

@router.get("/{ticker}", response_model=StockDetailResponse)
async def get_stock_detail(ticker: str):
    """Retrieve granular stock detail, historical prices, technical indicators, and fundamentals."""
    detail = await market_data_service.get_detail(ticker)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Stock ticker '{ticker.upper()}' not found in coverage universe.")
    return detail

@router.get("/{ticker}/prices", response_model=List[PriceBar])
async def get_stock_prices(ticker: str, days: int = Query(252, ge=10, le=500)):
    """Retrieve historical daily OHLCV bars for price chart visualization."""
    bars = await market_data_service.get_prices(ticker, days=days)
    if not bars:
        raise HTTPException(status_code=404, detail=f"Price history for '{ticker.upper()}' not available.")
    return bars
