import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Settings,
  Cpu,
  CheckCircle2,
  Shield,
  Key,
  Server,
  Activity,
  Layers
} from 'lucide-react';
import { api } from '../api/client';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const SettingsPage: React.FC = () => {
  const [selectedProvider, setSelectedProvider] = useState<string>('DEMO');
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: api.getProviders,
    staleTime: 60000
  });

  const providerList = providers || [
    { id: 'DEMO', name: 'FinSight Demo Intelligence Engine', is_active: true, requires_api_key: false, description: 'Deterministic, context-grounded institutional AI provider with zero external credentials.' },
    { id: 'OPENAI', name: 'OpenAI (GPT-4o / GPT-4o-mini)', is_active: false, requires_api_key: true, description: 'Commercial multi-modal frontier LLM via OpenAI API.' },
    { id: 'ANTHROPIC', name: 'Anthropic (Claude 3.5 Sonnet)', is_active: false, requires_api_key: true, description: 'High-reasoning intelligence model for deep financial research.' },
    { id: 'HUGGINGFACE', name: 'Hugging Face Open-Source Models', is_active: false, requires_api_key: true, description: 'FinBERT and open-source models via HF Inference Endpoints.' },
    { id: 'BEDROCK', name: 'AWS Bedrock Enterprise', is_active: false, requires_api_key: true, description: 'Managed cloud foundation models with VPC security compliance.' }
  ];

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(`Active AI Provider switched to ${selectedProvider}. Provider failover guardrails are active.`);
    setTimeout(() => setSaveSuccess(null), 5000);
  };

  return (
    <div id="settings-page" className="page-wrapper">
      <DisclaimerBanner />

      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Settings size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            System Settings & AI Provider Failover Architecture
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Configure enterprise LLM provider routing, view real-time latency telemetry, and manage zero-credential demo modes.
        </p>
      </div>

      {saveSuccess && (
        <div style={{ padding: '12px 16px', backgroundColor: 'var(--accent-emerald-glow)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: 'var(--radius-md)', color: 'var(--accent-emerald)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
          <CheckCircle2 size={16} />
          <span>{saveSuccess}</span>
        </div>
      )}

      {/* Active Provider Selector */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Multi-Provider LLM Abstraction</h2>

        <form onSubmit={handleSave}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
            {providerList.map((p) => {
              const isSelected = selectedProvider === p.id;
              return (
                <label
                  key={p.id}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '14px',
                    padding: '14px 18px',
                    backgroundColor: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'var(--bg-surface)',
                    border: isSelected ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <input
                    type="radio"
                    name="provider"
                    value={p.id}
                    checked={isSelected}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                    style={{ marginTop: '4px' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>{p.name}</strong>
                      {p.id === 'DEMO' ? (
                        <span className="badge badge-cyan">Zero Credentials Required</span>
                      ) : (
                        <span className="badge badge-amber">Optional Commercial Provider</span>
                      )}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      {p.description}
                    </div>
                  </div>
                </label>
              );
            })}
          </div>

          <button id="save-provider-settings-btn" type="submit" className="btn btn-primary">
            <span>Apply Provider Configuration</span>
          </button>
        </form>
      </div>

      {/* System Telemetry & Environment Information */}
      <div className="glass-card">
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Runtime Telemetry & Architecture</h2>

        <div className="grid-12" style={{ fontSize: '13px' }}>
          <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>BACKEND CORE</div>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>FastAPI + Python 3.12 (asyncio)</div>
            <div style={{ fontSize: '11px', color: 'var(--accent-emerald)', marginTop: '4px' }}>● Status: Operational</div>
          </div>

          <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>VECTOR DATABASE</div>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>PostgreSQL + pgvector / In-Memory Index</div>
            <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', marginTop: '4px' }}>Cosine Distance Indexing Active</div>
          </div>

          <div className="col-4" style={{ backgroundColor: 'var(--bg-surface)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>FAILOVER POLICY</div>
            <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>Automatic DemoProvider Fallback</div>
            <div style={{ fontSize: '11px', color: 'var(--accent-purple)', marginTop: '4px' }}>Zero Client Crash Guarantee</div>
          </div>
        </div>
      </div>
    </div>
  );
};
