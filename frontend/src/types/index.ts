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

export interface ResearchOutputDTO {
  research_id: string;
  ticker: string;
  claims: string[];
  methodology: string;
  sources: Array<{
    doc_id: number;
    title: string;
    page: number;
    filing_type: string;
    chunk_id: string;
    content_hash: string;
    score: number;
    snippet: string;
  }>;
  assumptions: string[];
  limitations: string[];
  confidence: number;
  created_at: string;
}

export interface StrategySpecificationDTO {
  strategy_id: string;
  version: string;
  hypothesis: string;
  required_inputs: string[];
  features: string[];
  entry_conditions: string[];
  exit_conditions: string[];
  risk_constraints: Record<string, any>;
  holding_period: string;
  source_references: string[];
  created_at: string;
}

export interface ImplementationOutputDTO {
  strategy_id: string;
  version: string;
  source_code: string;
  test_code: string;
  dependencies: string[];
  static_check_result: Record<string, any>;
  review_status: string;
  created_at: string;
}

export interface QACheckResultDTO {
  passed: bool;
  ast_valid: bool;
  imports_valid: bool;
  unit_tests_passed: bool;
  invariants_passed: bool;
  lookahead_passed: bool;
  leakage_passed: bool;
  details: string[];
  checked_at: string;
}

type bool = boolean;

export interface BacktestResultDTO {
  strategy_id: string;
  version: string;
  snapshot_id: string;
  train_period: string;
  val_period: string;
  test_period: string;
  equity_curve: Array<{
    date: string;
    equity: number;
    cash: number;
    position_shares: number;
    benchmark_price: number;
  }>;
  trades: Array<{
    trade_id: string;
    ticker: string;
    side: string;
    entry_time: string;
    entry_price: number;
    exit_time?: string;
    exit_price?: number;
    shares: number;
    gross_pnl?: number;
    net_pnl?: number;
    return_pct?: number;
    total_costs?: number;
  }>;
  metrics: {
    initial_capital: number;
    ending_equity: number;
    total_return: number;
    annualized_return: number;
    annualized_volatility: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    max_drawdown: number;
    total_trades: number;
    hit_rate: number;
    turnover: number;
    total_transaction_costs: number;
    total_slippage_incurred: number;
    total_exchange_fees: number;
    alpha: number;
    beta: number;
    information_ratio: number;
  };
  suspicious_flags: string[];
}

export interface ApprovalRecordDTO {
  approval_id: string;
  workflow_id: string;
  artifact_hash: string;
  requested_by: string;
  reviewed_by?: string;
  decision: string;
  reason?: string;
  created_at: string;
  reviewed_at?: string;
}

export interface ShadowSimulationResultDTO {
  simulation_id: string;
  strategy_id: string;
  status: string;
  virtual_portfolio: {
    cash: number;
    shares: number;
    position_value: number;
    total_equity: number;
    initial_cash: number;
  };
  hypothetical_orders: Array<{
    order_id: string;
    ticker: string;
    side: string;
    shares: number;
    order_type: string;
    status: string;
    timestamp: string;
  }>;
  simulated_fills: Array<{
    fill_id: string;
    order_id: string;
    price: number;
    shares: number;
    costs: number;
    slippage: number;
    timestamp: string;
  }>;
  slippage_incurred: number;
  simulated_pnl: number;
  current_exposure: number;
  is_simulation_only: bool;
  disclaimer: string;
}

export interface RecommendationOutputDTO {
  ticker: string;
  action: 'BUY' | 'SELL' | 'HOLD' | 'NO_ACTION' | 'INSUFFICIENT_EVIDENCE';
  confidence: number;
  strategy_id: string;
  strategy_version: string;
  time_horizon: string;
  supporting_evidence: string[];
  risk_flags: string[];
  backtest_summary: Record<string, any>;
  shadow_summary: Record<string, any>;
  timestamp: string;
  disclaimer: string;
}

export interface WorkflowStateDTO {
  workflow_id: string;
  run_id: string;
  ticker: string;
  status: string;
  stage: string;
  research_output?: ResearchOutputDTO;
  strategy_spec?: StrategySpecificationDTO;
  candidate_code?: ImplementationOutputDTO;
  qa_results?: QACheckResultDTO;
  backtest_result?: BacktestResultDTO;
  approval_record?: ApprovalRecordDTO;
  shadow_result?: ShadowSimulationResultDTO;
  recommendation?: RecommendationOutputDTO;
  history: Array<{
    timestamp: string;
    node: string;
    status: string;
    details: Record<string, any>;
  }>;
  retry_count: number;
  error_message?: string;
}
