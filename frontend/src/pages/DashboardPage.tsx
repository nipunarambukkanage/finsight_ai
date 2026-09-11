import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  TrendingUp,
  TrendingDown,
  Sparkles,
  ShieldAlert,
  ArrowRight,
  FileText,
  Activity,
  Zap,
  Volume2,
  Cpu
} from 'lucide-react';
import { api } from '../api/client';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: stocks } = useQuery({
    queryKey: ['stocks'],
    queryFn: api.getStocks,
    staleTime: 60000
  });

  const { data: portfolio } = useQuery({
    queryKey: ['portfolio'],
    queryFn: api.getPortfolio,
    staleTime: 60000
  });

  const { data: sentiment } = useQuery({
    queryKey: ['sentiment-overview'],
    queryFn: api.getSentimentOverview,
    staleTime: 60000
  });

  const { data: docs } = useQuery({
    queryKey: ['documents'],
    queryFn: api.getDocuments,
    staleTime: 60000
  });

  return (
    <div id="dashboard-page" className="page-wrapper">
      <DisclaimerBanner />


      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '28px',
          flexWrap: 'wrap',
          gap: '16px'
        }}
      >
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            Financial Intelligence Dashboard
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
            Real-time generative investment analytics, RAG knowledge retrieval, and multi-stage research agents.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            id="launch-research-agent-btn"
            className="btn btn-primary"
            onClick={() => navigate('/research-agent')}
          >
            <Sparkles size={16} />
            <span>Launch AI Research Agent</span>
          </button>
          <button
            id="open-assistant-btn"
            className="btn btn-secondary"
            onClick={() => navigate('/assistant')}
          >
            <span>Ask AI Assistant</span>
            <ArrowRight size={14} />
          </button>
        </div>
      </div>


      <div className="grid-12" style={{ marginBottom: '24px' }}>
        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            S&P 500 Benchmark (SPY)
          </div>
          <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '8px' }}>$558.40</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-emerald)', marginTop: '4px', fontSize: '12px', fontWeight: 600 }}>
            <TrendingUp size={14} />
            <span>+0.85% Today</span>
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            Portfolio Total Value
          </div>
          <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '8px' }}>
            ${portfolio ? portfolio.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '1,048,250.00'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-emerald)', marginTop: '4px', fontSize: '12px', fontWeight: 600 }}>
            <TrendingUp size={14} />
            <span>+{portfolio ? portfolio.total_unrealized_pl_pct.toFixed(2) : '18.42'}% Unrealized P/L</span>
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            Macro Volatility (VIX)
          </div>
          <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '8px' }}>15.42</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-cyan)', marginTop: '4px', fontSize: '12px', fontWeight: 600 }}>
            <Activity size={14} />
            <span>Low Risk / Stable Regime</span>
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            Market Sentiment Index
          </div>
          <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '8px' }}>
            {sentiment ? `${sentiment.positive_pct}% Bullish` : '74.2% Bullish'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-emerald)', marginTop: '4px', fontSize: '12px', fontWeight: 600 }}>
            <Zap size={14} />
            <span>FinBERT Institutional Consensus</span>
          </div>
        </div>
      </div>


      <div className="grid-12" style={{ marginBottom: '24px' }}>

        <div className="col-8 glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--accent-cyan-glow)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--accent-cyan)'
                }}
              >
                <Sparkles size={16} />
              </div>
              <h2 style={{ fontSize: '16px', fontWeight: 700 }}>FinSight AI Daily Executive Briefing</h2>
            </div>
            <button
              id="voice-briefing-play-btn"
              className="btn btn-secondary btn-sm"
              onClick={() => navigate('/voice')}
            >
              <Volume2 size={14} />
              <span>Audio Briefing</span>
            </button>
          </div>

          <div
            style={{
              padding: '16px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              lineHeight: 1.6,
              fontSize: '13px',
              color: 'var(--text-secondary)'
            }}
          >
            <p style={{ marginBottom: '12px' }}>
              <strong style={{ color: 'var(--text-primary)' }}>Macro Narrative:</strong> U.S. large-cap equities maintain strong upward structural support, propelled by semiconductor architecture upgrades and accelerating enterprise generative AI adoption. 10-Year Treasury yields remain anchored at 4.15%, keeping equity valuation multiples elevated yet stable across mega-cap technology leaders.
            </p>
            <p style={{ marginBottom: '12px' }}>
              <strong style={{ color: 'var(--text-primary)' }}>Watchlist Catalysts:</strong> <span style={{ color: 'var(--accent-cyan)' }}>NVIDIA (NVDA)</span> leads intraday volume following initial customer delivery milestones for the Blackwell architecture. <span style={{ color: 'var(--accent-cyan)' }}>Apple (AAPL)</span> continues to expand services segment gross margins (74.2% in FY24), shielding free cash flows against smartphone hardware cyclicality.
            </p>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '16px' }}>
              <span className="badge badge-cyan">RAG Grounded</span>
              <span className="badge badge-emerald">FinBERT Score +0.68</span>
              <span className="badge badge-purple">Zero Hallucination Guard</span>
            </div>
          </div>


          <div style={{ marginTop: '20px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px' }}>
              QUICK AI INVESTIGATIONS:
            </div>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              {[
                'Compare Apple & Microsoft valuation',
                'What are NVIDIA Blackwell risks?',
                'Explain Services margin expansion',
                'Audit portfolio risk concentration'
              ].map((promptText) => (
                <button
                  key={promptText}
                  className="btn btn-secondary btn-sm"
                  onClick={() => navigate(`/assistant?q=${encodeURIComponent(promptText)}`)}
                >
                  <span>{promptText}</span>
                  <ArrowRight size={12} />
                </button>
              ))}
            </div>
          </div>
        </div>


        <div className="col-4 glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Core Coverage Watchlist</h2>
            <button
              id="view-all-stocks-btn"
              className="btn btn-secondary btn-sm"
              onClick={() => navigate('/stocks')}
            >
              All Tickers
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {(stocks || [
              { ticker: 'AAPL', name: 'Apple Inc.', current_price: 235.50, change_percent: 1.42, pe_ratio: 34.2 },
              { ticker: 'MSFT', name: 'Microsoft Corp.', current_price: 428.20, change_percent: 0.85, pe_ratio: 36.1 },
              { ticker: 'NVDA', name: 'NVIDIA Corp.', current_price: 128.80, change_percent: 3.15, pe_ratio: 52.4 },
              { ticker: 'GOOGL', name: 'Alphabet Inc.', current_price: 182.40, change_percent: -0.45, pe_ratio: 24.8 },
              { ticker: 'AMZN', name: 'Amazon.com', current_price: 194.20, change_percent: 1.12, pe_ratio: 44.5 }
            ]).map((stk) => {
              const isPos = stk.change_percent >= 0;
              return (
                <div
                  key={stk.ticker}
                  className="glass-card-interactive"
                  id={`watchlist-card-${stk.ticker}`}
                  onClick={() => navigate(`/stocks/${stk.ticker}`)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <strong style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{stk.ticker}</strong>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>P/E: {stk.pe_ratio}x</span>
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      {stk.name}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 600, fontSize: '13px' }}>${stk.current_price.toFixed(2)}</div>
                    <div
                      style={{
                        fontSize: '11px',
                        fontWeight: 600,
                        color: isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)'
                      }}
                    >
                      {isPos ? '+' : ''}{stk.change_percent.toFixed(2)}%
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>


      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Indexed SEC Filings & Research Intelligence</h2>
          </div>
          <button
            id="open-rag-explorer-btn"
            className="btn btn-secondary btn-sm"
            onClick={() => navigate('/documents')}
          >
            Manage Filings
          </button>
        </div>

        <div className="grid-12">
          {(docs || [
            { id: 1, ticker: 'AAPL', title: 'Apple Inc. Form 10-K Annual Report (FY 2024)', doc_type: '10-K', reporting_period: 'FY 2024', summary: 'Services margin expansion to 74.2% and iPhone 16 supply chain resilience.' },
            { id: 2, ticker: 'NVDA', title: 'NVIDIA Corporation Q3 Fiscal 2025 Earnings Release', doc_type: 'Earnings', reporting_period: 'Q3 FY2025', summary: 'Data Center revenue surging 112% to $30.8B driven by Hopper and Blackwell architectures.' },
            { id: 3, ticker: 'MSFT', title: 'Microsoft Corporation Form 10-K Annual Report (FY 2024)', doc_type: '10-K', reporting_period: 'FY 2024', summary: 'Azure cloud growth of 29% and 60,000+ enterprise Azure OpenAI deployments.' }
          ]).map((doc) => (
            <div
              key={doc.id}
              className="col-4 glass-card-interactive"
              id={`doc-card-${doc.id}`}
              onClick={() => navigate(`/rag?q=${encodeURIComponent(doc.ticker || 'AAPL')}`)}
              style={{ padding: '16px', backgroundColor: 'var(--bg-surface)' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="badge badge-cyan">{doc.ticker}</span>
                <span className="badge badge-purple">{doc.doc_type}</span>
              </div>
              <div style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)', marginBottom: '6px' }}>
                {doc.title}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                {doc.summary}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
