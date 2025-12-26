# FinSight AI: 10-Minute Executive & Interview Demonstration Script

## 1. Demonstration Metadata
- **Duration**: Exactly 10 minutes
- **Target Audience**: Quant Leads, Heads of Quantitative Research, AI Engineering Directors, CTOs
- **Core Message**: FinSight AI is an institutional research and decision-support engine combining stateful LangGraph agent pipelines, verifiable SEC filing RAG, AST code sandboxing, deterministic backtesting, and simulation-only shadow execution without any real-money order routing.

---

## 2. Timed Scene-by-Scene Script

### Scene 1: Introduction & Regulatory Guardrails (00:00 – 01:30)
**Click Path**: Open `http://localhost:5173/` $\rightarrow$ Dashboard
- **Presenter Talking Point**:
  > *"Welcome to FinSight AI. In quantitative finance, the challenge with generative AI is not generating text—it's guaranteeing determinism, verifiable lineage, and operational safety. FinSight AI is purpose-built as an institutional research and trading-decision support engine. Notice the regulatory banner at the top: the system enforces an absolute invariant—it never places real-money trades or connects to brokerage execution APIs."*
- **Key Actions**:
  1. Highlight the institutional dark theme, telemetry metrics, and regulatory disclaimer.
  2. Point to the Ticker Selector (`AAPL`, `MSFT`, `NVDA`) and explain zero-credential demo mode.

---

### Scene 2: The Autonomous Workflow Hub & LangGraph State Machine (01:30 – 04:00)
**Click Path**: Click **"Autonomous Research Workflow"** in the sidebar (`/workflow`)
- **Presenter Talking Point**:
  > *"Rather than relying on unconstrained chat prompts, our flagship capability is a stateful LangGraph workflow. It coordinates specialized agents through strict sequential stages: Market Data Snapshot, SEC Evidence Retrieval, Strategy Specification, Developer Agent Code Generation, QA Agent Sandbox Validation, Deterministic Backtesting, Human Approval Gate, and Shadow Simulation."*
- **Key Actions**:
  1. Click **"Initiate Autonomous Workflow"** for `AAPL`.
  2. Observe the interactive pipeline stepper animating across the 9 stages.
  3. Show the workflow pausing cleanly at **Stage 7: Approval Gate (`WAITING_APPROVAL`)**.

---

### Scene 3: SEC Evidence Retrieval & Prompt Injection Defense (04:00 – 05:30)
**Click Path**: Select the **"SEC Evidence"** tab in the Workflow Hub
- **Presenter Talking Point**:
  > *"Notice how the Research Agent grounds its thesis in audited 10-K disclosures. Every claim links to an immutable citation with page number, filing date, and cosine similarity. Furthermore, because corporate filings are untrusted external text, our RAG pipeline passes all chunks through a Prompt Injection Sanitizer that strips prompt hijacking attempts before model ingestion."*
- **Key Actions**:
  1. Inspect the retrieved citations and corporate risk excerpts for Apple.
  2. Point out the zero-hallucination confidence score and data limitation transparency.

---

### Scene 4: Developer Agent, AST Sandbox & QA Look-Ahead Perturbation (05:30 – 07:30)
**Click Path**: Click **"Candidate Strategy Code"** tab $\rightarrow$ Switch to **"QA Audit & Bias Checks"** tab
- **Presenter Talking Point**:
  > *"Here is where engineering rigor shines. The Developer Agent wrote executable Python code for a dual-momentum volatility breakout strategy. Before execution, the QA Agent subjected the code to Abstract Syntax Tree (AST) static analysis. We whitelist only mathematical libraries—any attempt to import `os`, `socket`, or call `exec()` is blocked at the grammar level. Next, the QA Agent runs a look-ahead perturbation test: it shocks future prices to prove the strategy doesn't peek forward with negative shifts."*
- **Key Actions**:
  1. Display the syntax-highlighted candidate Python code (`generate_signals(df)`).
  2. Show the green QA badges: AST Import Filter Passed, Unit Test Passed, Look-Ahead Bias Absent, Missing Data Resilient.

---

### Scene 5: Deterministic Backtest & Human-in-the-Loop Approval (07:30 – 09:00)
**Click Path**: Click **"Deterministic Backtest"** tab $\rightarrow$ Switch to **"Human Approval Gate"** tab
- **Presenter Talking Point**:
  > *"In the backtest tab, we observe deterministic performance on a strict out-of-sample test partition: Sharpe ratio of 1.42, 5.0 bps slippage per trade, and complete transaction cost accounting. But notice: the agent cannot autonomously deploy to simulation. Wall Street risk management demands human oversight. Here in the Approval Gate, the operator inspects the SHA-256 code fingerprint, confirms separation of duties, and provides approval."*
- **Key Actions**:
  1. Inspect the equity curve and trade ledger showing execution prices and slippage.
  2. In the Approval Gate modal, enter reviewer notes: *"Reviewed out-of-sample Sharpe and AST report. Approved for paper simulation."*
  3. Click **"Approve & Authorize Shadow Simulation"**.

---

### Scene 6: Shadow Trading Simulation & Decision Brief (09:00 – 10:00)
**Click Path**: Click **"Shadow Simulation"** tab $\rightarrow$ View Final Recommendation Banner
- **Presenter Talking Point**:
  > *"Once approved, the strategy enters our isolated Shadow Trading environment. The virtual ledger tracks hypothetical fills, mark-to-market P&L, and cash reserves without capital risk. The operator can pause or resume at any time. Finally, the synthesized Institutional Brief issues an evidence-backed HOLD/BUY rating with explicit risk scenarios. FinSight AI bridges generative AI and quantitative finance with uncompromising safety."*
- **Key Actions**:
  1. Show the virtual cash balance (\$100,000 baseline) and simulated order ledger.
  2. Toggle the **"Pause Simulation"** and **"Resume Simulation"** operator kill-switch.
  3. Conclude at the Institutional Recommendation banner.

---

## 3. High-Value Interview Q&A Talking Points

- **Q: Why LangGraph instead of simple autogen or chain-of-thought?**
  - *Answer*: Financial workflows require explicit state machines, resumability after pauses, checkpointing, and conditional loops (e.g., retrying code generation if AST checks fail). LangGraph provides typed state graphs rather than uncontrolled probabilistic loops.
- **Q: How do you prevent look-ahead bias in AI-generated strategies?**
  - *Answer*: Two layers: first, our backtesting engine enforces strict chronological bar-by-bar iteration over temporal train/val/test splits (`shuffle=False`). Second, the QA Agent runs an adversarial perturbation check, perturbing future prices and asserting that past signals remain invariant.
- **Q: What happens if external LLM providers experience an outage or rate limit?**
  - *Answer*: The Multi-Provider Gateway features automated retries with exponential backoff, timeout caps, and instantaneous fallback to local Ollama or deterministic zero-credential `DemoProvider`.
