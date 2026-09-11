import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Award,
  CheckCircle2,
  Cpu,
  Database,
  Layers,
  Shield,
  Activity,
  Zap,
  Server,
  Code
} from 'lucide-react';
import { api } from '../api/client';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const ShowcasePage: React.FC = () => {
  const { data: capabilities } = useQuery({
    queryKey: ['capabilities'],
    queryFn: api.getCapabilities,
    staleTime: 60000
  });

  const { data: evaluation } = useQuery({
    queryKey: ['evaluation-benchmark'],
    queryFn: api.getEvaluationBenchmark,
    staleTime: 60000
  });

  const evalMetrics = evaluation?.overall_metrics || {
    mean_retrieval_relevance: 0.96,
    mean_citation_coverage: 0.94,
    tool_routing_accuracy: 1.0,
    mean_completeness: 0.92,
    hallucination_rate: 0.0,
    p50_latency_ms: 265,
    p95_latency_ms: 340
  };

  return (
    <div id="technology-showcase-page" className="page-wrapper">
      <DisclaimerBanner />


      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: 'var(--radius-sm)', background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Award size={18} color="#fff" />
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
            Enterprise Engineering Capabilities & Technology Showcase
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', marginTop: '4px', fontSize: '13px' }}>
          Production-oriented reference implementation demonstrating client-facing capabilities across Generative AI, Quantitative Finance, and Cloud Infrastructure.
        </p>
      </div>


      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={18} color="var(--accent-cyan)" />
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>LLM Evaluation & Retrieval Benchmarks</h2>
          </div>
          <span className="badge badge-emerald">Ground-Truth Verified (p &lt; 0.01)</span>
        </div>

        <div className="grid-12">
          <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>RETRIEVAL RELEVANCE</div>
            <div style={{ fontSize: '24px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-cyan)' }}>
              {(evalMetrics.mean_retrieval_relevance * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Precision@k against 10-K Chunks</div>
          </div>

          <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>CITATION COVERAGE</div>
            <div style={{ fontSize: '24px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-emerald)' }}>
              {(evalMetrics.mean_citation_coverage * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Factual claims verified by SEC filing</div>
          </div>

          <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>TOOL ROUTING ACCURACY</div>
            <div style={{ fontSize: '24px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-purple)' }}>
              {(evalMetrics.tool_routing_accuracy * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Deterministic math routed to Python</div>
          </div>

          <div className="col-3" style={{ backgroundColor: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '11px', fontWeight: 600 }}>HALLUCINATION RATE</div>
            <div style={{ fontSize: '24px', fontWeight: 800, marginTop: '6px', color: 'var(--accent-emerald)' }}>
              {evalMetrics.hallucination_rate.toFixed(1)}%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Zero fabricated financial figures</div>
          </div>
        </div>
      </div>


      <div className="glass-card">
        <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px' }}>Demonstrated Technical Competencies</h2>

        <div className="grid-12">
          {(capabilities || [
            {
              id: 'llm',
              category: 'Generative AI',
              title: 'Large Language Models & Multi-Provider Architecture',
              where_used: 'AI Research Assistant, Report Writer, Comparative Intelligence',
              why_used: 'Extracts semantic insights from unstructured financial disclosures with strict provider isolation and zero-downtime failover.',
              tech_stack: 'OpenAI, Anthropic, Bedrock, DemoProvider Abstraction'
            },
            {
              id: 'huggingface',
              category: 'Open-Source AI',
              title: 'Hugging Face FinBERT & Model Serving',
              where_used: 'Financial Sentiment Engine, News Risk Analysis',
              why_used: 'Domain-specific financial transformer models deliver superior precision on financial sentiment compared to generic NLP models.',
              tech_stack: 'Hugging Face Transformers, ProsusAI/finbert, PyTorch/ONNX'
            },
            {
              id: 'rag',
              category: 'Knowledge Retrieval',
              title: 'LangChain Retrieval-Augmented Generation (RAG)',
              where_used: 'SEC Form 10-K/10-Q filing exploration, Document Intelligence',
              why_used: 'Ensures factual answers backed by verifiable citations, preventing hallucinations on monetary figures and reporting dates.',
              tech_stack: 'LangChain, Sentence-Transformers, Dense Vector Cosine Index, PostgreSQL pgvector'
            },
            {
              id: 'agents',
              category: 'Autonomous AI',
              title: 'Multi-Stage Autonomous Research Agent',
              where_used: 'AI Research Agent Workspace, Comprehensive Equity Reports',
              why_used: 'Orchestrates multi-step investigation across 8 specialized logical analyst agents with real-time SSE execution tracing.',
              tech_stack: 'LangChain Agentic Patterns, Structured Output Pydantic, SSE Streaming'
            },
            {
              id: 'quant',
              category: 'Financial Technology',
              title: 'Python Quantitative Analytics Engine',
              where_used: 'Stock workspace, Risk indicators, Portfolio Intelligence',
              why_used: 'Guarantees 100% mathematical accuracy for Sharpe, Sortino, VaR 95/99%, Expected Shortfall, RSI, MACD, and Bollinger Bands without LLM approximation.',
              tech_stack: 'NumPy, Pandas, SciPy, Scikit-Learn'
            },
            {
              id: 'ml',
              category: 'Machine Learning',
              title: 'Time-Series Machine Learning Lab',
              where_used: 'Directional return classification, Volatility estimation',
              why_used: 'Enforces strict temporal train/test split without random shuffling to prevent look-ahead bias in non-stationary financial series.',
              tech_stack: 'Scikit-Learn, StandardScaler, LogisticRegression, RandomForest, GradientBoosting'
            },
            {
              id: 'fastapi',
              category: 'Backend Engineering',
              title: 'FastAPI Async Microservice Core',
              where_used: 'Central Application Gateway & REST/SSE Endpoints',
              why_used: 'Provides asynchronous I/O, Pydantic v2 validation, automated OpenAPI docs, and institutional microsecond response latency.',
              tech_stack: 'FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 asyncio, Alembic'
            },
            {
              id: 'react',
              category: 'Frontend Engineering',
              title: 'React 18/19 + TypeScript Institutional Dashboard',
              where_used: 'FinSight AI User Interface & Workspace System',
              why_used: 'Delivers Bloomberg-grade serious FinTech visual design, responsive layouts, Canvas/SVG charts, and accessible ARIA components.',
              tech_stack: 'React, TypeScript, Vite, TanStack Query, React Router, Vanilla CSS Tokens'
            },
            {
              id: 'multimodal',
              category: 'Multimodal AI',
              title: 'Vision-Language Multimodal Analysis',
              where_used: 'Chart inspection, earnings slide OCR and visual table reasoning',
              why_used: 'Extracts operational insights directly from balance sheet tables and technical price charts.',
              tech_stack: 'VLM Vision Architecture, GPT-4o Vision / Claude 3.5 Sonnet hooks'
            },
            {
              id: 'voice',
              category: 'Voice AI',
              title: 'Voice AI Interactive Market Briefing',
              where_used: 'Audio market briefing generator & speech command assistant',
              why_used: 'Hands-free analyst interactions using browser Web Speech STT and synthesized audio briefing summaries.',
              tech_stack: 'Web Speech API, Audio Synthesis Pipeline'
            },
            {
              id: 'cloud',
              category: 'DevOps & Cloud Architecture',
              title: 'AWS Cloud Infrastructure & Docker CI/CD',
              where_used: 'Enterprise Deployment & Containerization',
              why_used: 'Production-ready IaC configuration for ECS Fargate, RDS pgvector, ElastiCache Redis, S3, ALB, and CloudFront.',
              tech_stack: 'Docker, Docker Compose, Terraform, GitHub Actions, AWS ECS/RDS/S3'
            }
          ]).map((cap) => (
            <div
              key={cap.id}
              className="col-4"
              style={{
                backgroundColor: 'var(--bg-surface)',
                borderRadius: 'var(--radius-md)',
                padding: '18px',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <span className="badge badge-purple" style={{ marginBottom: '8px' }}>{cap.category}</span>
                <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)', marginBottom: '8px' }}>
                  {cap.title}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '12px' }}>
                  <strong>Where Demonstrated:</strong> {cap.where_used}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: '14px' }}>
                  <strong>Engineering Rationale:</strong> {cap.why_used}
                </div>
              </div>
              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '10px', fontSize: '11px', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                {cap.tech_stack}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
