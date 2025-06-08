from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from backend.app.models.schemas import (
    RAGQueryRequest, RAGQueryResponse, DocumentDTO, Citation
)
from backend.app.rag.engine import rag_engine

router = APIRouter()

@router.post("/query", response_model=RAGQueryResponse)
async def query_knowledge_base(req: RAGQueryRequest):
    """Query the LangChain RAG financial knowledge base with strict evidence citations."""
    return await rag_engine.query(req)

@router.get("/documents", response_model=List[DocumentDTO])
async def list_indexed_documents():
    """List all indexed financial documents in the vector knowledge base."""
    return list(rag_engine.documents.values())

@router.post("/upload", response_model=DocumentDTO)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    ticker: Optional[str] = Form(None),
    doc_type: Optional[str] = Form("Financial Report")
):
    """Upload and process a financial report (PDF/TXT/MD) into the vector knowledge base."""
    contents = await file.read()
    filename = file.filename or "uploaded_doc.txt"
    doc_title = title or filename

    # Extract text
    if filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(contents))
            extracted_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        except Exception:
            extracted_text = contents.decode("utf-8", errors="ignore")
    else:
        extracted_text = contents.decode("utf-8", errors="ignore")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Unable to extract readable text from uploaded file.")

    return rag_engine.add_custom_document(
        title=doc_title,
        text=extracted_text,
        ticker=ticker.upper() if ticker else None,
        doc_type=doc_type or "Financial Report"
    )
