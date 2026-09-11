from fastapi import APIRouter, Depends
from backend.app.models.schemas import PortfolioSummary
from backend.app.services.portfolio import portfolio_service
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()

@router.get("/", response_model=PortfolioSummary)
async def get_portfolio(user: TokenPayload = Depends(get_current_user)):
    """Retrieve institutional model portfolio summary, asset allocations, risk metrics, and AI risk commentary."""
    return await portfolio_service.get_portfolio_summary()
