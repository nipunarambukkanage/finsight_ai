import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Database,
  Search,
  FileText,
  CheckCircle2,
  ShieldCheck,
  Activity,
  Layers
} from 'lucide-react';
import { api } from '../api/client';
import { RAGQueryResponse } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const RAGExplorerPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialQ = searchParams.get('q') || "What was Apple's Services segment gross margin in FY2024?";

  const [query, setQuery] = useState(initialQ);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RAGQueryResponse | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    try {
      const res = await api.queryRAG(query);
      setResponse(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="rag-explorer-page" className="page-wrapper">
      <DisclaimerBanner />

      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Database size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            LangChain RAG Vector Knowledge Explorer
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Dense vector retrieval across tokenized SEC filings. Queries execute cosine similarity ranking to return evidence-backed answers.
        </p>
      </div>

      {/* Search Input Bar */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              id="rag-query-input"
              type="text"
              className="input-text"
              placeholder="Query SEC 10-K knowledge base (e.g. What are Apple's supply chain risks?)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ paddingLeft: '42px', fontSize: '14px' }}
            />
          </div>
          <button
            id="rag-query-submit-btn"
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Retrieving Vector Chunks...' : 'Execute RAG Query'}
          </button>
        </form>

        {/* Suggested Queries */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', alignSelf: 'center' }}>Try:</span>
          {[
            "What was Apple's Services segment gross margin in FY2024?",
            "What are NVIDIA's Data Center revenue drivers?",
            "What are Apple's geopolitical supply chain risks?",
            "What is Microsoft's Azure OpenAI customer growth?"
          ].map((qText) => (
            <button
              key={qText}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: '11px' }}
              onClick={() => { setQuery(qText); }}
            >
              {qText}
            </button>
          ))}
        </div>
      </div>

      {/* Results Section */}
      {response && (
        <div className="grid-12">
          {/* Grounded Answer Card */}
          <div className="col-8 glass-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={18} color="var(--accent-emerald)" />
                <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Grounded Synthesis</h2>
              </div>
              <span className="badge badge-emerald">Evidence Coverage: {(response.evidence_coverage * 100).toFixed(1)}%</span>
            </div>

            <div
              style={{
                padding: '18px',
                backgroundColor: 'var(--bg-surface)',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px',
                lineHeight: 1.7,
                color: 'var(--text-primary)',
                whiteSpace: 'pre-line',
                border: '1px solid var(--border-subtle)'
              }}
            >
              {response.answer}
            </div>

            <div style={{ marginTop: '16px', fontSize: '11px', color: 'var(--text-muted)' }}>
              {response.disclaimer}
            </div>
          </div>

          {/* Retrieved Chunks & Citations */}
          <div className="col-4 glass-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} color="var(--accent-cyan)" />
                <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Retrieved Chunks</h2>
              </div>
              <span className="badge badge-cyan">{response.citations.length} Verified</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {response.citations.map((cite, i) => (
                <div
                  key={i}
                  style={{
                    padding: '14px',
                    backgroundColor: 'var(--bg-surface)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '12px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span className="badge badge-purple">{cite.ticker}</span>
                    <span style={{ color: 'var(--accent-emerald)', fontWeight: 600, fontSize: '11px' }}>
                      Cosine Sim: {cite.similarity_score}
                    </span>
                  </div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                    {cite.document_title}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    Page: {cite.page_number} · Chunk #{cite.chunk_index}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', lineHeight: 1.5, fontStyle: 'italic', backgroundColor: 'var(--bg-secondary)', padding: '8px', borderRadius: '4px' }}>
                    "{cite.snippet}"
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
