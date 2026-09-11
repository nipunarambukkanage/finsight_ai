import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  TrendingUp,
  FileText,
  Code,
  CheckSquare,
  BarChart3,
  Play,
  Pause,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';
import { api } from '../api/client';
import { WorkflowStateDTO } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const WorkflowPage: React.FC = () => {
  const [ticker, setTicker] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'evidence' | 'strategy' | 'qa' | 'backtest' | 'approval' | 'shadow' | 'audit'>('evidence');
  const [workflow, setWorkflow] = useState<WorkflowStateDTO | null>(null);
  const [reviewReason, setReviewReason] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const stages = [
    { key: 'market_data', label: '1. Market Data', desc: 'Parquet Snapshot' },
    { key: 'research', label: '2. SEC RAG', desc: 'Evidence Grounding' },
    { key: 'strategy_specification', label: '3. Strategy Spec', desc: 'Hypothesis Formulation' },
    { key: 'implementation', label: '4. Dev Agent', desc: 'Candidate Python Code' },
    { key: 'qa_validation', label: '5. QA Agent', desc: 'AST & Bias Checks' },
    { key: 'backtesting', label: '6. Backtest', desc: 'Deterministic Replay' },
    { key: 'human_approval', label: '7. Approval Gate', desc: 'Human Review' },
    { key: 'shadow_trading', label: '8. Shadow Mode', desc: 'Virtual Execution' },
    { key: 'recommendation', label: '9. Institutional Brief', desc: 'Decision Support' },
  ];

  const handleStartWorkflow = async () => {
    setLoading(true);
    try {
      const res = await api.startWorkflow(ticker);
      setWorkflow(res);
      if (res.status === 'WAITING_APPROVAL') {
        setActiveTab('approval');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovalDecision = async (decision: 'APPROVE' | 'REJECT' | 'REQUEST_CHANGES') => {
    if (!workflow) return;
    setActionLoading(true);
    try {
      const res = await api.resumeWorkflow(
        workflow.workflow_id,
        decision,
        reviewReason || `Operator ${decision} decision`,
        'senior_analyst'
      );
      setWorkflow(res);
      if (decision === 'APPROVE') {
        setActiveTab('shadow');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePauseResumeShadow = async () => {
    if (!workflow || !workflow.shadow_result) return;
    setActionLoading(true);
    try {
      const simId = workflow.shadow_result.simulation_id;
      if (workflow.shadow_result.status === 'ACTIVE') {
        const res = await api.pauseShadowTrading(workflow.strategy_spec?.strategy_id || 'strat', simId);
        setWorkflow({ ...workflow, shadow_result: res });
      } else {
        const res = await api.startShadowTrading(workflow.strategy_spec?.strategy_id || 'strat', ticker);
        setWorkflow({ ...workflow, shadow_result: res });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <DisclaimerBanner />


      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
          background: 'var(--bg-secondary)',
          padding: '20px 24px',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-sm)'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={20} color="var(--accent-cyan)" />
            <h1 style={{ fontSize: '20px', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
              Autonomous Research & Strategy Workflow Hub
            </h1>
            <span
              style={{
                fontSize: '11px',
                padding: '2px 8px',
                borderRadius: '12px',
                background: 'rgba(6, 182, 212, 0.15)',
                color: 'var(--accent-cyan)',
                fontWeight: 600
              }}
            >
              LANGGRAPH STATEFUL
            </span>
          </div>
          <p style={{ margin: '6px 0 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
            Strict multi-stage pipeline: Market Data &rarr; Evidence Retrieval &rarr; Strategy Spec &rarr; Candidate Code &rarr; QA &rarr; Backtest &rarr; Human Approval &rarr; Shadow Simulation &rarr; Decision Recommendation.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <select
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            disabled={loading}
            style={{
              padding: '10px 16px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-primary)',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <option value="AAPL">Apple Inc. (AAPL)</option>
            <option value="MSFT">Microsoft Corp. (MSFT)</option>
            <option value="NVDA">NVIDIA Corp. (NVDA)</option>
          </select>

          <button
            onClick={handleStartWorkflow}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
              color: '#ffffff',
              border: 'none',
              fontWeight: 600,
              fontSize: '14px',
              cursor: loading ? 'not-allowed' : 'pointer',
              boxShadow: '0 0 16px var(--accent-cyan-glow)'
            }}
          >
            {loading ? <Clock size={16} className="spin" /> : <Play size={16} />}
            {loading ? 'Executing Pipeline...' : 'Initiate Autonomous Workflow'}
          </button>
        </div>
      </div>


      <div
        style={{
          background: 'var(--bg-secondary)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-subtle)',
          padding: '20px',
          marginBottom: '24px'
        }}
      >
        <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '12px', textTransform: 'uppercase' }}>
          LangGraph Stateful Execution Pipeline
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(9, 1fr)', gap: '8px' }}>
          {stages.map((s, idx) => {
            const isCompleted = workflow?.history.some((h) => h.node.includes(s.key) && h.status.includes('completed')) || false;
            const isWaiting = workflow?.status === 'WAITING_APPROVAL' && s.key === 'human_approval';
            const isActive = workflow?.stage === s.key;

            return (
              <div
                key={s.key}
                style={{
                  padding: '10px',
                  borderRadius: 'var(--radius-sm)',
                  background: isWaiting
                    ? 'rgba(234, 179, 8, 0.15)'
                    : isCompleted
                    ? 'rgba(16, 185, 129, 0.12)'
                    : isActive
                    ? 'rgba(6, 182, 212, 0.15)'
                    : 'var(--bg-tertiary)',
                  border: `1px solid ${
                    isWaiting
                      ? 'var(--accent-amber)'
                      : isCompleted
                      ? 'var(--accent-emerald)'
                      : isActive
                      ? 'var(--accent-cyan)'
                      : 'var(--border-subtle)'
                  }`,
                  textAlign: 'center'
                }}
              >
                <div style={{ fontSize: '11px', fontWeight: 700, color: isWaiting ? 'var(--accent-amber)' : isCompleted ? 'var(--accent-emerald)' : 'var(--text-primary)' }}>
                  {s.label}
                </div>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {s.desc}
                </div>
                <div style={{ marginTop: '6px' }}>
                  {isWaiting ? (
                    <span style={{ fontSize: '9px', color: 'var(--accent-amber)', fontWeight: 600 }}>PAUSED</span>
                  ) : isCompleted ? (
                    <CheckCircle2 size={12} color="var(--accent-emerald)" style={{ margin: '0 auto' }} />
                  ) : (
                    <span style={{ fontSize: '9px', color: 'var(--text-muted)' }}>PENDING</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>


      {workflow && (
        <div>

          <div
            style={{
              display: 'flex',
              gap: '8px',
              borderBottom: '1px solid var(--border-subtle)',
              marginBottom: '20px',
              overflowX: 'auto'
            }}
          >
            {[
              { id: 'evidence', label: 'Research Evidence & Citations', icon: FileText },
              { id: 'strategy', label: 'Strategy Specification & Code', icon: Code },
              { id: 'qa', label: 'QA & Bias Audit', icon: CheckSquare },
              { id: 'backtest', label: 'Deterministic Backtest', icon: BarChart3 },
              { id: 'approval', label: 'Human Approval Gate', icon: ShieldCheck, badge: workflow.status === 'WAITING_APPROVAL' ? 'REQUIRED' : undefined },
              { id: 'shadow', label: 'Shadow Simulation', icon: TrendingUp },
              { id: 'audit', label: 'Audit Lineage', icon: Clock }
            ].map((tab) => {
              const Icon = tab.icon;
              const isSelected = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px 18px',
                    background: 'none',
                    border: 'none',
                    borderBottom: isSelected ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                    color: isSelected ? 'var(--accent-cyan)' : 'var(--text-muted)',
                    fontWeight: isSelected ? 600 : 500,
                    fontSize: '13px',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap'
                  }}
                >
                  <Icon size={16} />
                  {tab.label}
                  {tab.badge && (
                    <span
                      style={{
                        fontSize: '9px',
                        padding: '2px 6px',
                        borderRadius: '8px',
                        background: 'rgba(234, 179, 8, 0.2)',
                        color: 'var(--accent-amber)',
                        fontWeight: 700
                      }}
                    >
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>


          <div style={{ background: 'var(--bg-secondary)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-subtle)', padding: '24px' }}>

            {activeTab === 'evidence' && workflow.research_output && (
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
                  Retrieved SEC Form 10-K Evidence & Claims
                </h3>
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>Grounded Analytical Claims:</div>
                  <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-primary)', fontSize: '13px', lineHeight: 1.6 }}>
                    {workflow.research_output.claims.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>Verified Source Citations:</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '12px' }}>
                  {workflow.research_output.sources.map((s, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '14px',
                        borderRadius: 'var(--radius-md)',
                        background: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-subtle)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-cyan)' }}>
                          {s.title} (Page {s.page})
                        </span>
                        <span style={{ fontSize: '10px', padding: '2px 6px', background: 'rgba(255,255,255,0.06)', borderRadius: '4px', color: 'var(--text-muted)' }}>
                          Similarity: {(s.score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 8px 0', lineHeight: 1.5 }}>
                        "{s.snippet}"
                      </p>
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                        Chunk ID: {s.chunk_id} | Hash: {s.content_hash.slice(0, 12)}...
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}


            {activeTab === 'strategy' && workflow.strategy_spec && (
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
                  Strategy Specification & Generated Python Implementation
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Strategy Hypothesis</div>
                    <div style={{ fontSize: '13px', color: 'var(--text-primary)', marginTop: '4px', fontWeight: 500 }}>
                      {workflow.strategy_spec.hypothesis}
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Holding Period & Risk Constraints</div>
                    <div style={{ fontSize: '13px', color: 'var(--text-primary)', marginTop: '4px' }}>
                      Horizon: {workflow.strategy_spec.holding_period} | Max DD Limit: {(workflow.strategy_spec.risk_constraints.max_drawdown_limit * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                {workflow.candidate_code && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Developer Agent Candidate Code (Sandbox Isolated):</span>
                      <span style={{ fontSize: '11px', color: 'var(--accent-emerald)', fontWeight: 600 }}>STATUS: {workflow.candidate_code.review_status.toUpperCase()}</span>
                    </div>
                    <pre
                      style={{
                        padding: '16px',
                        borderRadius: 'var(--radius-md)',
                        background: '#0d1117',
                        color: '#c9d1d9',
                        fontSize: '12px',
                        fontFamily: 'Consolas, Monaco, monospace',
                        overflowX: 'auto',
                        border: '1px solid var(--border-subtle)'
                      }}
                    >
                      {workflow.candidate_code.source_code}
                    </pre>
                  </div>
                )}
              </div>
            )}


            {activeTab === 'qa' && workflow.qa_results && (
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
                  QA Agent Static & Dynamic Security Verification
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginBottom: '20px' }}>
                  {[
                    { label: 'AST Static Security', passed: workflow.qa_results.ast_valid },
                    { label: 'Subprocess Sandbox', passed: workflow.qa_results.unit_tests_passed },
                    { label: 'Financial Invariants', passed: workflow.qa_results.invariants_passed },
                    { label: 'Look-Ahead Bias Test', passed: workflow.qa_results.lookahead_passed },
                    { label: 'Data Leakage Test', passed: workflow.qa_results.leakage_passed }
                  ].map((chk, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '14px',
                        borderRadius: 'var(--radius-md)',
                        background: chk.passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        border: `1px solid ${chk.passed ? 'var(--accent-emerald)' : 'var(--accent-rose)'}`,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px'
                      }}
                    >
                      {chk.passed ? <CheckCircle2 size={18} color="var(--accent-emerald)" /> : <AlertTriangle size={18} color="var(--accent-rose)" />}
                      <div>
                        <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>{chk.label}</div>
                        <div style={{ fontSize: '10px', color: chk.passed ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                          {chk.passed ? 'VERIFIED PASSED' : 'CHECK FAILED'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>Detailed Execution Audit Log:</div>
                <div style={{ background: 'var(--bg-tertiary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                  {workflow.qa_results.details.map((d, idx) => (
                    <div key={idx} style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px', fontFamily: 'monospace' }}>
                      &bull; {d}
                    </div>
                  ))}
                </div>
              </div>
            )}


            {activeTab === 'backtest' && workflow.backtest_result && (
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
                  Deterministic Backtest Analytics & Trade Ledger
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '20px' }}>
                  {[
                    { label: 'Sharpe Ratio', val: workflow.backtest_result.metrics.sharpe_ratio?.toFixed(2) },
                    { label: 'Sortino Ratio', val: workflow.backtest_result.metrics.sortino_ratio?.toFixed(2) },
                    { label: 'Max Drawdown', val: `${(workflow.backtest_result.metrics.max_drawdown * 100).toFixed(1)}%` },
                    { label: 'Total Return', val: `${(workflow.backtest_result.metrics.total_return * 100).toFixed(1)}%` },
                    { label: 'Hit Rate (Win %)', val: `${(workflow.backtest_result.metrics.hit_rate * 100).toFixed(1)}%` },
                    { label: 'Turnover Ratio', val: `${(workflow.backtest_result.metrics.turnover * 100).toFixed(1)}%` },
                    { label: 'Transaction Costs', val: `$${workflow.backtest_result.metrics.total_transaction_costs?.toFixed(2)}` },
                    { label: 'Slippage Incurred', val: `$${workflow.backtest_result.metrics.total_slippage_incurred?.toFixed(2)}` }
                  ].map((m, idx) => (
                    <div key={idx} style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{m.label}</div>
                      <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                        {m.val}
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Trade Ledger ({workflow.backtest_result.trades.length} Completed Hypothetical Trades):
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ background: 'var(--bg-tertiary)', textAlign: 'left', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '8px 12px' }}>Trade ID</th>
                        <th style={{ padding: '8px 12px' }}>Side</th>
                        <th style={{ padding: '8px 12px' }}>Entry Date</th>
                        <th style={{ padding: '8px 12px' }}>Entry Price</th>
                        <th style={{ padding: '8px 12px' }}>Exit Date</th>
                        <th style={{ padding: '8px 12px' }}>Exit Price</th>
                        <th style={{ padding: '8px 12px' }}>Net P&L</th>
                        <th style={{ padding: '8px 12px' }}>Return</th>
                      </tr>
                    </thead>
                    <tbody>
                      {workflow.backtest_result.trades.map((t, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                          <td style={{ padding: '8px 12px', fontWeight: 600 }}>{t.trade_id}</td>
                          <td style={{ padding: '8px 12px', color: 'var(--accent-emerald)' }}>{t.side}</td>
                          <td style={{ padding: '8px 12px' }}>{t.entry_time}</td>
                          <td style={{ padding: '8px 12px' }}>${t.entry_price.toFixed(2)}</td>
                          <td style={{ padding: '8px 12px' }}>{t.exit_time || '-'}</td>
                          <td style={{ padding: '8px 12px' }}>${t.exit_price?.toFixed(2) || '-'}</td>
                          <td style={{ padding: '8px 12px', color: (t.net_pnl || 0) >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)', fontWeight: 600 }}>
                            ${t.net_pnl?.toFixed(2) || '-'}
                          </td>
                          <td style={{ padding: '8px 12px' }}>
                            {t.return_pct ? `${(t.return_pct * 100).toFixed(2)}%` : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}


            {activeTab === 'approval' && workflow.approval_record && (
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
                  Human-in-the-Loop Governance & Approval Gate
                </h3>
                <div style={{ background: 'var(--bg-tertiary)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <div>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>APPROVAL GATE ID:</span>
                      <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>{workflow.approval_record.approval_id}</div>
                    </div>
                    <div>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>CURRENT DECISION:</span>
                      <div style={{ fontSize: '14px', fontWeight: 700, color: workflow.approval_record.decision === 'APPROVE' ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>
                        {workflow.approval_record.decision}
                      </div>
                    </div>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>ARTIFACT INTEGRITY SHA-256 HASH:</div>
                  <div style={{ fontFamily: 'monospace', fontSize: '12px', color: 'var(--accent-cyan)', wordBreak: 'break-all' }}>
                    {workflow.approval_record.artifact_hash}
                  </div>
                </div>

                {workflow.status === 'WAITING_APPROVAL' ? (
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Review Comments / Audit Rationale:
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Backtest verified, risk bounds acceptable for shadow simulation."
                      value={reviewReason}
                      onChange={(e) => setReviewReason(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '10px 14px',
                        borderRadius: 'var(--radius-md)',
                        background: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-subtle)',
                        color: 'var(--text-primary)',
                        marginBottom: '16px',
                        fontSize: '13px'
                      }}
                    />
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <button
                        onClick={() => handleApprovalDecision('APPROVE')}
                        disabled={actionLoading}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '10px 24px',
                          borderRadius: 'var(--radius-md)',
                          background: 'var(--accent-emerald)',
                          color: '#ffffff',
                          border: 'none',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        <ShieldCheck size={16} /> Approve & Activate Shadow Simulation
                      </button>
                      <button
                        onClick={() => handleApprovalDecision('REJECT')}
                        disabled={actionLoading}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '10px 24px',
                          borderRadius: 'var(--radius-md)',
                          background: 'var(--accent-rose)',
                          color: '#ffffff',
                          border: 'none',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        <ShieldAlert size={16} /> Reject Strategy
                      </button>
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: '14px', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-emerald)', fontSize: '13px' }}>
                    &check; Approval processed by {workflow.approval_record.reviewed_by || 'senior_analyst'}: "{workflow.approval_record.reason}"
                  </div>
                )}
              </div>
            )}


            {activeTab === 'shadow' && workflow.shadow_result && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                    Simulation-Only Shadow Trading Environment
                  </h3>
                  <button
                    onClick={handlePauseResumeShadow}
                    disabled={actionLoading}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '8px 16px',
                      borderRadius: 'var(--radius-md)',
                      background: workflow.shadow_result.status === 'ACTIVE' ? 'var(--accent-amber)' : 'var(--accent-emerald)',
                      color: '#ffffff',
                      border: 'none',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    {workflow.shadow_result.status === 'ACTIVE' ? <Pause size={14} /> : <Play size={14} />}
                    {workflow.shadow_result.status === 'ACTIVE' ? 'Pause Shadow Mode' : 'Resume Shadow Mode'}
                  </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '20px' }}>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Virtual Total Equity</div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                      ${workflow.shadow_result.virtual_portfolio.total_equity.toLocaleString()}
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Simulated P&L</div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: workflow.shadow_result.simulated_pnl >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)', marginTop: '4px' }}>
                      ${workflow.shadow_result.simulated_pnl.toFixed(2)}
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Virtual Shares Held</div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                      {workflow.shadow_result.virtual_portfolio.shares} shares
                    </div>
                  </div>
                  <div style={{ background: 'var(--bg-tertiary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Slippage Incurred</div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                      ${workflow.shadow_result.slippage_incurred.toFixed(2)}
                    </div>
                  </div>
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Simulated Order Ledger & Fills ({workflow.shadow_result.simulated_fills.length} Virtual Fills):
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                    <thead>
                      <tr style={{ background: 'var(--bg-tertiary)', textAlign: 'left', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '8px 12px' }}>Fill ID</th>
                        <th style={{ padding: '8px 12px' }}>Order ID</th>
                        <th style={{ padding: '8px 12px' }}>Price</th>
                        <th style={{ padding: '8px 12px' }}>Shares</th>
                        <th style={{ padding: '8px 12px' }}>Costs</th>
                        <th style={{ padding: '8px 12px' }}>Slippage</th>
                        <th style={{ padding: '8px 12px' }}>Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {workflow.shadow_result.simulated_fills.map((f, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                          <td style={{ padding: '8px 12px', fontWeight: 600 }}>{f.fill_id}</td>
                          <td style={{ padding: '8px 12px' }}>{f.order_id}</td>
                          <td style={{ padding: '8px 12px' }}>${f.price.toFixed(2)}</td>
                          <td style={{ padding: '8px 12px' }}>{f.shares}</td>
                          <td style={{ padding: '8px 12px' }}>${f.costs.toFixed(2)}</td>
                          <td style={{ padding: '8px 12px' }}>${f.slippage.toFixed(2)}</td>
                          <td style={{ padding: '8px 12px', color: 'var(--text-muted)' }}>{f.timestamp}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}


            {activeTab === 'audit' && (
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
                  End-to-End Workflow Audit Lineage
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {workflow.history.map((h, i) => (
                    <div
                      key={i}
                      style={{
                        padding: '12px 16px',
                        borderRadius: 'var(--radius-md)',
                        background: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-subtle)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}
                    >
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                          {h.node} &rarr; <span style={{ color: 'var(--accent-cyan)' }}>{h.status.toUpperCase()}</span>
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                          Details: {JSON.stringify(h.details)}
                        </div>
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {new Date(h.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>


          {workflow.recommendation && (
            <div
              style={{
                marginTop: '24px',
                padding: '24px',
                borderRadius: 'var(--radius-lg)',
                background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(16, 185, 129, 0.1))',
                border: '1px solid var(--accent-cyan)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  FINAL INSTITUTIONAL RESEARCH RECOMMENDATION
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '6px' }}>
                  <span
                    style={{
                      fontSize: '24px',
                      fontWeight: 800,
                      padding: '4px 16px',
                      borderRadius: '8px',
                      background: workflow.recommendation.action === 'BUY' ? 'var(--accent-emerald)' : 'var(--accent-amber)',
                      color: '#ffffff'
                    }}
                  >
                    {workflow.recommendation.action}
                  </span>
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {ticker} &bull; Horizon: {workflow.recommendation.time_horizon}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      Model Confidence: {(workflow.recommendation.confidence * 100).toFixed(0)}% | Strategy: {workflow.recommendation.strategy_id} (v{workflow.recommendation.strategy_version})
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'right', maxWidth: '400px' }}>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {workflow.recommendation.disclaimer}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkflowPage;
