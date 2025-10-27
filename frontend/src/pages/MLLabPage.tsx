import React, { useState } from 'react';
import {
  Cpu,
  AlertTriangle,
  Play,
  CheckCircle2,
  BarChart,
  Shield,
  Activity,
  Layers
} from 'lucide-react';
import { api } from '../api/client';
import { MLMetrics } from '../types';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const MLLabPage: React.FC = () => {
  const [ticker, setTicker] = useState('AAPL');
  const [modelType, setModelType] = useState('random_forest');
  const [horizon, setHorizon] = useState(5);
  const [training, setTraining] = useState(false);
  const [metrics, setMetrics] = useState<MLMetrics | null>(null);

  const handleTrain = async (e: React.FormEvent) => {
    e.preventDefault();
    setTraining(true);
    try {
      const res = await api.trainMLModel(ticker, modelType, 0.2, horizon);
      setMetrics(res);
    } catch (err) {
      console.error(err);
    } finally {
      setTraining(false);
    }
  };

  return (
    <div id="ml-lab-page" className="page-wrapper">
      <DisclaimerBanner />

      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Cpu size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Responsible Time-Series Machine Learning Lab
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Strict temporal train/test splitting without look-ahead leakage. Predicts return direction and evaluates ROC-AUC against stationary baselines.
        </p>
      </div>

      {/* Warning Alert Banner */}
      <div
        style={{
          padding: '14px 18px',
          backgroundColor: 'rgba(244, 63, 94, 0.08)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '24px',
          fontSize: '12px',
          color: '#fda4af'
        }}
      >
        <AlertTriangle size={18} style={{ flexShrink: 0, color: 'var(--accent-rose)' }} />
        <div>
          <strong>Responsible ML Methodology Notice:</strong> Financial market time-series data must NEVER be randomly shuffled. Random k-fold cross validation introduces catastrophic look-ahead bias. FinSight AI enforces chronological temporal train/test splitting.
        </div>
      </div>

      {/* Configuration Form */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Configure Pipeline Parameters</h2>

        <form onSubmit={handleTrain} style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ flex: 1, minWidth: '180px' }}>
            <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 600 }}>
              SECURITY TICKER
            </label>
            <select
              id="ml-ticker-select"
              className="input-text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
            >
              {['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1, minWidth: '220px' }}>
            <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 600 }}>
              ALGORITHM ARCHITECTURE
            </label>
            <select
              id="ml-model-select"
              className="input-text"
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
            >
              <option value="random_forest">Random Forest Classifier (100 Trees)</option>
              <option value="logistic_regression">Regularized Logistic Regression (L2)</option>
              <option value="gradient_boosting">Gradient Boosting Classifier</option>
            </select>
          </div>

          <div style={{ flex: 1, minWidth: '180px' }}>
            <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px', fontWeight: 600 }}>
              FORECAST HORIZON
            </label>
            <select
              id="ml-horizon-select"
              className="input-text"
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
            >
              <option value={1}>1-Day Forward Direction</option>
              <option value={5}>5-Day Forward Direction</option>
              <option value={10}>10-Day Forward Direction</option>
            </select>
          </div>

          <button
            id="run-ml-train-btn"
            type="submit"
            className="btn btn-primary"
            disabled={training}
            style={{ padding: '10px 20px' }}
          >
            <Play size={16} />
            <span>{training ? 'Training Model...' : 'Train & Evaluate Pipeline'}</span>
          </button>
        </form>
      </div>

      {/* ML Evaluation Output */}
      {metrics && (
        <div id="ml-results-container">
          {/* Top Metric Cards */}
          <div className="grid-12" style={{ marginBottom: '24px' }}>
            <div className="col-3 glass-card">
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>OUT-OF-SAMPLE ACCURACY</div>
              <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-cyan)' }}>
                {(metrics.accuracy * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Test Samples: {metrics.test_samples} bars
              </div>
            </div>

            <div className="col-3 glass-card">
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>PRECISION (DIRECTION UP)</div>
              <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-emerald)' }}>
                {(metrics.precision * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Recall: {(metrics.recall * 100).toFixed(1)}%
              </div>
            </div>

            <div className="col-3 glass-card">
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>ROC-AUC SCORE</div>
              <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-amber)' }}>
                {metrics.roc_auc.toFixed(3)}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Baseline Random: 0.500
              </div>
            </div>

            <div className="col-3 glass-card">
              <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>F1 SCORE</div>
              <div style={{ fontSize: '26px', fontWeight: 800, marginTop: '6px' }}>
                {metrics.f1_score.toFixed(3)}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Harmonic Mean Balance
              </div>
            </div>
          </div>

          {/* Confusion Matrix & Feature Importances */}
          <div className="grid-12" style={{ marginBottom: '24px' }}>
            {/* Confusion Matrix */}
            <div className="col-6 glass-card">
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px' }}>Out-of-Sample Confusion Matrix</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', textAlign: 'center' }}>
                <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>TRUE NEGATIVE (PREDICT DOWN, WAS DOWN)</div>
                  <div style={{ fontSize: '22px', fontWeight: 800, marginTop: '6px', color: 'var(--text-primary)' }}>
                    {metrics.confusion_matrix[0]?.[0] || 0}
                  </div>
                </div>
                <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>FALSE POSITIVE (PREDICT UP, WAS DOWN)</div>
                  <div style={{ fontSize: '22px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-rose)' }}>
                    {metrics.confusion_matrix[0]?.[1] || 0}
                  </div>
                </div>
                <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>FALSE NEGATIVE (PREDICT DOWN, WAS UP)</div>
                  <div style={{ fontSize: '22px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-rose)' }}>
                    {metrics.confusion_matrix[1]?.[0] || 0}
                  </div>
                </div>
                <div style={{ padding: '16px', backgroundColor: 'var(--bg-surface)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>TRUE POSITIVE (PREDICT UP, WAS UP)</div>
                  <div style={{ fontSize: '22px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-emerald)' }}>
                    {metrics.confusion_matrix[1]?.[1] || 0}
                  </div>
                </div>
              </div>
            </div>

            {/* Feature Importances */}
            <div className="col-6 glass-card">
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '14px' }}>Feature Importance Hierarchy</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {Object.entries(metrics.feature_importances).map(([feat, imp]) => (
                  <div key={feat}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '2px' }}>
                      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{feat}</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>{(imp * 100).toFixed(1)}%</strong>
                    </div>
                    <div style={{ height: '6px', backgroundColor: 'var(--bg-surface)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${Math.min(100, Math.abs(imp) * 300)}%`, height: '100%', backgroundColor: 'var(--accent-cyan)' }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
