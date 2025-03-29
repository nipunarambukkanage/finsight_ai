from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.app.models.schemas import QuantRequest, QuantAnalyticsResponse, CorrelationMatrixResponse
from backend.app.services.market_data import market_data_service
from backend.app.analytics.engine import QuantitativeAnalyticsEngine

router = APIRouter()

@router.post("/calculate", response_model=QuantAnalyticsResponse)
async def calculate_quant_analytics(req: QuantRequest):
    """Compute risk statistics, correlation matrix, and cumulative returns across selected tickers."""
    tickers = [t.upper() for t in req.tickers]
    metrics_dict = {}
    returns_dict = {}
    cum_returns_dict = {}

    for t in tickers:
        detail = await market_data_service.get_detail(t)
        if detail:
            metrics_dict[t] = detail.risk_stats
            closes = [b.close for b in detail.prices]
            rets = QuantitativeAnalyticsEngine.calculate_daily_returns(closes)
            returns_dict[t] = rets
            cum_rets = QuantitativeAnalyticsEngine.calculate_cumulative_returns(rets)
            cum_returns_dict[t] = [
                {"date": detail.prices[i+1].date, "return": round(float(cum_rets[i]), 4)}
                for i in range(len(cum_rets))
            ]

    corr_res = QuantitativeAnalyticsEngine.calculate_correlation_matrix(tickers, returns_dict)

    return QuantAnalyticsResponse(
        tickers=tickers,
        metrics=metrics_dict,
        correlation_matrix=CorrelationMatrixResponse(**corr_res),
        cumulative_returns=cum_returns_dict
    )
