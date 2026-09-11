import React, { useState } from 'react';
import {
  Image,
  Upload,
  Sparkles,
  Layers,
  CheckCircle2,
  Shield,
  Activity,
  Maximize2
} from 'lucide-react';
import { api } from '../api/client';
import { MultimodalAnalyzeResponse } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const MultimodalPage: React.FC = () => {
  const [selectedType, setSelectedType] = useState<string>('stock_chart');
  const [prompt, setPrompt] = useState(
    'Analyze this technical candlestick chart: identify trend channel, critical support/resistance boundaries, and volume divergence.'
  );
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<MultimodalAnalyzeResponse | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setAnalyzing(true);
    try {
      const res = await api.analyzeImage(prompt, selectedType);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div id="multimodal-page" className="page-wrapper">
      <DisclaimerBanner />


      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Image size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Vision-Language Multimodal Financial Intelligence
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Provides an enterprise VLM architecture for inspecting technical price charts, SEC balance sheet tables, and earnings presentation slides.
        </p>
      </div>


      <div className="grid-12" style={{ marginBottom: '24px' }}>

        <div className="col-6 glass-card">
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Select Target Document / Chart</h2>

          <div style={{ display: 'flex', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}>
            {[
              { id: 'stock_chart', label: 'Technical Price Chart' },
              { id: 'financial_table', label: 'Balance Sheet Table' },
              { id: 'earnings_slide', label: 'Earnings Slide' }
            ].map((t) => (
              <button
                key={t.id}
                className={`btn btn-sm ${selectedType === t.id ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => {
                  setSelectedType(t.id);
                  if (t.id === 'stock_chart') setPrompt('Analyze this technical candlestick chart: identify trend channel, critical support/resistance boundaries, and volume divergence.');
                  if (t.id === 'financial_table') setPrompt('Extract all primary balance sheet line items: audit liquidity, debt maturity, and GAAP reconciliation.');
                  if (t.id === 'earnings_slide') setPrompt('Summarize key executive guidance takeaways, segment growth highlights, and forward margin targets.');
                }}
              >
                {t.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleAnalyze}>
            <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
              VISION PROMPT INSTRUCTION
            </label>
            <textarea
              id="multimodal-prompt-input"
              className="input-text"
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              style={{ resize: 'vertical', marginBottom: '16px' }}
            />

            <button
              id="run-multimodal-btn"
              type="submit"
              className="btn btn-primary"
              disabled={analyzing}
            >
              <Sparkles size={16} />
              <span>{analyzing ? 'Inspecting Visual Artifacts...' : 'Execute Vision Analysis'}</span>
            </button>
          </form>
        </div>


        <div className="col-6 glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: 'var(--bg-surface)' }}>
          <div
            style={{
              width: '100%',
              height: '240px',
              borderRadius: 'var(--radius-md)',
              border: '2px dashed var(--border-subtle)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px',
              backgroundColor: 'var(--bg-secondary)',
              color: 'var(--text-muted)'
            }}
          >
            <Image size={36} color="var(--accent-cyan)" />
            <div style={{ textAlign: 'center', padding: '0 20px' }}>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '13px' }}>
                {selectedType === 'stock_chart' ? 'AAPL Daily Candlestick Artifact' : selectedType === 'financial_table' ? 'SEC 10-K Balance Sheet Table' : 'Q3 Institutional Earnings Slide'}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Multi-channel OCR and visual feature tensor initialized
              </div>
            </div>
            <span className="badge badge-cyan">Ready for VLM Inference</span>
          </div>
        </div>
      </div>


      {result && (
        <div className="glass-card" id="multimodal-result-container">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '14px', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={18} color="var(--accent-emerald)" />
              <h2 style={{ fontSize: '16px', fontWeight: 700 }}>VLM Vision-Language Reasoning Output</h2>
            </div>
            <span className="badge badge-purple">{result.model_used}</span>
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
              marginBottom: '16px'
            }}
          >
            {result.analysis}
          </div>

          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px' }}>
              EXTRACTED VISUAL FEATURE TENSORS:
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {result.visual_features.map((feat, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--accent-cyan)' }} />
                  <span>{feat}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
