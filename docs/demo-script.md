# FinSight AI: Executive & Client Demonstration Script

## Demonstration Overview
- **Duration**: 12 – 15 minutes
- **Target Audience**: Institutional Investors, Chief Technology Officers, Heads of Equity Research, Quant Leads
- **Objective**: Showcase how FinSight AI combines generative AI, multi-stage autonomous agents, institutional quantitative analytics, and zero-hallucination RAG into a Bloomberg-grade decision engine.

---

### Scene 1: Executive Overview & Platform Dashboard (00:00 – 02:00)
**Click Path**: Open `http://localhost:5173/` $\rightarrow$ Institutional Market Overview

- **Presenter Talking Point**:
  > "Welcome to FinSight AI. Modern equity research is overwhelmed by volume—thousands of pages of SEC filings, earnings call audio, and volatile macroeconomic data. FinSight AI brings Wall Street-grade quantitative rigor and generative AI intelligence into a single unified terminal."
- **Actions to Perform**:
  1. Highlight the institutional dark theme, glassmorphism cards, and live telemetry pill in the header.
  2. Point to the top **Regulatory Disclaimer Banner**: *"Notice that compliance and responsible AI are engineered directly into the core—no ungrounded trade execution or black-box predictions."*
  3. Review the Ticker Bar (AAPL, MSFT, NVDA, GOOGL, AMZN, TSLA) and Market Status indicator.

---

### Scene 2: Deep-Dive Stock Workspace & Canvas Charting (02:00 – 04:30)
**Click Path**: Click **"Stock Workspace"** in sidebar $\rightarrow$ Select `NVDA`

- **Presenter Talking Point**:
  > "Let's examine NVIDIA. Notice the high-performance HTML5 Canvas chart. We built our own custom canvas rendering engine to deliver sub-millisecond responsive crosshairs, volume distributions, and technical overlay calculations without heavy third-party bundle bloat."
- **Actions to Perform**:
  1. Toggle Technical Overlays: SMA 20, SMA 50, Bollinger Bands, and RSI (14).
  2. Hover over candlestick bars to demonstrate real-time crosshair inspection (Open, High, Low, Close, Volume).
  3. Review the Key Financial Metrics panel: P/E, EV/EBITDA, Free Cash Flow Yield, and 52-week trading bounds.

---

### Scene 3: SEC Filing RAG & Verifiable Citations (04:30 – 07:00)
**Click Path**: Click **"AI Assistant"** in sidebar $\rightarrow$ Type or click sample prompt: *"What are Apple's primary supply chain and antitrust risk factors in their 2024 10-K?"*

- **Presenter Talking Point**:
  > "The biggest barrier to LLM adoption in finance is hallucination. If an analyst presents an ungrounded figure to an investment committee, it can result in multi-million dollar losses. Watch how FinSight AI grounds every single assertion."
- **Actions to Perform**:
  1. Submit the prompt and observe the streaming response.
  2. Point to the in-line interactive citation pill: `[Doc: Apple Inc. Fiscal 2024 Form 10-K, Page 42]`.
  3. Click the citation pill to reveal the **Citation Drawer** showing the exact source filing excerpt, filing date, and cosine similarity confidence score.

---

### Scene 4: FinBERT Sentiment & Filing Diff Analysis (07:00 – 09:00)
**Click Path**: Click **"Sentiment Engine"** $\rightarrow$ Navigate to **"Filing Comparison"** tab

- **Presenter Talking Point**:
  > "Standard NLP models fail on financial language because words like 'liability' or 'cost reduction' have nuanced corporate meanings. Here, we run Hugging Face FinBERT, specifically fine-tuned on financial corpora."
- **Actions to Perform**:
  1. Inspect the 7-day and 30-day sentiment score breakdown for `MSFT` and `AAPL`.
  2. In the Filing Comparison tool, select **Apple 2023 10-K** vs. **Apple 2024 10-K**.
  3. Highlight the highlighted diff showing newly inserted risk language regarding regulatory antitrust scrutiny in Europe and AI data center energy commitments.

---

### Scene 5: Autonomous Multi-Stage Research Agent (09:00 – 11:30)
**Click Path**: Click **"Research Agent"** $\rightarrow$ Enter `AAPL` $\rightarrow$ Click **"Run Full Autonomous Research Run"**

- **Presenter Talking Point**:
  > "Rather than a simple one-shot prompt, our Autonomous Research Agent executes an 8-stage pipeline mirroring a Wall Street research associate's complete analytical workflow."
- **Actions to Perform**:
  1. Watch the live 8-stage stepper animate through Market Data, Fundamentals, FinBERT Sentiment, Filing RAG, Technicals, Risk Analytics, Time-Series ML, and Synthesis.
  2. Inspect the live streaming log terminal displaying millisecond-by-millisecond execution telemetry.
  3. View the generated 14-section institutional report.
  4. Demonstrate the **"Export Markdown"** and **"Export JSON"** buttons.

---

### Scene 6: Quantitative Risk & Responsible ML Labs (11:30 – 13:30)
**Click Path**: Click **"Analytics Lab"** $\rightarrow$ Switch to **"ML Lab"**

- **Presenter Talking Point**:
  > "Many finance applications show fake 95% directional prediction accuracy by secretly leaking future data into training. At FinSight AI, we enforce strict non-anticipative temporal splitting—no random shuffling, no look-ahead bias."
- **Actions to Perform**:
  1. In Analytics Lab, inspect the interactive Portfolio Correlation Heatmap, 95% and 99% Value at Risk (VaR), and Conditional VaR (Expected Shortfall).
  2. In ML Lab, select **Gradient Boosting Classifier**, review the out-of-sample confusion matrix, ROC-AUC curve, and feature importance rankings (volatility clustering and volume surge).

---

### Scene 7: Multimodal Vision & Voice AI Interface (13:30 – 15:00)
**Click Path**: Click **"Vision AI"** $\rightarrow$ Click **"Voice AI"**

- **Presenter Talking Point**:
  > "Finally, we bring multimodal and hands-free interaction to the equity research desk. Analysts can upload a technical chart for instant VLM pattern breakdown, or interact using conversational voice commands."
- **Actions to Perform**:
  1. In Vision AI, click the sample candlestick chart and run analysis to view automated support/resistance detection and pattern classification.
  2. In Voice AI, click **"Start Listening"**, speak or click sample query *"Summarize NVDA quarterly risk"*, and observe the voice transcription and audio synthesis playback.

---

### Conclusion & Wrap-Up
- **Presenter Closing**:
  > "FinSight AI delivers an end-to-end blueprint for modern institutional FinTech: zero-credential resilience, strict regulatory safety, enterprise cloud readiness, and state-of-the-art AI engineering. Thank you."
