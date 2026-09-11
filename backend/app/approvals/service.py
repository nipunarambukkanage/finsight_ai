"""
FinSight AI - Human Approval Service & Audit Engine
Manages formal human-in-the-loop approval workflows for:
- Strategy promotion
- Generated code acceptance
- Backtest promotion
- Shadow-trading activation
- Recommendation publication
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import hashlib
from backend.app.orchestration.contracts import ApprovalRecord, ApprovalDecision
from backend.app.orchestration.permissions import PermissionEnforcer
from backend.app.core.logging import logger

class ApprovalService:
    def __init__(self):
        self._approvals: Dict[str, ApprovalRecord] = {}

    def create_approval_request(
        self,
        workflow_id: str,
        artifact_content: str,
        requested_by: str = "supervisor"
    ) -> ApprovalRecord:
        """Create an approval request and generate unique artifact hash."""
        approval_id = f"appr-{uuid.uuid4().hex[:8]}"
        artifact_hash = hashlib.sha256(artifact_content.encode('utf-8')).hexdigest()

        rec = ApprovalRecord(
            approval_id=approval_id,
            workflow_id=workflow_id,
            artifact_hash=artifact_hash,
            requested_by=requested_by,
            reviewed_by=None,
            decision="PENDING",
            reason=None,
            created_at=datetime.now(timezone.utc),
            reviewed_at=None
        )
        self._approvals[approval_id] = rec
        logger.info(f"Created approval gate {approval_id} for workflow {workflow_id} (Artifact: {artifact_hash[:8]})")
        return rec

    def get_approval(self, approval_id: str) -> Optional[ApprovalRecord]:
        return self._approvals.get(approval_id)

    def process_decision(
        self,
        approval_id: str,
        reviewed_by: str,
        decision: ApprovalDecision,
        reason: Optional[str] = None
    ) -> ApprovalRecord:
        """Approve, reject, or request changes with separation of duties enforcement."""
        rec = self._approvals.get(approval_id)
        if not rec:
            raise ValueError(f"Approval record '{approval_id}' not found.")
        if rec.decision != "PENDING":
            raise ValueError(f"Approval record '{approval_id}' is already finalized as {rec.decision}.")



        try:
            decision = decision if isinstance(decision, ApprovalDecision) else ApprovalDecision(str(decision).upper())
        except ValueError as exc:
            raise ValueError(f"Unsupported approval decision: {decision}") from exc


        PermissionEnforcer.check_separation_of_duties(rec.requested_by, reviewed_by)

        rec.decision = decision.value
        rec.reviewed_by = reviewed_by
        rec.reason = reason or f"Decision {decision.value} by {reviewed_by}"
        rec.reviewed_at = datetime.now(timezone.utc)

        logger.info(f"Approval gate {approval_id} processed: {decision.value} by {reviewed_by} (Reason: {rec.reason})")
        return rec

    def list_pending_approvals(self) -> List[ApprovalRecord]:
        return [a for a in self._approvals.values() if a.decision == "PENDING"]

approval_service = ApprovalService()
