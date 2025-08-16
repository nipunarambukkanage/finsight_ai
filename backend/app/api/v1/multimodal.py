from fastapi import APIRouter
from backend.app.models.schemas import MultimodalAnalyzeRequest, MultimodalAnalyzeResponse
from backend.app.services.multimodal import multimodal_service

router = APIRouter()

@router.post("/analyze", response_model=MultimodalAnalyzeResponse)
async def analyze_financial_image(req: MultimodalAnalyzeRequest):
    """Analyze financial candlestick charts, balance sheet tables, or earnings slides with VLM architecture."""
    return await multimodal_service.analyze_image(req)
