from fastapi import APIRouter, Depends
from backend.app.models.schemas import VoiceBriefingRequest, VoiceBriefingResponse
from backend.app.services.voice import voice_service
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()

@router.post("/briefing", response_model=VoiceBriefingResponse)
async def generate_voice_briefing(req: VoiceBriefingRequest, user: TokenPayload = Depends(get_current_user)):
    """Generate audio script and financial takeaways for voice assistant playback."""
    return await voice_service.generate_briefing(req)
