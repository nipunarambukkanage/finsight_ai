"""Versioned application interfaces for the independent assessment artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.config import settings
from backend.app.core.security import TokenPayload, get_current_user
from backend.app.providers.gateway import ModelRequest, model_gateway
from task2_genai.src.contracts import FilingRiskOutput

router = APIRouter()


class FilingRiskRequest(BaseModel):
    excerpt: str = Field(min_length=20, max_length=50_000)
    document_id: str = Field(min_length=1, max_length=200)
    filing_date: Optional[str] = None
    company: Optional[str] = None


def _grounding(output: FilingRiskOutput, request: FilingRiskRequest) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for risk in output.risks:
        quote_ok = bool(risk.supporting_quote and risk.supporting_quote in request.excerpt)
        document_ok = bool(risk.document_id and risk.document_id == request.document_id)
        checks.append({"category": risk.category, "quote_present": quote_ok, "document_match": document_ok, "grounded": quote_ok and document_ok})
    grounded = sum(check["grounded"] for check in checks)
    return {"risk_count": len(checks), "grounded_count": grounded, "grounding_rate": grounded / len(checks) if checks else (1.0 if output.abstain else 0.0), "checks": checks}


@router.post("/filing-risks")
async def extract_filing_risks(request: FilingRiskRequest, user: TokenPayload = Depends(get_current_user)):
    """Return a schema-validated model response and exact-quote grounding audit."""
    prompt = (
        f"Document ID: {request.document_id}\n"
        f"Company: {request.company or 'unknown'}\n"
        f"Filing date: {request.filing_date or 'unknown'}\n"
        "Extract only risks supported by the excerpt. Quote exact text, preserve the document id, "
        "and abstain when evidence is insufficient. Return only FilingRiskOutput JSON.\n\n"
        f"Filing excerpt:\n{request.excerpt}"
    )
    model_request = ModelRequest(task_type="filing_risk_extraction", complexity="medium", allow_demo_fallback=settings.DEMO_MODE)
    try:
        raw, telemetry = await model_gateway.generate(prompt, request=model_request)
        output = FilingRiskOutput.model_validate_json(raw if isinstance(raw, str) else raw.model_dump_json())
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Filing-risk model is unavailable or returned invalid JSON: {exc}") from exc
    grounding = _grounding(output, request)
    if grounding["grounding_rate"] < 1.0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"message": "Model output failed exact evidence grounding", "grounding": grounding})
    return {"schema_version": "1.0", "document_id": request.document_id, "output": output, "grounding": grounding, "telemetry": telemetry}


@router.get("/model-evaluations/{evaluation_id}")
async def read_model_evaluation(evaluation_id: str, user: TokenPayload = Depends(get_current_user)):
    """Read a committed Task 2 evaluation artifact without inventing metrics."""
    candidates = [
        Path("task2_genai/artifacts") / f"{evaluation_id}.json",
        Path("task2_genai/artifacts") / "evaluation.json" if evaluation_id == "latest" else Path("__missing__"),
    ]
    artifact = next((path for path in candidates if path.exists()), None)
    if artifact is None:
        raise HTTPException(status_code=404, detail="No executed model evaluation artifact is available")
    try:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=500, detail=f"Evaluation artifact is unreadable: {exc}") from exc
    return {"schema_version": "1.0", "evaluation_id": evaluation_id, "artifact": str(artifact), "metrics": payload}
