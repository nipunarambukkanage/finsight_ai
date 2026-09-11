from fastapi import APIRouter, Depends
from backend.app.models.schemas import MultimodalAnalyzeRequest, MultimodalAnalyzeResponse
from backend.app.services.multimodal import multimodal_service
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()

@router.post("/analyze", response_model=MultimodalAnalyzeResponse)
async def analyze_financial_image(req: MultimodalAnalyzeRequest, user: TokenPayload = Depends(get_current_user)):
    """Analyze financial candlestick charts, balance sheet tables, or earnings slides with VLM architecture."""
    return await multimodal_service.analyze_image(req)
