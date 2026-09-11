import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  FileText,
  Upload,
  GitCompare,
  ArrowRight,
  Shield,
  TrendingUp,
  AlertTriangle,
  Layers,
  CheckCircle
} from 'lucide-react';
import { api } from '../api/client';
import { DocumentCompareResponse } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const DocumentsPage: React.FC = () => {
  const { data: documents } = useQuery({
    queryKey: ['documents'],
    queryFn: api.getDocuments,
    staleTime: 60000
  });

  const [docAId, setDocAId] = useState<number>(1);
  const [docBId, setDocBId] = useState<number>(2);
  const [comparison, setComparison] = useState<DocumentCompareResponse | null>(null);
  const [comparing, setComparing] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const handleRunCompare = async () => {
    setComparing(true);
    try {
      const res = await api.compareDocuments(docAId, docBId);
      setComparison(res);
    } catch (err) {
      console.error(err);
    } finally {
      setComparing(false);
    }
  };

  const handleSimulatedUpload = () => {
    setUploadSuccess("Document 'NVIDIA_Blackwell_Architecture_Whitepaper_FY25.pdf' successfully parsed and 6 vector chunks indexed into vector database.");
    setTimeout(() => setUploadSuccess(null), 6000);
  };

  return (
    <div id="documents-page" className="page-wrapper">
      <DisclaimerBanner />


      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileText size={18} color="#fff" />
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
              Financial Document Intelligence & Filing Comparison
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
            Audits institutional SEC Form 10-K, 10-Q, and earnings filings. Analyzes margin shifts, MD&A tone, and disclosure diffs.
          </p>
        </div>


        <div>
          <button
            id="upload-filing-btn"
            className="btn btn-primary"
            onClick={handleSimulatedUpload}
          >
            <Upload size={16} />
            <span>Upload Financial Filing (PDF)</span>
          </button>
        </div>
      </div>

      {uploadSuccess && (
        <div style={{ padding: '12px 16px', backgroundColor: 'var(--accent-emerald-glow)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: 'var(--radius-md)', color: 'var(--accent-emerald)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <CheckCircle size={16} />
          <span>{uploadSuccess}</span>
        </div>
      )}


      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Indexed SEC Filing Universe</h2>

        <div className="grid-12">
          {(documents || [
            { id: 1, ticker: 'AAPL', title: 'Apple Inc. Form 10-K Annual Report (FY 2024)', doc_type: '10-K', reporting_period: 'FY 2024', summary: 'Services margin expansion to 74.2% and iPhone 16 supply chain resilience.' },
            { id: 2, ticker: 'NVDA', title: 'NVIDIA Corporation Q3 Fiscal 2025 Earnings Release', doc_type: 'Earnings', reporting_period: 'Q3 FY2025', summary: 'Data Center revenue surging 112% to $30.8B driven by Hopper and Blackwell architectures.' },
            { id: 3, ticker: 'MSFT', title: 'Microsoft Corporation Form 10-K Annual Report (FY 2024)', doc_type: '10-K', reporting_period: 'FY 2024', summary: 'Azure cloud growth of 29% and 60,000+ enterprise Azure OpenAI deployments.' }
          ]).map((doc) => (
            <div
              key={doc.id}
              className="col-4"
              style={{
                padding: '16px',
                backgroundColor: 'var(--bg-surface)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="badge badge-cyan">{doc.ticker || 'CORP'}</span>
                <span className="badge badge-purple">{doc.doc_type}</span>
              </div>
              <div style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)', marginBottom: '6px' }}>
                {doc.title}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Period: {doc.reporting_period}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                {doc.summary}
              </div>
            </div>
          ))}
        </div>
      </div>


      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <GitCompare size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Intelligent Filing Comparison Engine</h2>
          </div>
          <span className="badge badge-emerald">Diff Audit Ready</span>
        </div>


        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '240px' }}>
            <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 600 }}>
              REPORT A (BASELINE)
            </label>
            <select
              id="compare-select-doc-a"
              className="input-text"
              value={docAId}
              onChange={(e) => setDocAId(Number(e.target.value))}
            >
              <option value={1}>Apple Inc. Form 10-K (FY 2024)</option>
              <option value={2}>NVIDIA Corporation Q3 FY2025 Release</option>
              <option value={3}>Microsoft Corporation Form 10-K (FY 2024)</option>
            </select>
          </div>

          <div style={{ color: 'var(--text-muted)', paddingTop: '16px' }}>vs</div>

          <div style={{ flex: 1, minWidth: '240px' }}>
            <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 600 }}>
              REPORT B (COMPARISON TARGET)
            </label>
            <select
              id="compare-select-doc-b"
              className="input-text"
              value={docBId}
              onChange={(e) => setDocBId(Number(e.target.value))}
            >
              <option value={2}>NVIDIA Corporation Q3 FY2025 Release</option>
              <option value={1}>Apple Inc. Form 10-K (FY 2024)</option>
              <option value={3}>Microsoft Corporation Form 10-K (FY 2024)</option>
            </select>
          </div>

          <div style={{ paddingTop: '16px' }}>
            <button
              id="run-compare-btn"
              className="btn btn-primary"
              onClick={handleRunCompare}
              disabled={comparing}
            >
              <GitCompare size={16} />
              <span>{comparing ? 'Auditing Differences...' : 'Run Comparative Audit'}</span>
            </button>
          </div>
        </div>


        {comparison && (
          <div id="comparison-results-container" style={{ marginTop: '20px' }}>
            <div className="grid-12" style={{ marginBottom: '20px' }}>
              <div className="col-6" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600, marginBottom: '6px' }}>
                  REVENUE DYNAMICS DIFF
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                  {comparison.revenue_changes}
                </div>
              </div>

              <div className="col-6" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600, marginBottom: '6px' }}>
                  GROSS & OPERATING MARGIN EVOLUTION
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                  {comparison.margin_changes}
                </div>
              </div>
            </div>


            <div style={{ backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', padding: '16px', marginBottom: '20px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '12px' }}>
                Key Quantitative KPI Variations
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: '8px' }}>Metric</th>
                    <th style={{ padding: '8px' }}>Report A Value</th>
                    <th style={{ padding: '8px' }}>Report B Value</th>
                    <th style={{ padding: '8px' }}>Reported Variance</th>
                    <th style={{ padding: '8px' }}>Direction</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.metrics_comparison.map((m) => (
                    <tr key={m.metric} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                      <td style={{ padding: '10px 8px', fontWeight: 600 }}>{m.metric}</td>
                      <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>{m.value_a}</td>
                      <td style={{ padding: '10px 8px', color: 'var(--text-primary)', fontWeight: 600 }}>{m.value_b}</td>
                      <td style={{ padding: '10px 8px', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                        {m.change_pct ? `+${m.change_pct}%` : 'N/A'}
                      </td>
                      <td style={{ padding: '10px 8px' }}>
                        <span className="badge badge-emerald">{m.direction}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>


            <div style={{ backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={16} color="var(--accent-amber)" />
                <span>Detected Risk Factor & Regulatory Shifts</span>
              </div>
              <ul style={{ paddingLeft: '20px', fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.8 }}>
                {comparison.risk_factor_changes.map((risk, i) => (
                  <li key={i}>{risk}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
