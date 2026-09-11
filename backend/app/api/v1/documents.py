from fastapi import APIRouter, HTTPException, Depends
from backend.app.models.schemas import DocumentCompareRequest, DocumentCompareResponse
from backend.app.services.document_intelligence import document_intelligence_service
from backend.app.core.security import get_current_user, TokenPayload

router = APIRouter()

@router.post("/compare", response_model=DocumentCompareResponse)
async def compare_reports(req: DocumentCompareRequest, user: TokenPayload = Depends(get_current_user)):
    """Compare two financial reports to detect metric variations, margin diffs, and risk shifts."""
    return document_intelligence_service.compare_documents(req.doc_id_a, req.doc_id_b)
