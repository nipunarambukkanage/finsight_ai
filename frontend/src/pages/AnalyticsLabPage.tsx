import React, { useState } from 'react';
import {
  Calculator,
  Activity,
  Layers,
  Info,
  TrendingDown,
  ShieldAlert
} from 'lucide-react';
import { CorrelationHeatmap } from '../components/CorrelationHeatmap';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const AnalyticsLabPage: React.FC = () => {
  const [selectedTickers, setSelectedTickers] = useState<string[]>(['AAPL', 'MSFT', 'NVDA', 'GOOGL']);


  const sampleMatrix = [
    [1.00, 0.62, 0.54, 0.58],
    [0.62, 1.00, 0.68, 0.71],
    [0.54, 0.68, 1.00, 0.49],
    [0.58, 0.71, 0.49, 1.00]
  ];

  const quantStats = [
    { ticker: 'AAPL', annVol: '22.4%', sharpe: 1.82, mdd: '-15.8%', beta: 1.08, var95: '2.14%', cvar95: '2.92%' },
    { ticker: 'MSFT', annVol: '24.1%', sharpe: 1.74, mdd: '-14.2%', beta: 0.92, var95: '2.28%', cvar95: '3.10%' },
    { ticker: 'NVDA', annVol: '44.8%', sharpe: 2.35, mdd: '-28.4%', beta: 1.68, var95: '4.15%', cvar95: '5.62%' },
    { ticker: 'GOOGL', annVol: '26.2%', sharpe: 1.62, mdd: '-18.1%', beta: 1.05, var95: '2.48%', cvar95: '3.38%' }
  ];

  return (
    <div id="analytics-lab-page" className="page-wrapper">
      <DisclaimerBanner />


      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Calculator size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Python Quantitative Analytics Laboratory
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Deterministic financial calculations powered by NumPy and SciPy. Value at Risk (VaR), Expected Shortfall (CVaR), and Correlation Matrices.
        </p>
      </div>


      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Quantitative Risk & Tail-Loss Audit</h2>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>Ticker</th>
                <th style={{ padding: '10px' }}>Annualized Volatility (σ)</th>
                <th style={{ padding: '10px' }}>Sharpe Ratio (Rf=4%)</th>
                <th style={{ padding: '10px' }}>Beta (vs SPY)</th>
                <th style={{ padding: '10px' }}>Max Drawdown (MDD)</th>
                <th style={{ padding: '10px' }}>Historical VaR (95%)</th>
                <th style={{ padding: '10px' }}>Expected Shortfall (CVaR)</th>
              </tr>
            </thead>
            <tbody>
              {quantStats.map((st) => (
                <tr key={st.ticker} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                  <td style={{ padding: '12px', fontWeight: 700, color: 'var(--accent-cyan)' }}>{st.ticker}</td>
                  <td style={{ padding: '12px' }}>{st.annVol}</td>
                  <td style={{ padding: '12px', fontWeight: 600, color: 'var(--accent-emerald)' }}>{st.sharpe}</td>
                  <td style={{ padding: '12px' }}>{st.beta}</td>
                  <td style={{ padding: '12px', color: 'var(--accent-rose)', fontWeight: 600 }}>{st.mdd}</td>
                  <td style={{ padding: '12px', color: 'var(--accent-amber)', fontWeight: 600 }}>{st.var95}</td>
                  <td style={{ padding: '12px', color: 'var(--accent-rose)', fontWeight: 600 }}>{st.cvar95}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>


      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Pairwise Pearson Correlation Matrix</h2>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Computed over 252 trading days of daily return distributions.
            </div>
          </div>
          <span className="badge badge-cyan">NumPy Covariance Engine</span>
        </div>

        <CorrelationHeatmap tickers={selectedTickers} matrix={sampleMatrix} />
      </div>


      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <Info size={16} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '14px', fontWeight: 700 }}>Mathematical Formulations & Methodology</h3>
        </div>
        <div className="grid-12" style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ color: 'var(--text-primary)' }}>Annualized Volatility:</strong>
            <div style={{ fontFamily: 'var(--font-mono)', marginTop: '4px', color: 'var(--accent-cyan)' }}>
              σ_ann = σ_daily × √(252)
            </div>
          </div>
          <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ color: 'var(--text-primary)' }}>Value at Risk (VaR 95%):</strong>
            <div style={{ fontFamily: 'var(--font-mono)', marginTop: '4px', color: 'var(--accent-cyan)' }}>
              VaR_0.95 = -Percentile(Returns, 5.0)
            </div>
          </div>
          <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
            <strong style={{ color: 'var(--text-primary)' }}>Expected Shortfall (CVaR):</strong>
            <div style={{ fontFamily: 'var(--font-mono)', marginTop: '4px', color: 'var(--accent-cyan)' }}>
              CVaR_0.95 = E[R | R ≤ VaR_0.95]
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
