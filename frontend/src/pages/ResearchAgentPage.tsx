import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  CheckCircle2,
  Clock,
  Printer,
  Download,
  Shield,
  FileCheck,
  TrendingUp,
  Activity
} from 'lucide-react';
import { api } from '../api/client';
import { ResearchReportDTO, AgentTraceStep } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const ResearchAgentPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialTicker = searchParams.get('ticker') || 'AAPL';

  const [ticker, setTicker] = useState(initialTicker);
  const [running, setRunning] = useState(false);
  const [currentStageIdx, setCurrentStageIdx] = useState<number>(-1);
  const [report, setReport] = useState<ResearchReportDTO | null>(null);

  const stagesList = [
    { name: 'Research Planner', desc: 'Formulates investment thesis, scope, and key risk parameters' },
    { name: 'Market Data Analyst', desc: 'Audits historical OHLCV price series, trading volume, and liquidity' },
    { name: 'Fundamental Analyst', desc: 'Calculates Gross/Operating Margins, Free Cash Flow, and Debt leverage' },
    { name: 'Technical Analyst', desc: 'Computes RSI(14), MACD convergence, and Bollinger Band boundaries' },
    { name: 'Risk & Sentiment Analyst', desc: 'Assesses Beta vs S&P 500, Max Drawdown, VaR 95%, and FinBERT tone' },
    { name: 'Document Researcher', desc: 'Performs semantic vector RAG search across SEC Form 10-K filings' },
    { name: 'Report Writer', desc: 'Synthesizes 14-section institutional brief with multi-scenario estimates' },
    { name: 'Verification Agent', desc: 'Audits calculation lineage, verifies evidence, and attaches disclaimers' }
  ];

  const [activeTrace, setActiveTrace] = useState<AgentTraceStep[]>(
    stagesList.map((s) => ({
      stage: s.name,
      description: s.desc,
      status: 'pending'
    }))
  );

  const handleLaunchAgent = async () => {
    setRunning(true);
    setReport(null);
    setCurrentStageIdx(0);


    const updatedTrace: AgentTraceStep[] = [...activeTrace].map(t => ({
      ...t,
      status: 'pending' as const
    }));

    for (let i = 0; i < stagesList.length; i++) {
      setCurrentStageIdx(i);
      updatedTrace[i] = {
        ...updatedTrace[i],
        status: 'in_progress'
      };
      setActiveTrace([...updatedTrace]);
      await new Promise((r) => setTimeout(r, 450));

      updatedTrace[i] = {
        ...updatedTrace[i],
        status: 'completed',
        duration_ms: 180 + i * 20
      };
      setActiveTrace([...updatedTrace]);
    }

    try {
      const res = await api.runResearchAgent(ticker);
      setReport(res);
      setActiveTrace(res.execution_trace);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
      setCurrentStageIdx(-1);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportMarkdown = () => {
    if (!report) return;
    const blob = new Blob([report.full_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `FinSight_${ticker}_Research_Report.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div id="research-agent-page" className="page-wrapper">
      <DisclaimerBanner />


      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Sparkles size={18} color="#fff" />
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
              AI Multi-Stage Equity Research Agent
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
            Autonomous 8-stage financial analyst agent generating comprehensive institutional research reports with verified evidence grounding.
          </p>
        </div>


        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select
            id="agent-ticker-select"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            disabled={running}
            style={{
              padding: '10px 14px',
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-primary)',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '13px',
              outline: 'none'
            }}
          >
            {['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].map((t) => (
              <option key={t} value={t}>{t} - Core Coverage</option>
            ))}
          </select>

          <button
            id="run-research-agent-btn"
            className="btn btn-primary"
            onClick={handleLaunchAgent}
            disabled={running}
          >
            <Sparkles size={16} />
            <span>{running ? 'Agent Orchestrating...' : 'Launch Research Agent'}</span>
          </button>
        </div>
      </div>


      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Execution Trace & Analyst Agent Pipeline</h2>
          </div>
          <span className="badge badge-cyan">8 Logical Agent Stages</span>
        </div>

        <div className="grid-12">
          {activeTrace.map((step, idx) => {
            const isDone = step.status === 'completed';
            const isInProg = step.status === 'in_progress';

            return (
              <div
                key={step.stage}
                id={`agent-step-${idx}`}
                className="col-3"
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  borderRadius: 'var(--radius-md)',
                  padding: '14px',
                  border: isInProg ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                  boxShadow: isInProg ? '0 0 12px var(--accent-cyan-glow)' : 'none',
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)' }}>STAGE 0{idx + 1}</span>
                  {isDone ? (
                    <CheckCircle2 size={16} color="var(--accent-emerald)" />
                  ) : isInProg ? (
                    <Clock size={16} color="var(--accent-cyan)" className="animate-pulse-glow" />
                  ) : (
                    <Clock size={16} color="var(--text-muted)" />
                  )}
                </div>
                <div style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>{step.stage}</div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                  {step.description}
                </div>
                {step.findings_summary && (
                  <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)', fontSize: '11px', color: 'var(--accent-cyan)' }}>
                    {step.findings_summary}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>


      {report && (
        <div className="glass-card" id="generated-report-container">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <span className="badge badge-emerald" style={{ marginBottom: '6px' }}>Verified Institutional Equity Brief</span>
              <h2 style={{ fontSize: '20px', fontWeight: 800 }}>{report.title}</h2>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Evidence Coverage: <strong>{(report.evidence_coverage * 100).toFixed(1)}%</strong> · AI Confidence Score: <strong>{(report.ai_confidence * 100).toFixed(1)}%</strong>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                id="report-print-btn"
                className="btn btn-secondary btn-sm"
                onClick={handlePrint}
              >
                <Printer size={14} />
                <span>Print Report</span>
              </button>
              <button
                id="report-export-btn"
                className="btn btn-primary btn-sm"
                onClick={handleExportMarkdown}
              >
                <Download size={14} />
                <span>Export Markdown</span>
              </button>
            </div>
          </div>


          <div
            style={{
              padding: '24px',
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              lineHeight: 1.7,
              fontSize: '14px',
              color: 'var(--text-primary)',
              whiteSpace: 'pre-line'
            }}
          >
            {report.full_markdown}
          </div>
        </div>
      )}
    </div>
  );
};
