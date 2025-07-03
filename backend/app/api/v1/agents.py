from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio
from backend.app.models.schemas import (
    ResearchAgentRequest, ResearchReportDTO
)
from backend.app.agents.research_agent import research_agent

router = APIRouter()

@router.post("/research", response_model=ResearchReportDTO)
async def execute_research_agent(req: ResearchAgentRequest):
    """Execute autonomous multi-stage equity research agent and generate full analyst brief."""
    return await research_agent.run_research(req)

@router.get("/research/stream/{ticker}")
async def stream_research_agent_trace(ticker: str):
    """
    Stream real-time visual trace steps of the 8-stage Research Agent via Server-Sent Events (SSE).
    """
    async def event_generator():
        stages = [
            ("Research Planner", "Deconstruct investment thesis and analytical scope"),
            ("Market Data Analyst", "Auditing historical price distributions and liquidity"),
            ("Fundamental Analyst", "Auditing income statement quality and gross margin stability"),
            ("Technical Analyst", "Computing RSI-14, MACD, and Bollinger Bands"),
            ("Risk & Sentiment Analyst", "Evaluating Beta, Max Drawdown, and FinBERT sentiment"),
            ("Document Researcher", "Scanning SEC Form 10-K filings in vector knowledge base"),
            ("Report Writer", "Synthesizing 14-section institutional research brief"),
            ("Verification Agent", "Auditing calculation lineage and attaching disclaimers")
        ]

        for i, (stage, desc) in enumerate(stages):
            data = {
                "step": i + 1,
                "total_steps": len(stages),
                "stage": stage,
                "description": desc,
                "status": "in_progress"
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.4)

            data["status"] = "completed"
            yield f"data: {json.dumps(data)}\n\n"

        # Final complete trigger
        report = await research_agent.run_research(ResearchAgentRequest(ticker=ticker))
        yield f"event: complete\ndata: {json.dumps(report.model_dump(), default=str)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
