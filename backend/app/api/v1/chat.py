from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio
from backend.app.models.schemas import AIChatRequest, AIChatResponse
from backend.app.services.chat_service import chat_service
from backend.app.providers.manager import provider_manager
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()

@router.post("/", response_model=AIChatResponse)
async def chat_interaction(req: AIChatRequest, user: TokenPayload = Depends(get_current_user)):
    """Context-aware financial assistant interaction with intent classification and tool execution."""
    return await chat_service.process_chat(req)

@router.post("/stream")
async def chat_interaction_stream(req: AIChatRequest, user: TokenPayload = Depends(get_current_user)):
    """Server-Sent Events (SSE) streaming financial assistant response."""
    async def stream_generator():

        yield f"data: {json.dumps({'type': 'status', 'status': 'Analyzing query intent & retrieving verified data...'})}\n\n"
        await asyncio.sleep(0.3)

        full_res = await chat_service.process_chat(req)

        yield f"data: {json.dumps({'type': 'metadata', 'intent': full_res.intent, 'tools_called': full_res.tools_called, 'citations': [c.model_dump() for c in full_res.citations]})}\n\n"


        words = full_res.response.split(" ")
        for w in words:
            yield f"data: {json.dumps({'type': 'token', 'token': w + ' '})}\n\n"
            await asyncio.sleep(0.015)

        yield f"data: {json.dumps({'type': 'done', 'disclaimer': full_res.disclaimer})}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
