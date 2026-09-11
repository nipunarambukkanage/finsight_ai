from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json
from backend.app.models.schemas import (
    ResearchAgentRequest, ResearchReportDTO
)
from backend.app.agents.research_agent import research_agent
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()

@router.post("/research", response_model=ResearchReportDTO)
async def execute_research_agent(req: ResearchAgentRequest, user: TokenPayload = Depends(get_current_user)):
    """Execute autonomous multi-stage equity research agent and generate full analyst brief."""
    try:
        return await asyncio.wait_for(research_agent.run_research(req), timeout=15.0)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Legacy research run exceeded its 15-second execution limit") from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.get("/research/stream/{ticker}")
async def stream_research_agent_trace(ticker: str, user: TokenPayload = Depends(get_current_user)):
    """
    Stream real-time visual trace steps of the 8-stage Research Agent via Server-Sent Events (SSE).
    """
    async def event_generator():
        try:
            report = await asyncio.wait_for(research_agent.run_research(ResearchAgentRequest(ticker=ticker)), timeout=15.0)
        except asyncio.TimeoutError:
            yield "event: error\ndata: {\"error\": \"Legacy research run exceeded its 15-second execution limit\"}\n\n"
            return
        except ValueError as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"
            return
        total = len(report.execution_trace)
        for i, step in enumerate(report.execution_trace):
            data = step.model_dump()
            data.update({"step": i + 1, "total_steps": total})
            yield f"data: {json.dumps(data, default=str)}\n\n"
        yield f"event: complete\ndata: {json.dumps(report.model_dump(), default=str)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
