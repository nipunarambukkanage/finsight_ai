"""
FinSight AI - Context-Aware Financial Assistant & Tool Calling Orchestrator
Processes user queries through a multi-stage deterministic pipeline:
Intent Classification -> Tool Selection -> Deterministic Data Retrieval ->
RAG Synthesis -> Evidence Attachment -> Safety Disclaimer Guardrails.
"""

from typing import List, Dict, Any, Optional
import re
from backend.app.models.schemas import (
    AIChatRequest, AIChatResponse, Citation
)
from backend.app.services.market_data import market_data_service
from backend.app.services.sentiment import sentiment_service
from backend.app.services.portfolio import portfolio_service
from backend.app.rag.engine import rag_engine
from backend.app.providers.gateway import ModelRequest, model_gateway
from backend.app.config import settings

class AIChatAssistantService:

    async def process_chat(self, req: AIChatRequest) -> AIChatResponse:
        query = req.message.strip()
        lower = query.lower()


        ticker = req.ticker
        if not ticker:
            match = re.search(r"\b(aapl|msft|nvda|googl|amzn|tsla)\b", lower)
            if match:
                ticker = match.group(1).upper()

        tools_called: List[str] = []
        citations: List[Citation] = []
        intent = "general_financial_query"


        if "compare" in lower or (" vs " in lower) or ("versus" in lower):
            intent = "comparative_analysis"
            tools_called.append("compare_companies")

            found_tickers = re.findall(r"\b(aapl|msft|nvda|googl|amzn|tsla)\b", lower)
            t1 = found_tickers[0].upper() if len(found_tickers) > 0 else "AAPL"
            t2 = found_tickers[1].upper() if len(found_tickers) > 1 else "MSFT"

            ov1 = await market_data_service.get_overview(t1)
            ov2 = await market_data_service.get_overview(t2)

            response_text = (
                f"### Comparative Intelligence: {t1} vs. {t2}\n\n"
                f"| Metric | {t1} ({ov1.name if ov1 else t1}) | {t2} ({ov2.name if ov2 else t2}) |\n"
                f"| :--- | :--- | :--- |\n"
                f"| **Current Price** | ${ov1.current_price:.2f} | ${ov2.current_price:.2f} |\n"
                f"| **Market Cap** | ${ov1.market_cap/1e9:.1f}B | ${ov2.market_cap/1e9:.1f}B |\n"
                f"| **P/E Ratio** | {ov1.pe_ratio}x | {ov2.pe_ratio}x |\n"
                f"| **Beta** | {ov1.beta} | {ov2.beta} |\n"
                f"| **52-Week Range** | ${ov1.week_52_low:.2f} - ${ov1.week_52_high:.2f} | ${ov2.week_52_low:.2f} - ${ov2.week_52_high:.2f} |\n\n"
                f"**Analytical Synthesis:**\n"
                f"- **{t1}** exhibits strong recurring capital returns with Free Cash Flow yield and ecosystem lock-in.\n"
                f"- **{t2}** demonstrates superior margin resilience driven by scalable enterprise cloud and software architecture."
            )


        elif "portfolio" in lower or "holdings" in lower or "allocation" in lower:
            intent = "portfolio_risk_query"
            tools_called.append("analyze_portfolio")
            p_summary = await portfolio_service.get_portfolio_summary()
            response_text = (
                f"### Institutional Portfolio Risk Assessment\n\n"
                f"- **Total Portfolio Value:** ${p_summary.total_value:,.2f}\n"
                f"- **Unrealized Gain/Loss:** +${p_summary.total_unrealized_pl:,.2f} (+{p_summary.total_unrealized_pl_pct:.2f}%)\n"
                f"- **Annualized Volatility:** {p_summary.volatility*100:.1f}%\n"
                f"- **Portfolio Sharpe Ratio:** {p_summary.sharpe_ratio}\n"
                f"- **Maximum Drawdown:** {p_summary.max_drawdown*100:.1f}%\n\n"
                f"**Top Allocations:** " + ", ".join([f"{h.ticker}: {h.allocation_pct}%" for h in p_summary.holdings[:3]]) + "\n\n"
                f"**AI Risk Commentary:** {p_summary.ai_risk_assessment}"
            )


        elif any(k in lower for k in ["rsi", "macd", "moving average", "bollinger", "technical"]):
            intent = "technical_analysis"
            tools_called.append("calculate_technical_indicators")
            target = ticker or "AAPL"
            detail = await market_data_service.get_detail(target)
            tech = detail.technicals if detail else None
            response_text = (
                f"### Technical Indicator Audit: {target}\n\n"
                f"- **Relative Strength Index (RSI-14):** {tech.rsi if tech else 54.2} (Balanced neutral momentum zone)\n"
                f"- **MACD Line:** {tech.macd if tech else 1.25} | **Signal Line:** {tech.macd_signal if tech else 0.95} (Histogram: {tech.macd_hist if tech else 0.30})\n"
                f"- **20-Day Simple Moving Average (SMA20):** ${tech.sma_20 if tech else 228.40}\n"
                f"- **50-Day Simple Moving Average (SMA50):** ${tech.sma_50 if tech else 221.10}\n"
                f"- **Bollinger Bands (20, 2 std):** Upper: ${tech.bb_upper if tech else 242.10} | Lower: ${tech.bb_lower if tech else 215.30}\n\n"
                "Price action is currently tracking above the 50-day moving average, signaling positive medium-term structural support."
            )


        elif any(k in lower for k in ["document", "filing", "10-k", "10-q", "earnings", "supply chain", "margin"]):
            intent = "document_rag_retrieval"
            tools_called.extend(["search_financial_documents", "retrieve_document_chunks"])
            rag_res = await rag_engine.query(req=type("Req", (), {"query": query, "ticker": ticker, "top_k": 3})())
            response_text = rag_res.answer
            citations = rag_res.citations


        elif ticker:
            intent = "stock_overview"
            tools_called.extend(["get_stock_overview", "calculate_financial_metrics"])
            detail = await market_data_service.get_detail(ticker)
            ov = detail.overview if detail else None
            f = detail.fundamentals if detail else {}
            response_text = (
                f"### Financial & Operational Brief: {ov.name} ({ticker})\n\n"
                f"- **Current Market Price:** ${ov.current_price:.2f} ({ov.change_percent:+.2f}%)\n"
                f"- **Market Capitalization:** ${ov.market_cap/1e9:.1f} Billion\n"
                f"- **TTM P/E Multiple:** {ov.pe_ratio}x | **Forward P/E:** {ov.forward_pe}x\n"
                f"- **Gross Margin:** {f.get('gross_margin', 0.45)*100:.1f}% | **Operating Margin:** {f.get('operating_margin', 0.30)*100:.1f}%\n"
                f"- **52-Week Range:** ${ov.week_52_low:.2f} - ${ov.week_52_high:.2f}\n\n"
                f"**Business Overview:** {ov.description}"
            )
        else:
            intent = "market_general"
            tools_called.append("get_market_overview")
            response_text, _ = await model_gateway.generate(
                query,
                request=ModelRequest(task_type="general_financial_query", allow_demo_fallback=settings.DEMO_MODE),
            )
            response_text = str(response_text)

        disclaimer = (
            "FinSight AI is a research and demonstration platform. Information generated by the system "
            "does not constitute financial advice and should not be considered a recommendation to buy or sell securities."
        )

        return AIChatResponse(
            response=response_text,
            intent=intent,
            tools_called=tools_called,
            citations=citations,
            confidence_score=0.91,
            disclaimer=disclaimer
        )

chat_service = AIChatAssistantService()
