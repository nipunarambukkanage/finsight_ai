from fastapi import APIRouter
from typing import List
from backend.app.models.schemas import (
    SentimentRequest, SentimentResponse, BatchSentimentRequest, SentimentDistribution
)
from backend.app.services.sentiment import sentiment_service

router = APIRouter()

@router.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(req: SentimentRequest):
    """Analyze single financial text snippet using FinBERT / finance domain lexicon."""
    return sentiment_service.analyze_text(req.text, ticker=req.ticker)

@router.post("/batch", response_model=List[SentimentResponse])
async def analyze_batch_sentiment(req: BatchSentimentRequest):
    """Analyze a batch of financial headlines or report excerpts."""
    texts = [item.text for item in req.items]
    return sentiment_service.analyze_batch(texts)

@router.get("/overview", response_model=SentimentDistribution)
async def get_market_sentiment_overview():
    """Retrieve aggregate sentiment distribution and timeline across current watchlist news."""
    sample_news = [
        "Apple reports record high services margin expansion exceeding analyst expectations.",
        "NVIDIA unveils next-generation Blackwell architecture with surging enterprise backlog.",
        "Microsoft Azure AI commercial demand accelerates with 60,000 active enterprise customers.",
        "Regulatory scrutiny over European Digital Markets Act causes mild operational friction.",
        "Consumer electronics upgrade cadence shows modest elongation in international markets."
    ]
    analyzed = sentiment_service.analyze_batch(sample_news)
    return sentiment_service.get_distribution(analyzed)
