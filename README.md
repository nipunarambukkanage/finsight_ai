# FinSight AI: Generative AI Investment Intelligence & Stock Research Platform

[![CI Pipeline](https://github.com/nipunarambukkanage/finsight_ai/actions/workflows/ci.yml/badge.svg)](https://github.com/nipunarambukkanage/finsight_ai/actions)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.0-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS Fargate](https://img.shields.io/badge/AWS-ECS%20Fargate%20%7C%20Bedrock-FF9900.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Tests](https://img.shields.io/badge/Pytest%20%26%20Vitest-Passing%20100%25-brightgreen.svg)](#testing--verification)

> **Enterprise FinTech Reference Platform**: A commercial-grade investment intelligence application combining Generative AI, multi-provider LLM orchestration, verifiable SEC filing RAG, multi-stage autonomous research agents, Wall Street quantitative analytics, non-anticipative time-series machine learning, multimodal chart vision, and Voice AI.

---

> [!IMPORTANT]
> **REGULATORY DISCLAIMER**: FinSight AI is an engineering demonstration and decision-support research platform. It does NOT provide personalized investment advice, broker-dealer execution, or trading guarantees. Historical performance and simulated metrics are not indicative of future market results. All investment involves risk of loss.

---

## 1. Key Capabilities Matrix

| Domain | Capability | Implementation Highlights |
| :--- | :--- | :--- |
| **Generative AI & LLMs** | Multi-Provider Orchestration | Unified `LLMProviderInterface` supporting OpenAI (`gpt-4o`), Anthropic Claude 3.5 Sonnet, AWS Bedrock, Hugging Face, and deterministic zero-credential fallback. |
| **Retrieval-Augmented Generation (RAG)** | Verifiable SEC Filing Intelligence | Chunk-level semantic retrieval across 10-K, 10-Q, and 8-K filings with interactive in-line citations (`[Doc: ..., Page ...]`), cosine reranking, and citation drawer inspection. |
| **Autonomous AI Agents** | 8-Stage Equity Research Agent | Orchestrated research pipeline with real-time Server-Sent Events (SSE) telemetry, synthesizing a 14-section institutional report with Markdown & JSON export. |
| **Financial Sentiment** | FinBERT Financial NLP | Domain-specialized sentiment scoring (`ProsusAI/finbert`) with Loughran-McDonald lexicon fallback, entity sentiment extraction, and 30-day sentiment trajectories. |
| **Quantitative Analytics** | Institutional Risk & Technicals | Annualized Volatility, Sharpe, Sortino, Max Drawdown, Beta, Correlation Matrix, Historical & Parametric Value-at-Risk (95% & 99% VaR), CVaR, RSI, MACD, Bollinger Bands. |
| **Responsible Machine Learning** | Directional Equity Prediction | Strict chronological train/test splitting (`shuffle=False`), point-in-time feature engineering (eliminating look-ahead bias), Logistic Regression, Random Forest, Gradient Boosting. |
| **Multimodal Vision** | Financial Chart Inspection | Vision-Language Model analysis of candlestick patterns, support/resistance levels, trendline breaks, and volume moving average crossovers. |
| **Voice AI** | Speech-to-Text & Institutional Audio | Browser-native W3C Web Speech API integration, zero-latency transcription, and conversational audio synthesis. |
| **Institutional UX** | Bloomberg-Inspired Interface | React 19 + TypeScript + Vite, custom HTML5 Canvas OHLCV charting, glassmorphism, responsive data density, zero non-functional controls. |

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

## 3. Zero-Credential Institutional Demo Mode

FinSight AI is engineered to be **frictionless for evaluators, clients, and CI/CD pipelines**. 
- **No external API keys are required** to explore 100% of the application.
- The platform automatically activates `DemoProvider` when third-party keys are absent, utilizing high-fidelity deterministic 252-day geometric Brownian motion price paths, real-world fundamental balance sheets, indexed SEC 10-Ks, and pre-computed FinBERT sentiment scores for:
  - **Apple Inc. (`AAPL`)**
  - **Microsoft Corporation (`MSFT`)**
  - **NVIDIA Corporation (`NVDA`)**
  - **Alphabet Inc. (`GOOGL`)**
  - **Amazon.com Inc. (`AMZN`)**
  - **Tesla Inc. (`TSLA`)**

Visual pills across the interface transparently declare when simulated institutional datasets are active.

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
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 5. Configuration & Environment Variables

Copy `.env.example` to `.env` to configure external foundation models or customize ports:

```env
# Server
APP_ENV=development
PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
JWT_SECRET_KEY=change-this-in-production-to-a-secure-random-token

# Default LLM Provider (demo | openai | anthropic | huggingface | bedrock)
DEFAULT_LLM_PROVIDER=demo

# External Model Keys (Optional - activates real cloud inference when set)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
HUGGINGFACE_API_TOKEN=
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# Database & Cache (Used in Docker / Production)
DATABASE_URL=postgresql://finsight:finsight_secret@localhost:5432/finsight_db
REDIS_URL=redis://localhost:6379/0
```

---

## 6. Testing & Verification

The platform maintains extensive unit and integration test suites for both backend and frontend:

### Backend Test Suite (Pytest)
```bash
pytest --cov=backend/app --cov-report=term-missing tests/backend/
```
**Results**:
- 19 passed automated tests.
- 77% overall statement test coverage across all quantitative, RAG, and ML engine modules.
- Zero deprecation warnings (`datetime.now(timezone.utc)` standard enforced).

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm test
```
**Results**:
- 3/3 passed component tests verifying DisclaimerBanner rendering, DonutChart SVG path calculations, and CorrelationHeatmap cell rendering.

### Production Production Build
```bash
cd frontend
npm run build
```
- Type-checked with zero TypeScript compilation errors.
- Optimized bundle generated in `frontend/dist/`.

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

- [docs/architecture.md](docs/architecture.md): High-level system architecture and data flows.
- [docs/ai-architecture.md](docs/ai-architecture.md): Multi-provider LLM abstraction, FinBERT sentiment, and VLM design.
- [docs/rag.md](docs/rag.md): SEC filing RAG retrieval, chunking, and verifiable citation grounding.
- [docs/agents.md](docs/agents.md): 8-Stage Autonomous Research Agent execution and SSE streaming protocol.
- [docs/ml-methodology.md](docs/ml-methodology.md): Responsible time-series ML, temporal splits, and avoidance of look-ahead bias.
- [docs/aws-architecture.md](docs/aws-architecture.md): Enterprise AWS Terraform infrastructure specification.
- [docs/demo-script.md](docs/demo-script.md): 12-15 minute live executive demonstration script.
- [SECURITY.md](SECURITY.md): Enterprise security architecture, redacting filters, and vulnerability disclosure.
- [AGENTS.md](AGENTS.md): Autonomous agent guardrails and development guidelines.

---

## 9. License & Attribution

Developed by the **FinSight AI Engineering Team**. Released under the MIT License for institutional research and demonstration purposes.
