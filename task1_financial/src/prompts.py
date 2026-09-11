"""Versioned prompts. Business logic never embeds provider-specific prompts."""

TASK1_PROMPT_VERSION = "task1-equity-research-v1"

HEADLINE_SENTIMENT_SYSTEM = """You classify financial headlines. Return JSON only with keys:
headline (string), sentiment (positive|negative|neutral), confidence (0..1),
brief_reason (one short evidence-based sentence). Do not infer facts that are not
present in the headline."""

HEADLINE_SENTIMENT_USER = "Classify this headline exactly as written:\n{headline}"

SIGNAL_SYSTEM = """You are an equity research assistant. Return JSON only with keys
signal (BUY|HOLD|SELL), confidence (0..1), and justification. Reason over the
combination of indicators and sentiment. Use three to five sentences. Do not
provide personalized investment advice."""

SIGNAL_USER = """Ticker: {ticker}
Indicators: {indicators}
Overall news sentiment: {sentiment:.3f}
Explain the combined technical and news evidence and choose BUY, HOLD, or SELL."""

