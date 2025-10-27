import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  PieChart,
  TrendingUp,
  ShieldAlert,
  Bot,
  Layers,
  ArrowUpRight,
  Activity
} from 'lucide-react';
import { api } from '../api/client';
import { DonutChart } from '../components/DonutChart';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const PortfolioPage: React.FC = () => {
  const { data: portfolio, isLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: api.getPortfolio,
    staleTime: 60000
  });

  const p = portfolio || {
    total_value: 1048250.00,
    cash_balance: 150000.00,
    invested_value: 898250.00,
    total_unrealized_pl: 165400.00,
    total_unrealized_pl_pct: 22.57,
    sharpe_ratio: 1.68,
    volatility: 0.214,
    max_drawdown: -0.142,
    sector_allocation: {
      Technology: 68.5,
      'Consumer Cyclical': 17.2,
      Cash: 14.3
    },
    holdings: [
      { ticker: 'AAPL', name: 'Apple Inc.', shares: 1200, average_cost: 195.0, current_price: 235.50, market_value: 282600.0, unrealized_pl: 48600.0, unrealized_pl_pct: 20.77, allocation_pct: 27.0 },
      { ticker: 'MSFT', name: 'Microsoft Corp.', shares: 850, average_cost: 380.0, current_price: 428.20, market_value: 363970.0, unrealized_pl: 40970.0, unrealized_pl_pct: 12.68, allocation_pct: 34.7 },
      { ticker: 'NVDA', name: 'NVIDIA Corp.', shares: 1800, average_cost: 92.5, current_price: 128.80, market_value: 231840.0, unrealized_pl: 65340.0, unrealized_pl_pct: 39.24, allocation_pct: 22.1 }
    ],
    ai_risk_assessment: "Portfolio displays high growth characteristics with a 72.4% overweight in Mega-Cap Technology and Semiconductor infrastructure. Top contributors to portfolio volatility are NVDA and AAPL. Diversification across non-cyclical cash-generating segments or defensive hedges is recommended to buffer against potential multiple compression in elevated rate environments."
  };

  return (
    <div id="portfolio-page" className="page-wrapper">
      <DisclaimerBanner />

      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <PieChart size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Institutional Portfolio Intelligence & Risk Architecture
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Multi-asset holding breakdown, sector exposures, unrealized gain/loss accounting, and AI Risk Advisor analysis.
        </p>
      </div>

      {/* Portfolio Top Metrics */}
      <div className="grid-12" style={{ marginBottom: '24px' }}>
        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>TOTAL PORTFOLIO VALUE</div>
          <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
            ${p.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-emerald)', marginTop: '4px', fontSize: '12px', fontWeight: 600 }}>
            <TrendingUp size={14} />
            <span>+${p.total_unrealized_pl.toLocaleString()} (+{p.total_unrealized_pl_pct.toFixed(2)}%)</span>
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>UNALLOCATED CASH</div>
          <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
            ${p.cash_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '12px' }}>
            Dry Powder Ratio: {((p.cash_balance / p.total_value) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>ANNUALIZED VOLATILITY</div>
          <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
            {(p.volatility * 100).toFixed(1)}%
          </div>
          <div style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '12px' }}>
            Max Drawdown: {(p.max_drawdown * 100).toFixed(1)}%
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>SHARPE RATIO (RF=4.0%)</div>
          <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
            {p.sharpe_ratio.toFixed(2)}
          </div>
          <div style={{ color: 'var(--accent-emerald)', marginTop: '4px', fontSize: '12px', fontWeight: 600 }}>
            Superior Risk-Adjusted Profile
          </div>
        </div>
      </div>

      {/* Middle Grid: Sector Donut & AI Advisor */}
      <div className="grid-12" style={{ marginBottom: '24px' }}>
        {/* Sector Allocation Donut */}
        <div className="col-6 glass-card">
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Sector & Asset Allocation</h2>
          <DonutChart data={p.sector_allocation} size={220} />
        </div>

        {/* AI Portfolio Risk Advisor */}
        <div className="col-6 glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
            <Bot size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>AI Portfolio Risk Advisor</h2>
          </div>

          <div
            style={{
              padding: '16px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              fontSize: '13px',
              lineHeight: 1.6,
              color: 'var(--text-secondary)'
            }}
          >
            <p style={{ marginBottom: '12px' }}>
              <strong style={{ color: 'var(--text-primary)' }}>Concentration Assessment:</strong> {p.ai_risk_assessment}
            </p>
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ fontSize: '12px' }}>
                • <strong>Top Volatility Contributor:</strong> NVDA (Historical Beta: 1.68)
              </div>
              <div style={{ fontSize: '12px' }}>
                • <strong>Defensive Buffer:</strong> Cash balance ($150,000) provides liquidity for opportunistic dips.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="glass-card">
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Portfolio Positions & Holdings</h2>

        <div style={{ overflowX: 'auto' }}>
          <table id="portfolio-holdings-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px' }}>Ticker</th>
                <th style={{ padding: '10px 12px' }}>Position Shares</th>
                <th style={{ padding: '10px 12px' }}>Avg Cost</th>
                <th style={{ padding: '10px 12px' }}>Market Price</th>
                <th style={{ padding: '10px 12px' }}>Current Value</th>
                <th style={{ padding: '10px 12px' }}>Unrealized Gain/Loss</th>
                <th style={{ padding: '10px 12px' }}>Allocation</th>
              </tr>
            </thead>
            <tbody>
              {p.holdings.map((h) => {
                const isPos = h.unrealized_pl >= 0;
                return (
                  <tr key={h.ticker} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '12px' }}>
                      <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{h.ticker}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{h.name}</div>
                    </td>
                    <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{h.shares.toLocaleString()}</td>
                    <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>${h.average_cost.toFixed(2)}</td>
                    <td style={{ padding: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>${h.current_price.toFixed(2)}</td>
                    <td style={{ padding: '12px', fontWeight: 600 }}>${h.market_value.toLocaleString()}</td>
                    <td style={{ padding: '12px', fontWeight: 600, color: isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                      {isPos ? '+' : ''}${h.unrealized_pl.toLocaleString()} ({isPos ? '+' : ''}{h.unrealized_pl_pct.toFixed(2)}%)
                    </td>
                    <td style={{ padding: '12px' }}>
                      <span className="badge badge-cyan">{h.allocation_pct}%</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
