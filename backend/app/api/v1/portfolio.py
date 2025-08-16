from fastapi import APIRouter
from backend.app.models.schemas import PortfolioSummary
from backend.app.services.portfolio import portfolio_service

router = APIRouter()

@router.get("/", response_model=PortfolioSummary)
async def get_portfolio():
    """Retrieve institutional model portfolio summary, asset allocations, risk metrics, and AI risk commentary."""
    return await portfolio_service.get_portfolio_summary()
