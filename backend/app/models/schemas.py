from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Market & Stock Schemas ---
class PriceBar(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class StockOverview(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    current_price: float
    change_percent: float
    market_cap: float
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: float = 1.0
    week_52_high: float
    week_52_low: float
    description: str

class TechnicalIndicators(BaseModel):
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None

class RiskStatistics(BaseModel):
    annualized_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    beta: float
    var_95_daily: float
    var_99_daily: float
    cvar_95_daily: float

class StockDetailResponse(BaseModel):
    overview: StockOverview
    prices: List[PriceBar]
    technicals: TechnicalIndicators
    risk_stats: RiskStatistics
    fundamentals: Dict[str, Any]
    is_simulated: bool = True

# --- Watchlist & Portfolio Schemas ---
class WatchlistItemDTO(BaseModel):
    ticker: str
    name: str
    price: float
    change_percent: float
    market_cap: float

class HoldingDTO(BaseModel):
    ticker: str
    name: str
    shares: float
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pl: float
    unrealized_pl_pct: float
    allocation_pct: float

class PortfolioSummary(BaseModel):
    total_value: float
    cash_balance: float
    invested_value: float
    total_unrealized_pl: float
    total_unrealized_pl_pct: float
    sharpe_ratio: float
    volatility: float
    max_drawdown: float
    sector_allocation: Dict[str, float]
    holdings: List[HoldingDTO]
    ai_risk_assessment: str

# --- Quantitative Analytics Schemas ---
class QuantRequest(BaseModel):
    tickers: List[str]
    timeframe_days: int = 252
    risk_free_rate: float = 0.04

class CorrelationMatrixResponse(BaseModel):
    tickers: List[str]
    matrix: List[List[float]]

class QuantAnalyticsResponse(BaseModel):
    tickers: List[str]
    metrics: Dict[str, RiskStatistics]
    correlation_matrix: CorrelationMatrixResponse
    cumulative_returns: Dict[str, List[Dict[str, Any]]]

# --- Sentiment Schemas ---
class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=2000)
    ticker: Optional[str] = None

class SentimentResponse(BaseModel):
    text: str
    label: str  # Positive, Neutral, Negative
    score: float
    key_phrases: List[str]
    explanation: str
    model_used: str

class BatchSentimentRequest(BaseModel):
    items: List[SentimentRequest]

class SentimentDistribution(BaseModel):
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    overall_sentiment_score: float  # -1.0 to 1.0
    timeline: List[Dict[str, Any]]

# --- RAG & Document Intelligence Schemas ---
class DocumentDTO(BaseModel):
    id: int
    ticker: Optional[str]
    title: str
    doc_type: str
    reporting_period: Optional[str]
    year: Optional[int]
    file_size_bytes: int
    created_at: datetime
    summary: Optional[str]

class Citation(BaseModel):
    document_id: int
    document_title: str
    ticker: Optional[str]
    page_number: Optional[int]
    chunk_index: int
    snippet: str
    similarity_score: float

class RAGQueryRequest(BaseModel):
    query: str
    ticker: Optional[str] = None
    top_k: int = 4

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    evidence_coverage: float
    is_demo_provider: bool = True
    disclaimer: str

class DocumentCompareRequest(BaseModel):
    doc_id_a: int
    doc_id_b: int

class MetricDiff(BaseModel):
    metric: str
    period_a: str
    value_a: str
    period_b: str
    value_b: str
    change_pct: Optional[float]
    direction: str  # increased, decreased, stable

class DocumentCompareResponse(BaseModel):
    doc_a_title: str
    doc_b_title: str
    revenue_changes: str
    margin_changes: str
    risk_factor_changes: List[str]
    management_tone_diff: str
    material_events: List[str]
    metrics_comparison: List[MetricDiff]

# --- AI Research Assistant & Chat ---
class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    citations: Optional[List[Citation]] = None
    tools_called: Optional[List[str]] = None

class AIChatRequest(BaseModel):
    message: str
    ticker: Optional[str] = None
    history: Optional[List[ChatMessage]] = None
    stream: bool = False

class AIChatResponse(BaseModel):
    response: str
    intent: str
    tools_called: List[str]
    citations: List[Citation]
    confidence_score: float
    disclaimer: str

# --- Multi-Stage Research Agent Schemas ---
class AgentTraceStep(BaseModel):
    stage: str
    description: str
    status: str  # pending, in_progress, completed, failed
    findings_summary: Optional[str] = None
    duration_ms: Optional[int] = None

class ResearchAgentRequest(BaseModel):
    ticker: str = Field(..., max_length=10)
    focus_areas: Optional[List[str]] = None  # fundamentals, technicals, risks, valuation

class ResearchReportDTO(BaseModel):
    id: int
    ticker: str
    title: str
    executive_summary: str
    full_markdown: str
    evidence_coverage: float
    ai_confidence: float
    created_at: datetime
    execution_trace: List[AgentTraceStep]
    disclaimer: str

# --- Machine Learning Schemas ---
class MLTrainRequest(BaseModel):
    ticker: str = "AAPL"
    task_type: str = "directional"  # directional, volatility, regime
    model_type: str = "random_forest"  # logistic_regression, random_forest, gradient_boosting
    test_size: float = 0.2
    prediction_horizon_days: int = 5

class MLMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    train_samples: int
    test_samples: int
    confusion_matrix: List[List[int]]
    feature_importances: Dict[str, float]
    methodology_warnings: List[str]

class MLExperimentDTO(BaseModel):
    id: int
    name: str
    ticker: str
    task_type: str
    model_type: str
    metrics: MLMetrics
    created_at: datetime

# --- Multimodal & Voice Schemas ---
class MultimodalAnalyzeRequest(BaseModel):
    prompt: str = "Analyze this financial chart and explain key trends, support/resistance, and volume."
    image_base64: Optional[str] = None
    image_type: str = "stock_chart"  # stock_chart, financial_table, earnings_slide

class MultimodalAnalyzeResponse(BaseModel):
    analysis: str
    visual_features: List[str]
    confidence: float
    model_used: str

class VoiceBriefingRequest(BaseModel):
    tickers: Optional[List[str]] = ["AAPL", "MSFT", "NVDA"]

class VoiceBriefingResponse(BaseModel):
    transcript_text: str
    audio_briefing_script: str
    key_takeaways: List[str]
    sentiment_headline: str
