from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


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


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=2000)
    ticker: Optional[str] = None

class SentimentResponse(BaseModel):
    text: str
    label: str
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
    overall_sentiment_score: float
    timeline: List[Dict[str, Any]]


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
    ticker: Optional[str] = None
    page_number: Optional[int] = None
    chunk_index: int
    snippet: str
    similarity_score: float
    filing_type: str = "10-K"
    publication_date: str = "2024-11-01"
    source_url: str = "https://www.sec.gov/edgar"
    section_or_page: str = "Item 7 - MD&A"
    chunk_id: str = "chunk-1"
    content_hash: str = ""
    retrieval_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    direction: str

class DocumentCompareResponse(BaseModel):
    doc_a_title: str
    doc_b_title: str
    revenue_changes: str
    margin_changes: str
    risk_factor_changes: List[str]
    management_tone_diff: str
    material_events: List[str]
    metrics_comparison: List[MetricDiff]


class ChatMessage(BaseModel):
    role: str
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


class AgentTraceStep(BaseModel):
    stage: str
    description: str
    status: str
    findings_summary: Optional[str] = None
    duration_ms: Optional[int] = None

class ResearchAgentRequest(BaseModel):
    ticker: str = Field(..., max_length=10)
    focus_areas: Optional[List[str]] = None

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


class MLTrainRequest(BaseModel):
    ticker: str = "AAPL"
    task_type: str = "directional"
    model_type: str = "random_forest"
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


class MultimodalAnalyzeRequest(BaseModel):
    prompt: str = "Analyze this financial chart and explain key trends, support/resistance, and volume."
    image_base64: Optional[str] = None
    image_type: str = "stock_chart"

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
