# FinSight AI - Agentic System Specifications

## 1. Agent Philosophy & Architecture
The agent system in FinSight AI is designed as a **Multi-Stage Autonomous Research Agent** rather than an uncontrolled conversational loop. It reflects institutional Wall Street equity research workflows where distinct analytical disciplines (market data, fundamentals, technicals, risk, and SEC filing audits) are conducted systematically before report synthesis.

```mermaid
graph TD
    Query[User Research Query] --> Planner[1. Research Planner]
    Planner --> MktData[2. Market Data Analyst]
    MktData --> Fund[3. Fundamental Analyst]
    Fund --> Tech[4. Technical Analyst]
    Tech --> Risk[5. Risk & Sentiment Analyst]
    Risk --> DocRes[6. Document Researcher (RAG)]
    DocRes --> Writer[7. Report Writer]
    Writer --> Verifier[8. Verification Agent]
    Verifier --> Report[14-Section Institutional Equity Brief]
```

---

## 2. Specialized Logical Agents

| Stage | Agent Name | Input Data | Analytical Responsibility | Output Format |
| :--- | :--- | :--- | :--- | :--- |
| **01** | `Research Planner` | Ticker, Focus Areas | Formulates analytical angle, key catalysts, and risk factors to investigate | Structured Research Scope |
| **02** | `Market Data Analyst` | Historical OHLCV Series | Evaluates 52-week trading ranges, liquidity, volume, and daily return distributions | Price Parameters |
| **03** | `Fundamental Analyst` | Financial Statements | Audits Gross & Operating Margins, Free Cash Flow conversion, ROE, and Debt leverage | Fundamental KPI Matrix |
| **04** | `Technical Analyst` | Price Series | Calculates Wilder RSI-14, MACD convergence/divergence, and Bollinger Bands | Technical Momentum Summary |
| **05** | `Risk & Sentiment Analyst` | Returns & News Text | Computes Beta vs S&P 500, Max Drawdown, VaR 95%, and FinBERT sentiment | Quantitative Risk Audit |
| **06** | `Document Researcher` | SEC 10-K / 10-Q Chunks | Executes vector semantic search to retrieve corporate management disclosures | Verified Source Citations |
| **07** | `Report Writer` | All Stage Outputs | Synthesizes comprehensive 14-section institutional analyst report with scenarios | Structured Markdown |
| **08** | `Verification Agent` | Generated Report & Chunks | Audits calculation lineage, verifies citations, and calculates confidence score | Verified Report DTO |

---

## 3. Tool Calling Allowlist
The agents interact strictly with typed, deterministic Python tools:
1. `get_stock_overview(ticker: str)`
2. `get_historical_prices(ticker: str, days: int)`
3. `calculate_financial_metrics(ticker: str)`
4. `calculate_technical_indicators(ticker: str)`
5. `search_financial_documents(query: str, ticker: str)`
6. `retrieve_document_chunks(doc_id: int)`
7. `analyze_sentiment(text: str)`
8. `compare_companies(ticker_a: str, ticker_b: str)`
9. `analyze_portfolio()`

---

## 4. Boundedness & Operational Safety
- **Maximum Execution Duration:** 15,000ms per complete agent run.
- **Trace Streaming:** Progress is streamed in real time via Server-Sent Events (`/api/v1/agents/research/stream/{ticker}`).
- **No Hallucination Fallback:** If filing evidence is missing, the agent explicitly documents data limitations in Section 10 of the report.
