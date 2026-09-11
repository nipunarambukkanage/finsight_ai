"""Versioned durable run API with replayable SSE events."""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.persistence.runs import run_repository
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()


class CreateRunRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10, pattern=r"^[A-Za-z0-9.\-]+$")
    workflow_kind: str = "research"
    data_mode: str = "live"
    payload: dict[str, Any] = Field(default_factory=dict)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_run(req: CreateRunRequest, response: Response, idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"), user: TokenPayload = Depends(get_current_user)):
    payload = {**req.payload, "data_mode": req.data_mode, "owner_id": user.sub}
    run = run_repository.create(req.ticker, req.workflow_kind, payload, idempotency_key)
    _check_owner(run, user)
    response.headers["Location"] = f"/api/v1/runs/{run['run_id']}"
    return run


@router.get("/{run_id}")
async def get_run(run_id: str, user: TokenPayload = Depends(get_current_user)):
    run = run_repository.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    _check_owner(run, user)
    return run


@router.get("/{run_id}/report")
async def get_report(run_id: str, user: TokenPayload = Depends(get_current_user)):
    """Return the immutable report artifact attached to a completed run."""
    run = run_repository.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    _check_owner(run, user)
    report = run.get("payload", {}).get("report")
    if report is None:
        raise HTTPException(status_code=409, detail="Report is not available for this run")
    return {"schema_version": "1.0", "run_id": run_id, "report": report}


@router.get("/{run_id}/evidence")
async def get_evidence(run_id: str, user: TokenPayload = Depends(get_current_user)):
    """Return source references without exposing another tenant's artifacts."""
    run = run_repository.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    _check_owner(run, user)
    report = run.get("payload", {}).get("report") or {}
    return {"schema_version": "1.0", "run_id": run_id, "evidence": report.get("execution_trace", [])}


@router.post("/{run_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_run(run_id: str, user: TokenPayload = Depends(get_current_user)):
    """Start a queued run in a bounded background task."""
    run = run_repository.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    _check_owner(run, user)
    lease_expired = False
    if run.get("lease_expires_at"):
        try:
            lease_expired = datetime.fromisoformat(run["lease_expires_at"]) <= datetime.now(timezone.utc)
        except ValueError:
            lease_expired = True
    if run["status"] not in {"QUEUED", "FAILED"} and not (run["status"] == "RUNNING" and lease_expired):
        raise HTTPException(status_code=409, detail=f"Run is {run['status']}")
    asyncio.create_task(_execute_run(run_id))
    return run_repository.update(run_id, "RUNNING")


@router.post("/{run_id}/cancel")
async def cancel_run(run_id: str, user: TokenPayload = Depends(get_current_user)):
    run = run_repository.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    _check_owner(run, user)
    if run["status"] in {"COMPLETED", "FAILED", "CANCELLED"}:
        raise HTTPException(status_code=409, detail=f"Run is already {run['status']}")
    return run_repository.update(run_id, "CANCELLED")


@router.get("/{run_id}/events")
async def stream_run_events(run_id: str, last_event_id: int = Header(default=0, alias="Last-Event-ID"), user: TokenPayload = Depends(get_current_user)):
    run = run_repository.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    _check_owner(run, user)

    async def generator():
        cursor = last_event_id
        idle_rounds = 0
        terminal = {"COMPLETED", "FAILED", "CANCELLED"}
        while True:
            events = run_repository.events(run_id, cursor)
            if events:
                idle_rounds = 0
                for event in events:
                    cursor = event["id"]
                    yield f"id: {cursor}\nevent: {event['event']}\ndata: {json.dumps(event['data'], default=str)}\n\n"
            else:
                idle_rounds += 1
                yield ": heartbeat\n\n"
                current = run_repository.get(run_id)
                if current and current["status"] in terminal and idle_rounds >= 3:
                    break
            await asyncio.sleep(0.25)

    return StreamingResponse(generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


async def _execute_run(run_id: str) -> None:
    """Reference dispatcher; production workers consume the same repository contract."""
    worker_id = f"worker-{uuid.uuid4().hex[:10]}"
    run = run_repository.claim(run_id, worker_id)
    if not run:
        return
    if run["status"] == "CANCELLED":
        return
    try:
        if run["workflow_kind"] == "research":
            from backend.app.agents.research_agent import research_agent
            from backend.app.models.schemas import ResearchAgentRequest
            report = await asyncio.wait_for(research_agent.run_research(ResearchAgentRequest(ticker=run["ticker"])), timeout=15.0)
            if run_repository.get(run_id)["status"] != "CANCELLED":
                run_repository.update(run_id, "COMPLETED", {"report": report.model_dump(mode="json")})
        else:
            if run_repository.get(run_id)["status"] != "CANCELLED":
                run_repository.update(run_id, "COMPLETED", {"message": "No handler registered for this workflow kind"})
    except Exception as exc:
        if (current := run_repository.get(run_id)) and current["status"] != "CANCELLED":
            run_repository.update(run_id, "FAILED", {"error": str(exc)})


def _check_owner(run: dict[str, Any], user: TokenPayload) -> None:
    owner_id = run.get("payload", {}).get("owner_id")
    if owner_id and owner_id != user.sub and user.role not in {"admin", "supervisor"}:
        raise HTTPException(status_code=404, detail="Run not found")
