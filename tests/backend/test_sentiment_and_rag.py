import pytest
from backend.app.services.sentiment import sentiment_service
from backend.app.rag.engine import rag_engine
from backend.app.models.schemas import RAGQueryRequest
from backend.app.services.document_intelligence import document_intelligence_service

def test_sentiment_analysis_labels():
    bullish = "Apple reports record revenue beat with accelerating services margin expansion."
    res_pos = sentiment_service.analyze_text(bullish)
    assert res_pos.label == "Positive"
    assert res_pos.score > 0.6
    assert len(res_pos.key_phrases) > 0

    bearish = "Company warns of severe supply chain headwinds and guidance cut amid macroeconomic recession."
    res_neg = sentiment_service.analyze_text(bearish)
    assert res_neg.label == "Negative"
    assert res_neg.score > 0.6

    neutral = "Company will hold its standard quarterly call on Thursday at 2 PM Eastern time."
    res_neu = sentiment_service.analyze_text(neutral)
    assert res_neu.label in ["Neutral", "Positive"]

@pytest.mark.asyncio
async def test_rag_knowledge_query_and_citations():
    req = RAGQueryRequest(query="What was Apple's Services segment gross margin in FY2024?", ticker="AAPL", top_k=2)
    res = await rag_engine.query(req)
    assert res.query == req.query
    assert len(res.citations) > 0
    assert "74.2%" in res.answer or "Services" in res.answer or len(res.citations) >= 1
    assert res.citations[0].document_title.startswith("Apple Inc.")
    assert res.evidence_coverage > 0.8
    assert "disclaimer" in res.disclaimer.lower()

def test_document_comparison():
    comp = document_intelligence_service.compare_documents(1, 2)
    assert comp.doc_a_title is not None
    assert comp.doc_b_title is not None
    assert len(comp.metrics_comparison) >= 2
    assert len(comp.risk_factor_changes) >= 1
