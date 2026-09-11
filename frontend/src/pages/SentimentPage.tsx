import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart2,
  Send,
  Zap,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Clock,
  Layers
} from 'lucide-react';
import { api } from '../api/client';
import { SentimentResponse } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const SentimentPage: React.FC = () => {
  const [inputText, setInputText] = useState(
    'Apple reports record services revenue beat with accelerating margin expansion and strong forward guidance.'
  );
  const [result, setResult] = useState<SentimentResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const { data: distribution } = useQuery({
    queryKey: ['sentiment-overview'],
    queryFn: api.getSentimentOverview,
    staleTime: 60000
  });

  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || analyzing) return;

    setAnalyzing(true);
    try {
      const res = await api.analyzeSentiment(inputText);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const sampleHeadlines = [
    'NVIDIA unveils Blackwell AI architecture with unprecedented enterprise customer backlog.',
    'Company warns of macroeconomic recession headwinds and cuts full-year capital expenditure.',
    'Board authorizes standard quarterly cash dividend of $0.25 per common share payable in May.',
    'Regulatory antitrust lawsuits could force restructuring of mobile application commission structures.'
  ];

  return (
    <div id="sentiment-page" className="page-wrapper">
      <DisclaimerBanner />


      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <BarChart2 size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Financial Sentiment Engine (Hugging Face FinBERT)
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Domain-specific transformer NLP for financial headline classification, key catalyst phrase extraction, and sentiment distribution tracking.
        </p>
      </div>


      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px' }}>Analyze Financial Commentary</h2>

        <form onSubmit={handleAnalyze}>
          <textarea
            id="sentiment-input-textarea"
            aria-label="Financial commentary"
            className="input-text"
            rows={3}
            placeholder="Enter earnings call commentary, analyst report note, or financial headline..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            style={{ resize: 'vertical', marginBottom: '12px' }}
          />

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>

            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', alignSelf: 'center' }}>Samples:</span>
              {sampleHeadlines.map((h, i) => (
                <button
                  key={i}
                  type="button"
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: '11px' }}
                  onClick={() => setInputText(h)}
                >
                  Headline #{i + 1}
                </button>
              ))}
            </div>

            <button
              id="analyze-sentiment-btn"
              type="submit"
              className="btn btn-primary"
              disabled={analyzing}
            >
              <Zap size={16} />
              <span>{analyzing ? 'Evaluating FinBERT...' : 'Classify Sentiment'}</span>
            </button>
          </div>
        </form>


        {result && (
          <div
            id="sentiment-result-card"
            style={{
              marginTop: '20px',
              padding: '18px',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span
                  className={`badge ${
                    result.label === 'Positive'
                      ? 'badge-emerald'
                      : result.label === 'Negative'
                      ? 'badge-rose'
                      : 'badge-cyan'
                  }`}
                  style={{ fontSize: '13px', padding: '4px 12px' }}
                >
                  {result.label === 'Positive' && <TrendingUp size={14} />}
                  {result.label === 'Negative' && <TrendingDown size={14} />}
                  <span>{result.label}</span>
                </span>
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  Confidence Score: <strong style={{ color: 'var(--text-primary)' }}>{(result.score * 100).toFixed(1)}%</strong>
                </span>
              </div>
              <span className="badge badge-purple" style={{ fontSize: '10px' }}>{result.model_used}</span>
            </div>

            <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.6, marginBottom: '14px' }}>
              {result.explanation}
            </div>


            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '6px' }}>
                IDENTIFIED FINANCIAL PHRASES & DRIVERS:
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {result.key_phrases.map((phrase, idx) => (
                  <span key={idx} className="badge badge-cyan" style={{ fontSize: '11px' }}>
                    "{phrase}"
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>


      <div className="grid-12">
        <div className="col-6 glass-card">
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Market Sentiment Distribution</h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>Positive Sentiment</span>
                <span>{distribution ? `${distribution.positive_pct}%` : '60.0%'}</span>
              </div>
              <div style={{ height: '8px', backgroundColor: 'var(--bg-surface)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${distribution ? distribution.positive_pct : 60}%`, height: '100%', backgroundColor: 'var(--accent-emerald)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Neutral Sentiment</span>
                <span>{distribution ? `${distribution.neutral_pct}%` : '25.0%'}</span>
              </div>
              <div style={{ height: '8px', backgroundColor: 'var(--bg-surface)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${distribution ? distribution.neutral_pct : 25}%`, height: '100%', backgroundColor: 'var(--accent-cyan)' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                <span style={{ color: 'var(--accent-rose)', fontWeight: 600 }}>Negative Sentiment</span>
                <span>{distribution ? `${distribution.negative_pct}%` : '15.0%'}</span>
              </div>
              <div style={{ height: '8px', backgroundColor: 'var(--bg-surface)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${distribution ? distribution.negative_pct : 15}%`, height: '100%', backgroundColor: 'var(--accent-rose)' }} />
              </div>
            </div>
          </div>
        </div>

        <div className="col-6 glass-card">
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Earnings Sentiment Progression</h2>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', height: '140px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)', padding: '10px' }}>
            {(distribution?.timeline || [
              { date: '2024-Q1', score: 0.42 },
              { date: '2024-Q2', score: 0.15 },
              { date: '2024-Q3', score: 0.58 },
              { date: '2024-Q4', score: 0.65 }
            ]).map((point) => (
              <div key={point.date} style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: 700,
                    color: point.score >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                    marginBottom: '8px'
                  }}
                >
                  {point.score >= 0 ? '+' : ''}{point.score}
                </div>
                <div
                  style={{
                    width: '32px',
                    height: `${Math.max(20, Math.abs(point.score) * 80)}px`,
                    backgroundColor: point.score >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                    borderRadius: '4px',
                    margin: '0 auto',
                    opacity: 0.85
                  }}
                />
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>{point.date}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
