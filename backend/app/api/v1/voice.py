from fastapi import APIRouter
from backend.app.models.schemas import VoiceBriefingRequest, VoiceBriefingResponse
from backend.app.services.voice import voice_service

router = APIRouter()

@router.post("/briefing", response_model=VoiceBriefingResponse)
async def generate_voice_briefing(req: VoiceBriefingRequest):
    """Generate audio script and financial takeaways for voice assistant playback."""
    return await voice_service.generate_briefing(req)
