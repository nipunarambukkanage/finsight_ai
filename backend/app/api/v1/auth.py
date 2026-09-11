from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import timedelta
from backend.app.core.security import create_access_token, get_current_user, TokenPayload
from backend.app.config import settings

router = APIRouter()

class DemoLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/demo-login", response_model=DemoLoginResponse)
async def demo_login():
    """Frictionless demo authentication returning access token for client evaluation."""
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo authentication is disabled")
    token = create_access_token("demo_analyst", role="senior_analyst")
    return DemoLoginResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": 1,
            "username": "demo_analyst",
            "full_name": "Senior Equity Research Analyst",
            "role": "senior_analyst",
            "permissions": ["all"]
        }
    )

@router.get("/me")
async def get_current_user_profile(user: TokenPayload = Depends(get_current_user)):
    """Retrieve active session profile."""
    return {
        "username": user.sub,
        "role": user.role,
        "demo_mode": settings.DEMO_MODE
    }
