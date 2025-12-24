"""
FinSight AI - Human Approval Endpoints
Handles explicit approval decisions (approve/reject/request changes) with audit logging.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.app.approvals.service import approval_service
from backend.app.orchestration.contracts import ApprovalRecord, ApprovalDecision
from backend.app.core.security import get_current_user_optional, TokenPayload

router = APIRouter()

class DecisionRequest(BaseModel):
    reason: Optional[str] = None
    reviewed_by: Optional[str] = None

@router.get("/pending", response_model=List[ApprovalRecord])
async def list_pending_approvals():
    """List all workflows currently awaiting human approval."""
    return approval_service.list_pending_approvals()

@router.get("/{approval_id}", response_model=ApprovalRecord)
async def get_approval_details(approval_id: str):
    """Retrieve details and artifact hash for an approval request."""
    rec = approval_service.get_approval(approval_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Approval record '{approval_id}' not found.")
    return rec

@router.post("/{approval_id}/approve", response_model=ApprovalRecord)
async def approve_artifact(
    approval_id: str,
    req: DecisionRequest,
    user: Optional[TokenPayload] = Depends(get_current_user_optional)
):
    """Formally approve an artifact to advance workflow to the next deterministic stage."""
    reviewer = req.reviewed_by or (user.sub if user else "senior_analyst")
    try:
        return approval_service.process_decision(
            approval_id=approval_id,
            reviewed_by=reviewer,
            decision=ApprovalDecision.APPROVE,
            reason=req.reason
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{approval_id}/reject", response_model=ApprovalRecord)
async def reject_artifact(
    approval_id: str,
    req: DecisionRequest,
    user: Optional[TokenPayload] = Depends(get_current_user_optional)
):
    """Formally reject an artifact with documented feedback."""
    reviewer = req.reviewed_by or (user.sub if user else "senior_analyst")
    try:
        return approval_service.process_decision(
            approval_id=approval_id,
            reviewed_by=reviewer,
            decision=ApprovalDecision.REJECT,
            reason=req.reason
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
