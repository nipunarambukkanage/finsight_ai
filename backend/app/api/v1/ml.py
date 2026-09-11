from fastapi import APIRouter, HTTPException, Depends
from backend.app.models.schemas import MLTrainRequest, MLMetrics
from backend.app.ml.engine import MachineLearningStockEngine
from backend.app.services.market_data import market_data_service
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()

@router.post("/train", response_model=MLMetrics)
async def train_ml_model(req: MLTrainRequest, user: TokenPayload = Depends(get_current_user)):
    """
    Train and evaluate a time-series machine learning model with strict temporal splitting.
    Never shuffles historical time-series data to ensure zero look-ahead bias.
    """
    bars = await market_data_service.get_prices(req.ticker)
    if not bars or len(bars) < 50:
        raise HTTPException(status_code=400, detail=f"Insufficient historical bars for ticker {req.ticker}.")

    return MachineLearningStockEngine.train_and_evaluate(
        price_bars=bars,
        model_type=req.model_type,
        test_size=req.test_size,
        horizon_days=req.prediction_horizon_days
    )
