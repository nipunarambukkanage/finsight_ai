"""One-page Markdown/HTML report rendering for the assessment bonus."""

from __future__ import annotations

from pathlib import Path
import base64
from io import BytesIO

from .contracts import EquityResearchResult


def render_markdown(result: EquityResearchResult) -> str:
    snap = result.snapshot
    ytd = f"{snap.ytd_return:.2%}" if snap.ytd_return is not None else "N/A"
    top = result.headline_sentiments[:3]
    headlines = "\n".join(f"- {item.headline} ({item.sentiment.value}, {item.confidence:.0%})" for item in top) or "- No validated headlines available."
    reasoning = result.reasoning
    explanation = reasoning.justification if reasoning else "Insufficient validated model evidence for a signal."
    signal = reasoning.signal.value if reasoning else "INSUFFICIENT_EVIDENCE"
    return f"""# Equity Research Brief - {snap.ticker}

## Company snapshot

Price: {snap.current_price if snap.current_price is not None else 'N/A'} | 52-week range: {snap.week_52_low if snap.week_52_low is not None else 'N/A'} - {snap.week_52_high if snap.week_52_high is not None else 'N/A'} | P/E: {snap.pe_ratio if snap.pe_ratio is not None else 'N/A'} | YTD: {ytd}

## Technical outlook

Momentum regime: **{snap.momentum_signal}**. RSI-14: `{snap.indicators.get('rsi_14')}`; MACD: `{snap.indicators.get('macd')}`; SMA-50/SMA-200: `{snap.indicators.get('sma_50')}` / `{snap.indicators.get('sma_200')}`.

## News sentiment

Aggregate validated sentiment: **{result.overall_sentiment_score:.2f}** ({len(result.headline_sentiments)} valid, {result.invalid_headlines} invalid).

{headlines}

## Model recommendation

**{signal}** - {explanation}

## Data limitations and risk disclaimer

{'; '.join(snap.limitations) or 'No pipeline limitations were recorded.'}

## Provenance

Provider: `{snap.provenance.provider}` | Mode: `{snap.provenance.data_mode}` | Retrieved: `{snap.provenance.retrieved_at.isoformat()}`
Observation range: `{snap.provenance.start_date or 'N/A'}` to `{snap.provenance.end_date or 'N/A'}` | Adjustment policy: `{snap.provenance.price_adjustment_policy}` | Analytical field: `{snap.provenance.analytical_price_field}`
Dataset SHA-256: `{snap.provenance.dataset_sha256 or 'N/A'}` | Corporate-action SHA-256: `{snap.provenance.corporate_actions_sha256 or 'N/A'}`

FinSight AI is decision-support software, not personalized investment advice. Historical or simulated results do not predict future returns. Verify all information before making decisions.
"""


def write_html(result: EquityResearchResult, output: str | Path) -> Path:
    path = Path(output)
    markdown = render_markdown(result)
    escaped = markdown.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    chart = ""
    try:
        import matplotlib.pyplot as plt
        labels, values = [], []
        for label in ("RSI-14", "MACD", "SMA-50", "SMA-200"):
            key = {"RSI-14": "rsi_14", "MACD": "macd", "SMA-50": "sma_50", "SMA-200": "sma_200"}[label]
            value = result.snapshot.indicators.get(key)
            if value is not None:
                labels.append(label); values.append(value)
        if values:
            figure, axis = plt.subplots(figsize=(6.5, 2.2))
            axis.bar(labels, values, color="#2364aa")
            axis.set_title(f"{result.snapshot.ticker} indicator snapshot")
            figure.tight_layout()
            buffer = BytesIO(); figure.savefig(buffer, format="png", dpi=150); plt.close(figure)
            chart = f"<img alt='Indicator chart' style='max-width:100%' src='data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}'/>"
    except Exception:
        chart = "<p>Chart unavailable in this runtime; install matplotlib to render it.</p>"
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>body{{font:15px system-ui;max-width:850px;margin:40px auto;color:#172033}}pre{{white-space:pre-wrap}}</style></head><body>{chart}<pre>{escaped}</pre></body></html>", encoding="utf-8")
    return path
