export interface PriceBar {
  date: str;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

type str = string;

export interface StockOverview {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  current_price: number;
  change_percent: number;
  market_cap: number;
  pe_ratio?: number;
  forward_pe?: number;
  dividend_yield?: number;
  beta: number;
  week_52_high: number;
  week_52_low: number;
  description: string;
}

export interface TechnicalIndicators {
  rsi?: number;
  macd?: number;
  macd_signal?: number;
  macd_hist?: number;
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  bb_upper?: number;
  bb_middle?: number;
  bb_lower?: number;
}

export interface RiskStatistics {
  annualized_volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  beta: number;
  var_95_daily: number;
  var_99_daily: number;
  cvar_95_daily: number;
}

export interface StockDetailResponse {
  overview: StockOverview;
  prices: PriceBar[];
  technicals: TechnicalIndicators;
  risk_stats: RiskStatistics;
  fundamentals: Record<string, any>;
  is_simulated: boolean;
}

export interface HoldingDTO {
  ticker: string;
  name: string;
  shares: number;
  average_cost: number;
  current_price: number;
  market_value: number;
  unrealized_pl: number;
  unrealized_pl_pct: number;
  allocation_pct: number;
}

export interface PortfolioSummary {
  total_value: number;
  cash_balance: number;
  invested_value: number;
  total_unrealized_pl: number;
  total_unrealized_pl_pct: number;
  sharpe_ratio: number;
  volatility: number;
  max_drawdown: number;
  sector_allocation: Record<string, number>;
  holdings: HoldingDTO[];
  ai_risk_assessment: string;
}

export interface SentimentResponse {
  text: string;
  label: 'Positive' | 'Neutral' | 'Negative';
  score: number;
  key_phrases: string[];
  explanation: string;
  model_used: string;
}

export interface SentimentDistribution {
  positive_pct: number;
  neutral_pct: number;
  negative_pct: number;
  overall_sentiment_score: number;
  timeline: Array<{ date: string; score: number }>;
}

export interface DocumentDTO {
  id: number;
  ticker?: string;
  title: string;
  doc_type: string;
  reporting_period?: string;
  year?: number;
  file_size_bytes: number;
  created_at: string;
  summary?: string;
}

export interface Citation {
  document_id: number;
  document_title: string;
  ticker?: string;
  page_number?: number;
  chunk_index: number;
  snippet: string;
  similarity_score: number;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  citations: Citation[];
  evidence_coverage: number;
  is_demo_provider: boolean;
  disclaimer: string;
}

export interface MetricDiff {
  metric: string;
  period_a: string;
  value_a: string;
  period_b: string;
  value_b: string;
  change_pct?: number;
  direction: string;
}

export interface DocumentCompareResponse {
  doc_a_title: string;
  doc_b_title: string;
  revenue_changes: string;
  margin_changes: string;
  risk_factor_changes: string[];
  management_tone_diff: string;
  material_events: string[];
  metrics_comparison: MetricDiff[];
}

export interface AIChatResponse {
  response: string;
  intent: string;
  tools_called: string[];
  citations: Citation[];
  confidence_score: number;
  disclaimer: string;
}

export interface AgentTraceStep {
  stage: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  findings_summary?: string;
  duration_ms?: number;
}

export interface ResearchReportDTO {
  id: number;
  ticker: string;
  title: string;
  executive_summary: string;
  full_markdown: string;
  evidence_coverage: number;
  ai_confidence: number;
  created_at: string;
  execution_trace: AgentTraceStep[];
  disclaimer: string;
}

export interface MLMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  train_samples: number;
  test_samples: number;
  confusion_matrix: number[][];
  feature_importances: Record<string, number>;
  methodology_warnings: string[];
}

export interface MultimodalAnalyzeResponse {
  analysis: string;
  visual_features: string[];
  confidence: number;
  model_used: string;
}

export interface VoiceBriefingResponse {
  transcript_text: string;
  audio_briefing_script: string;
  key_takeaways: string[];
  sentiment_headline: string;
}

export interface TechnologyCapability {
  id: string;
  category: string;
  title: string;
  where_used: string;
  why_used: string;
  tech_stack: string;
}

export interface EvaluationBenchmark {
  timestamp: string;
  total_test_cases: number;
  overall_metrics: {
    mean_retrieval_relevance: number;
    mean_citation_coverage: number;
    tool_routing_accuracy: number;
    mean_completeness: number;
    hallucination_rate: number;
    p50_latency_ms: number;
    p95_latency_ms: number;
  };
  detailed_results: Array<{
    case_id: string;
    query: string;
    retrieval_relevance: number;
    citation_coverage: number;
    tool_call_accuracy: number;
    answer_completeness: number;
    latency_ms: number;
    hallucination_detected: boolean;
    ground_truth_verified: boolean;
  }>;
}
