import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  TrendingUp,
  TrendingDown,
  Sparkles,
  Bot,
  Activity,
  Shield,
  BarChart2,
  Info,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { api } from '../api/client';
import { PriceChart } from '../components/PriceChart';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const StockWorkspacePage: React.FC = () => {
  const { ticker = 'AAPL' } = useParams<{ ticker: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'technicals' | 'fundamentals' | 'risk'>('technicals');
  const [timeframeDays, setTimeframeDays] = useState<number>(252);

  const activeTicker = ticker.toUpperCase();

  const { data: detail, isLoading } = useQuery({
    queryKey: ['stock-detail', activeTicker],
    queryFn: () => api.getStockDetail(activeTicker),
    staleTime: 60000
  });

  const { data: prices } = useQuery({
    queryKey: ['stock-prices', activeTicker, timeframeDays],
    queryFn: () => api.getStockPrices(activeTicker, timeframeDays),
    staleTime: 60000
  });

  if (isLoading && !detail) {
    return (
      <div className="page-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <Activity size={32} color="var(--accent-cyan)" className="animate-pulse-glow" />
          <div style={{ marginTop: '16px', color: 'var(--text-secondary)' }}>Loading institutional market data for {activeTicker}...</div>
        </div>
      </div>
    );
  }

  const overview = detail?.overview || {
    ticker: activeTicker,
    name: 'Apple Inc.',
    sector: 'Technology',
    industry: 'Consumer Electronics',
    current_price: 235.50,
    change_percent: 1.42,
    market_cap: 3580000000000,
    pe_ratio: 34.2,
    forward_pe: 29.8,
    dividend_yield: 0.44,
    beta: 1.08,
    week_52_high: 245.30,
    week_52_low: 164.08,
    description: 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories.'
  };

  const technicals = detail?.technicals || {
    rsi: 54.2,
    macd: 1.25,
    macd_signal: 0.95,
    macd_hist: 0.30,
    sma_20: 228.40,
    sma_50: 221.10,
    sma_200: 204.50,
    bb_upper: 242.10,
    bb_middle: 228.40,
    bb_lower: 215.30
  };

  const risk = detail?.risk_stats || {
    annualized_volatility: 0.224,
    sharpe_ratio: 1.82,
    sortino_ratio: 2.15,
    max_drawdown: -0.158,
    beta: 1.08,
    var_95_daily: 0.021,
    var_99_daily: 0.034,
    cvar_95_daily: 0.029
  };

  const funds = detail?.fundamentals || {
    revenue_ttm: 391035000000,
    gross_margin: 0.462,
    operating_margin: 0.315,
    net_margin: 0.240,
    eps_ttm: 6.08,
    fcf_ttm: 108800000000,
    debt_to_equity: 1.52,
    roe: 1.47,
    current_ratio: 0.99
  };

  const isPos = overview.change_percent >= 0;

  return (
    <div id="stock-workspace-page" className="page-wrapper">
      <DisclaimerBanner />

      {/* Ticker Selector Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '20px',
          flexWrap: 'wrap',
          gap: '16px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '28px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {overview.ticker}
              </h1>
              <span style={{ fontSize: '18px', color: 'var(--text-secondary)', fontWeight: 500 }}>
                {overview.name}
              </span>
              <span className="badge badge-cyan">Simulated Institutional Dataset</span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              {overview.sector} · {overview.industry} · Beta: {overview.beta}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            id="agent-investigate-btn"
            className="btn btn-primary"
            onClick={() => navigate(`/research-agent?ticker=${overview.ticker}`)}
          >
            <Sparkles size={16} />
            <span>Generate Full Agent Report</span>
          </button>
          <button
            id="assistant-ask-ticker-btn"
            className="btn btn-secondary"
            onClick={() => navigate(`/assistant?q=${encodeURIComponent(`Explain ${overview.ticker}'s recent financial performance and valuation`)}`)}
          >
            <Bot size={16} />
            <span>Ask AI Assistant</span>
          </button>
        </div>
      </div>

      {/* Price & Primary Multiples Banner */}
      <div className="grid-12" style={{ marginBottom: '24px' }}>
        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>CURRENT PRICE</div>
          <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
            ${overview.current_price.toFixed(2)}
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              color: isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)',
              marginTop: '4px',
              fontWeight: 600,
              fontSize: '12px'
            }}
          >
            {isPos ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>{isPos ? '+' : ''}{overview.change_percent.toFixed(2)}% Today</span>
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>MARKET CAPITALIZATION</div>
          <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
            ${(overview.market_cap / 1e12).toFixed(2)} Trillion
          </div>
          <div style={{ color: 'var(--text-muted)', marginTop: '4px', fontSize: '12px' }}>
            Shares Outstanding: {(overview.market_cap / overview.current_price / 1e9).toFixed(2)}B
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>VALUATION (P/E)</div>
          <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
            {overview.pe_ratio}x
          </div>
          <div style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '12px' }}>
            Forward P/E: {overview.forward_pe}x · Div: {overview.dividend_yield}%
          </div>
        </div>

        <div className="col-3 glass-card">
          <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>52-WEEK RANGE</div>
          <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '6px' }}>
            ${overview.week_52_low.toFixed(2)} - ${overview.week_52_high.toFixed(2)}
          </div>
          <div style={{ color: 'var(--text-muted)', marginTop: '4px', fontSize: '12px' }}>
            Range Spread: ${ (overview.week_52_high - overview.week_52_low).toFixed(2) }
          </div>
        </div>
      </div>

      {/* Interactive Price Chart Section */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Historical Price Action & Volume</h2>
            <span className="badge badge-emerald">Interactive Canvas</span>
          </div>

          {/* Timeframe Selectors */}
          <div style={{ display: 'flex', gap: '6px' }}>
            {[
              { label: '1M', days: 22 },
              { label: '3M', days: 66 },
              { label: '6M', days: 130 },
              { label: '1Y', days: 252 }
            ].map((tf) => (
              <button
                key={tf.label}
                className={`btn btn-sm ${timeframeDays === tf.days ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setTimeframeDays(tf.days)}
              >
                {tf.label}
              </button>
            ))}
          </div>
        </div>

        <PriceChart
          prices={prices && prices.length > 0 ? prices : (detail?.prices || [])}
          height={400}
          showSMA={true}
        />
      </div>

      {/* Tabs: Technicals vs Fundamentals vs Risk Statistics */}
      <div className="glass-card">
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-subtle)', marginBottom: '20px', gap: '20px' }}>
          {[
            { key: 'technicals', label: 'Technical Indicators' },
            { key: 'fundamentals', label: 'Fundamental Financials' },
            { key: 'risk', label: 'Quantitative Risk & VaR' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              style={{
                background: 'none',
                border: 'none',
                padding: '10px 4px',
                fontSize: '14px',
                fontWeight: activeTab === tab.key ? 700 : 500,
                color: activeTab === tab.key ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                borderBottom: activeTab === tab.key ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                cursor: 'pointer'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'technicals' && (
          <div className="grid-12">
            <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>RSI (14 PERIOD)</div>
              <div style={{ fontSize: '24px', fontWeight: 700, marginTop: '6px' }}>{technicals.rsi}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Neutral range (30 - 70). No immediate overbought or oversold exhaustion.
              </div>
            </div>

            <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>MACD (12, 26, 9)</div>
              <div style={{ fontSize: '24px', fontWeight: 700, marginTop: '6px' }}>{technicals.macd}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Signal: {technicals.macd_signal} · Histogram: <strong style={{ color: 'var(--accent-emerald)' }}>+{technicals.macd_hist}</strong>
              </div>
            </div>

            <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>MOVING AVERAGES</div>
              <div style={{ fontSize: '13px', marginTop: '6px', lineHeight: 1.8 }}>
                <div>SMA 20: <strong>${technicals.sma_20}</strong></div>
                <div>SMA 50: <strong>${technicals.sma_50}</strong></div>
                <div>SMA 200: <strong>${technicals.sma_200}</strong></div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'fundamentals' && (
          <div className="grid-12">
            <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>REVENUE (TTM)</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>${(funds.revenue_ttm / 1e9).toFixed(1)}B</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Gross Margin: {(funds.gross_margin * 100).toFixed(1)}%</div>
            </div>

            <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>OPERATING MARGIN</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>{(funds.operating_margin * 100).toFixed(1)}%</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Net Margin: {(funds.net_margin * 100).toFixed(1)}%</div>
            </div>

            <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>FREE CASH FLOW</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>${(funds.fcf_ttm / 1e9).toFixed(1)}B</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Cash Flow Conversion: High</div>
            </div>

            <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>LEVERAGE & ROE</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>ROE: {(funds.roe * 100).toFixed(1)}%</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Debt-to-Equity: {funds.debt_to_equity}x</div>
            </div>
          </div>
        )}

        {activeTab === 'risk' && (
          <div className="grid-12">
            <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>ANNUALIZED VOLATILITY</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>{(risk.annualized_volatility * 100).toFixed(1)}%</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Beta vs S&P 500: {risk.beta}</div>
            </div>

            <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>RISK-ADJUSTED RETURNS</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>Sharpe: {risk.sharpe_ratio}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Sortino (Downside): {risk.sortino_ratio}</div>
            </div>

            <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>VALUE AT RISK (VaR 95%)</div>
              <div style={{ fontSize: '22px', fontWeight: 700, marginTop: '6px' }}>{(risk.var_95_daily * 100).toFixed(2)}% (1-Day)</div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Expected Shortfall (CVaR): {(risk.cvar_95_daily * 100).toFixed(2)}%
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
