# FinSight AI: Generative AI Investment Intelligence & Stock Research Platform

[![CI Pipeline](https://github.com/nipunarambukkanage/finsight_ai/actions/workflows/ci.yml/badge.svg)](https://github.com/nipunarambukkanage/finsight_ai/actions)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS Fargate](https://img.shields.io/badge/AWS-ECS%20Fargate%20%7C%20Bedrock-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Verification](https://img.shields.io/badge/verification-rerun%20locally-blue.svg)](#testing--verification)

> **Enterprise FinTech Reference Platform**: A commercial-grade investment intelligence application combining Generative AI, multi-provider LLM orchestration, verifiable SEC filing RAG, multi-stage autonomous research agents, Wall Street quantitative analytics, non-anticipative time-series machine learning, multimodal chart vision, and Voice AI.

## Assessment-ready deliverables

The repository now includes independently executable submissions for all three
assessment domains:

- `task1_financial/`: live/demo-labelled yfinance pipeline, first-principles indicators, validated sentiment/signal reasoning, and one-page brief rendering.
- `task2_genai/`: filing-risk extraction contracts, teacher dataset generation and source-disjoint splits, QLoRA training configuration, merged-model flow, and held-out evaluation.
- `task3_agentic/`: five authorized tools, observation-driven routing, typed two-agent critique handoff, persistent cache, and `agent_trace.jsonl`.

See [docs/assessment-evidence.md](docs/assessment-evidence.md), [CITATIONS.md](CITATIONS.md), and [REFLECTION.md](REFLECTION.md). Run the assessment paths from [docs/runbook.md](docs/runbook.md) and follow the final [submission runbook](docs/submission-runbook.md). The [five-minute video walkthrough guide](docs/video-walkthrough-guide.pdf) includes a simple narration script. Live provider and Colab outputs must be regenerated before submission; fixture outputs are explicitly labelled and are not live evidence.

---

> [!IMPORTANT]
> **REGULATORY DISCLAIMER**: FinSight AI is an engineering demonstration and decision-support research platform. It does NOT provide personalized investment advice, broker-dealer execution, or trading guarantees. Historical performance and simulated metrics are not indicative of future market results. All investment involves risk of loss.

---

## 1. Key Capabilities Matrix

| Domain | Capability | Implementation Highlights |
| :--- | :--- | :--- |
| **LangGraph Autonomous Workflow** | Stateful Research & Strategy Pipeline | StateGraph coordinating specialized agents (Market Data, SEC RAG, Strategy Spec, Dev Agent, QA Agent, Backtesting, Approval Gate, Shadow Simulation) with checkpointing, failure retries, and pause/resume. |
| **Generative AI & LLMs** | Multi-Provider Orchestration | Unified `LLMProviderInterface` supporting OpenAI (`gpt-4o`), Anthropic Claude 3.5 Sonnet, AWS Bedrock, Ollama (local offline), and deterministic zero-credential fallback. |
| **Strategy Development & QA Sandbox** | AST Code Analysis & Adversarial QA | Developer Agent generating candidate Python code; QA Agent enforcing AST module whitelisting, restricted subprocess isolation, invariant bounds, and look-ahead bias perturbation tests. |
| **Deterministic Backtesting** | Reproducible Simulation Engine | Chronological train/val/test temporal partitions, non-anticipative bar-by-bar execution, 5.0 bps slippage, fee accounting, trade ledger, equity curve, and anomaly diagnostics. |
| **Shadow Trading & Approval Gate** | Virtual Simulation Environment | Cryptographic SHA-256 human approval gate with separation of duties; isolated virtual portfolio with simulated fills and operator emergency pause/resume. Strictly zero real-money order execution. |
| **Persistent Memory Architecture** | Cross-Run Vector Memory | Isolated tenant memory with secret sanitization (redacting API keys/passwords), SHA-256 content deduplication, version lineage, and PostgreSQL/pgvector compatibility. |
| **Retrieval-Augmented Generation (RAG)** | Verifiable SEC Filing Intelligence | Chunk-level semantic retrieval across 10-K, 10-Q, and 8-K filings with prompt-injection sanitization, interactive in-line citations (`[Doc: ..., Page ...]`), cosine reranking, and citation drawer inspection. |
| **Financial Sentiment** | FinBERT Financial NLP | Domain-specialized sentiment scoring (`ProsusAI/finbert`) with Loughran-McDonald lexicon fallback, entity sentiment extraction, and 30-day sentiment trajectories. |
| **Quantitative Analytics** | Institutional Risk & Technicals | Annualized Volatility, Sharpe, Sortino, Max Drawdown, Beta, Correlation Matrix, Historical & Parametric Value-at-Risk (95% & 99% VaR), CVaR, RSI, MACD, Bollinger Bands. |
| **Responsible Machine Learning** | Directional Equity Prediction | Strict chronological train/test splitting (`shuffle=False`), point-in-time feature engineering (eliminating look-ahead bias), Logistic Regression, Random Forest, Gradient Boosting. |
| **Multimodal Vision & Voice AI** | Financial Chart Inspection & Voice | Vision-Language Model analysis of candlestick patterns, support/resistance levels, trendline breaks, and browser-native Speech-to-Text / Audio Briefings. |
| **Institutional UX** | Bloomberg-Inspired Interface | React 19 + TypeScript + Vite, custom HTML5 Canvas OHLCV charting, glassmorphism, responsive data density, visual 7-tab Workflow Hub, zero non-functional controls. |

---

## 2. System Architecture

```mermaid
graph TD
    Client[React 19 Institutional Frontend - Vite / TypeScript]
    
    subgraph Gateway & Security Tier
        API[FastAPI Asynchronous Gateway]
        Auth[JWT Authentication & Demo Fallback]
        Telemetry[Request ID & Latency Telemetry Middleware]
        Sanitizer[SensitiveDataFilter Logging]
        API --> Auth
        API --> Telemetry
        API --> Sanitizer
    end

    Client -->|HTTPS / SSE| API

    subgraph Analytical Core
        QuantEngine[Quantitative Analytics & Risk Engine]
        MLEngine[Time-Series ML Pipeline]
        MarketSvc[Market Data & Brownian Simulation Engine]
    end

    subgraph AI & Orchestration Core
        ProviderMgr[Multi-Provider LLM Manager]
        RAGEngine[LangChain Semantic RAG Engine]
        AgentEngine[8-Stage Autonomous Research Agent]
        SentEngine[FinBERT Sentiment Classifier]
        VLMEngine[Multimodal Chart Vision Service]
        VoiceEngine[Voice AI Audio Engine]
    end

    API --> QuantEngine
    API --> MLEngine
    API --> MarketSvc
    API --> ProviderMgr
    API --> RAGEngine
    API --> AgentEngine
    API --> SentEngine
    API --> VLMEngine
    API --> VoiceEngine

    subgraph Data & Persistence Tier
        VectorStore[(pgvector PostgreSQL 16 / In-Memory HNSW)]
        Cache[(Redis 7 In-Memory Cache & Pub/Sub)]
        FilingStore[(SEC Filings & Synthetic Document Corpus)]
    end

    RAGEngine --> VectorStore
    RAGEngine --> FilingStore
    API --> Cache
```

---

## 3. Explicit Zero-Credential Institutional Demo Mode

FinSight AI is engineered to be **frictionless for evaluators, clients, and CI/CD pipelines**.
- **No external API keys are required** when the explicit `DEMO_MODE=True` profile is selected.
- That profile uses high-fidelity deterministic 252-day geometric Brownian motion price paths, labelled synthetic filings, and deterministic sentiment fixtures for:
  - **Apple Inc. (`AAPL`)**
  - **Microsoft Corporation (`MSFT`)**
  - **NVIDIA Corporation (`NVDA`)**
  - **Alphabet Inc. (`GOOGL`)**
  - **Amazon.com Inc. (`AMZN`)**
  - **Tesla Inc. (`TSLA`)**

Visual pills across the interface transparently declare when simulated institutional datasets are active.

### Cost boundary

The repository has no billing integration and does not provision cloud resources by
itself. The default local profile (`DEMO_MODE=True`, `DEFAULT_LLM_PROVIDER=DEMO`)
uses deterministic fixtures and open-source local services, so it can be run without
paid accounts. The AWS Terraform files and hosted model adapters are reference or
opt-in paths; applying Terraform or supplying a provider key is outside the free
local profile and may incur that provider's charges. Keep those keys empty and do
not run `terraform apply` when a zero-cost evaluation is required.

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.12+
- Node.js 20+ and npm
- Docker & Docker Compose (Optional, for containerized run)

### Option A: Local Development (Fastest)

#### 1. Start the FastAPI Backend
```bash
# In project root
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
*The interactive OpenAPI documentation will be live at `http://localhost:8000/docs`.*

#### 2. Start the React Frontend
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```
*Open your browser to `http://localhost:5173` to access the FinSight AI terminal.*

---

### Option B: Docker Compose (Full Stack)

To run the complete stack including PostgreSQL with `pgvector` and Redis:
```bash
docker compose up --build
```
- Frontend: `http://localhost` (or `http://localhost:5173`)
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 5. Configuration & Environment Variables

Copy `.env.example` to `.env` to configure external foundation models or customize ports:

```env
# Server
APP_ENV=development
PORT=8000
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
SECRET_KEY=change-this-in-production-to-a-secure-random-token

# Default LLM route (DEMO | GROQ | OPENROUTER | OLLAMA | VLLM)
DEFAULT_LLM_PROVIDER=demo
DEMO_MODE=True  # set False in production; no fabricated fallback is then permitted

# Hosted model keys (optional; leave blank for zero-cost demo mode)
OPENAI_API_KEY=
OPENROUTER_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=
HUGGINGFACE_API_TOKEN=
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
VLLM_BASE_URL=http://localhost:8001/v1
VLLM_MODEL=Qwen/Qwen2.5-1.5B-Instruct

# Database & cache (SQLite is the zero-cost local default)
DATABASE_URL=sqlite+aiosqlite:///./finsight.db
REDIS_URL=redis://localhost:6379/0
```

---

## 6. Testing & Verification

The platform maintains extensive unit, integration, and security test suites for both backend and frontend:

### Backend Test Suite (Pytest)
```bash
pytest tests/backend/
```
**Historical baseline** (from an earlier repository revision): 36 automated tests were reported as passing. This is not a current completion claim; rerun the suite after installing dependencies.
- Comprehensive test coverage across LangGraph stateful orchestration, AST static security sandbox, QA look-ahead bias perturbation, deterministic backtesting, slippage and fee friction, shadow paper trading, persistent memory sanitization/deduplication, prompt injection defense, and quantitative risk engines.
- Zero deprecation warnings (`datetime.now(timezone.utc)` standard enforced).

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm test
```
**Historical baseline** (from an earlier repository revision): 4 component suites were reported as passing. Rerun after `npm ci` for current evidence.

### Production Build Verification
```bash
cd frontend
npm run build
```
- Type-check and bundle verification must be rerun after the current changes.

---

## 7. Cloud Deployment (AWS ECS & Terraform)

Production infrastructure is codified in `infrastructure/terraform/`:
- **AWS ECS Fargate**: Serverless containerized backend with autoscaling.
- **AWS CloudFront & S3**: Global edge distribution for the React SPA.
- **Amazon RDS PostgreSQL 16**: Multi-AZ database with native `pgvector` extension.
- **Amazon ElastiCache Redis**: High-throughput distributed cache and pub/sub.
- **AWS Secrets Manager & KMS**: Enterprise secrets encryption and automated key rotation.

See [docs/aws-architecture.md](docs/aws-architecture.md) for full cloud configuration details.

---

## 8. Documentation Sitemap

- [docs/architecture.md](docs/architecture.md): High-level system architecture, microservices, and data flows.
- [docs/architecture-v2.md](docs/architecture-v2.md): Assessment-first modular-monolith target architecture and adoption records.
- [docs/agents.md](docs/agents.md): LangGraph stateful orchestration, 8-stage research agent, and SSE streaming protocol.
- [docs/memory.md](docs/memory.md): Persistent memory architecture, secret sanitization, and pgvector compatibility.
- [docs/backtesting.md](docs/backtesting.md): Deterministic backtesting engine, slippage/fee friction, and look-ahead bias prevention.
- [docs/shadow-trading.md](docs/shadow-trading.md): Simulation-only shadow paper trading, virtual portfolio, and human approval gates.
- [docs/security.md](docs/security.md): Threat modeling, AST code execution sandbox, prompt injection defense, and RBAC.
- [docs/local-development.md](docs/local-development.md): Zero-credential local setup, Ollama air-gapped LLM, and test runners.
- [docs/demo-script.md](docs/demo-script.md): 10-minute executive and interview demonstration script.
- [docs/ai-architecture.md](docs/ai-architecture.md): Multi-provider LLM gateway, FinBERT sentiment, and VLM design.
- [docs/rag.md](docs/rag.md): SEC filing RAG retrieval, chunking, and verifiable citation grounding.
- [docs/ml-methodology.md](docs/ml-methodology.md): Responsible time-series ML, temporal splits, and avoidance of look-ahead bias.
- [docs/aws-architecture.md](docs/aws-architecture.md): Enterprise AWS Terraform infrastructure specification.
- [docs/implementation-status.md](docs/implementation-status.md): Complete baseline and post-upgrade implementation audit.
- [SECURITY.md](SECURITY.md): Enterprise security architecture, redacting filters, and vulnerability disclosure.
- [AGENTS.md](AGENTS.md): Autonomous agent guardrails and development guidelines.

---

## 9. License & Attribution

Developed by the **FinSight AI Engineering Team**. Released under the MIT License for institutional research and demonstration purposes.
