import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Activity, Cpu, Moon, Sun, Shield, Bell } from 'lucide-react';
import { StockOverview } from '../types';

interface NavbarProps {
  stocks?: StockOverview[];
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ stocks = [], theme, onToggleTheme }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/stocks/${searchQuery.trim().toUpperCase()}`);
      setSearchQuery('');
    }
  };

  const tickerItems = stocks.length > 0 ? stocks : [
    { ticker: 'AAPL', current_price: 235.50, change_percent: 1.42 },
    { ticker: 'MSFT', current_price: 428.20, change_percent: 0.85 },
    { ticker: 'NVDA', current_price: 128.80, change_percent: 3.15 },
    { ticker: 'GOOGL', current_price: 182.40, change_percent: -0.45 },
    { ticker: 'AMZN', current_price: 194.20, change_percent: 1.12 },
    { ticker: 'TSLA', current_price: 242.10, change_percent: -1.80 }
  ];

  return (
    <header
      id="main-navbar"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 40,
        backgroundColor: 'var(--bg-glass)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Ticker Tape */}
      <div className="ticker-tape">
        {tickerItems.map((stk) => {
          const isPos = stk.change_percent >= 0;
          return (
            <div
              key={stk.ticker}
              className="ticker-item"
              id={`ticker-item-${stk.ticker}`}
              onClick={() => navigate(`/stocks/${stk.ticker}`)}
            >
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{stk.ticker}</span>
              <span style={{ color: 'var(--text-secondary)' }}>${stk.current_price.toFixed(2)}</span>
              <span style={{ color: isPos ? 'var(--accent-emerald)' : 'var(--accent-rose)', fontWeight: 600 }}>
                {isPos ? '+' : ''}{stk.change_percent.toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>

      {/* Main Bar */}
      <div
        style={{
          height: 'var(--navbar-height)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 28px'
        }}
      >
        {/* Search */}
        <form onSubmit={handleSearchSubmit} style={{ position: 'relative', width: '380px' }}>
          <Search
            size={16}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)'
            }}
          />
          <input
            id="global-ticker-search"
            type="text"
            className="input-text"
            placeholder="Search stock ticker (e.g. AAPL, NVDA, MSFT)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '36px' }}
          />
        </form>

        {/* Status Indicators & Profile */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div className="badge badge-cyan" id="demo-mode-badge" title="Zero-credential institutional demo mode enabled">
            <Cpu size={12} />
            <span>Demo AI Mode Active</span>
          </div>

          <div className="badge badge-emerald" id="system-latency-badge">
            <Activity size={12} />
            <span>Latency: 28ms</span>
          </div>

          <button
            id="theme-toggle-button"
            className="btn btn-secondary btn-sm"
            onClick={onToggleTheme}
            title="Toggle theme"
          >
            {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
          </button>

          <div
            id="user-profile-badge"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              fontSize: '12px',
              fontWeight: 500
            }}
          >
            <div
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontWeight: 700,
                fontSize: '11px'
              }}
            >
              EA
            </div>
            <span>Senior Equity Analyst</span>
          </div>
        </div>
      </div>
    </header>
  );
};
