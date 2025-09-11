import {
  StockOverview,
  StockDetailResponse,
  PortfolioSummary,
  SentimentResponse,
  SentimentDistribution,
  DocumentDTO,
  RAGQueryResponse,
  DocumentCompareResponse,
  AIChatResponse,
  ResearchReportDTO,
  MLMetrics,
  MultimodalAnalyzeResponse,
  VoiceBriefingResponse,
  TechnologyCapability,
  EvaluationBenchmark,
  PriceBar
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function fetchJSON<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {})
      },
      ...options
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.warn(`API request to ${endpoint} failed, checking fallback:`, error);
    throw error;
  }
}

export const api = {
  // Stocks
  getStocks: () => fetchJSON<StockOverview[]>('/stocks/'),
  getStockDetail: (ticker: string) => fetchJSON<StockDetailResponse>(`/stocks/${ticker}`),
  getStockPrices: (ticker: string, days = 252) => fetchJSON<PriceBar[]>(`/stocks/${ticker}/prices?days=${days}`),

  // Portfolio
  getPortfolio: () => fetchJSON<PortfolioSummary>('/portfolio/'),

  // Sentiment
  analyzeSentiment: (text: string, ticker?: string) =>
    fetchJSON<SentimentResponse>('/sentiment/analyze', {
      method: 'POST',
      body: JSON.stringify({ text, ticker })
    }),
  getSentimentOverview: () => fetchJSON<SentimentDistribution>('/sentiment/overview'),

  // RAG & Documents
  queryRAG: (query: string, ticker?: string, top_k = 4) =>
    fetchJSON<RAGQueryResponse>('/rag/query', {
      method: 'POST',
      body: JSON.stringify({ query, ticker, top_k })
    }),
  getDocuments: () => fetchJSON<DocumentDTO[]>('/rag/documents'),
  compareDocuments: (doc_id_a: number, doc_id_b: number) =>
    fetchJSON<DocumentCompareResponse>('/documents/compare', {
      method: 'POST',
      body: JSON.stringify({ doc_id_a, doc_id_b })
    }),

  // AI Assistant Chat
  chat: (message: string, ticker?: string) =>
    fetchJSON<AIChatResponse>('/chat/', {
      method: 'POST',
      body: JSON.stringify({ message, ticker })
    }),

  // AI Research Agent
  runResearchAgent: (ticker: string, focus_areas?: string[]) =>
    fetchJSON<ResearchReportDTO>('/agents/research', {
      method: 'POST',
      body: JSON.stringify({ ticker, focus_areas })
    }),

  // Machine Learning
  trainMLModel: (ticker: string, model_type: string, test_size = 0.2, horizon = 5) =>
    fetchJSON<MLMetrics>('/ml/train', {
      method: 'POST',
      body: JSON.stringify({
        ticker,
        model_type,
        test_size,
        prediction_horizon_days: horizon
      })
    }),

  // Multimodal Vision
  analyzeImage: (prompt: string, image_type = 'stock_chart', image_base64?: string) =>
    fetchJSON<MultimodalAnalyzeResponse>('/multimodal/analyze', {
      method: 'POST',
      body: JSON.stringify({ prompt, image_type, image_base64 })
    }),

  // Voice AI
  getVoiceBriefing: (tickers = ['AAPL', 'MSFT', 'NVDA']) =>
    fetchJSON<VoiceBriefingResponse>('/voice/briefing', {
      method: 'POST',
      body: JSON.stringify({ tickers })
    }),

  // Technology Showcase & Benchmark
  getCapabilities: () => fetchJSON<TechnologyCapability[]>('/showcase/capabilities'),
  getEvaluationBenchmark: () => fetchJSON<EvaluationBenchmark>('/showcase/evaluation-benchmark'),
  getProviders: () => fetchJSON<any[]>('/showcase/providers')
};
