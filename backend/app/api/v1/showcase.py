from fastapi import APIRouter
from typing import List, Dict, Any
from backend.app.services.evaluation import llm_evaluator
from backend.app.providers.manager import provider_manager

router = APIRouter()

@router.get("/capabilities")
async def get_technology_capabilities():
    """Retrieve full engineering capability breakdown demonstrated across FinSight AI."""
    capabilities = [
        {
            "id": "llm",
            "category": "Generative AI",
            "title": "Large Language Models & Multi-Provider Architecture",
            "where_used": "AI Research Assistant, Report Writer, Comparative Intelligence",
            "why_used": "Extracts semantic insights from unstructured financial disclosures with strict provider isolation and zero-downtime failover.",
            "tech_stack": "OpenAI, Anthropic, Bedrock, DemoProvider Abstraction"
        },
        {
            "id": "huggingface",
            "category": "Open-Source AI",
            "title": "Hugging Face FinBERT & Model Serving",
            "where_used": "Financial Sentiment Engine, News Risk Analysis",
            "why_used": "Domain-specific financial transformer models deliver superior precision on financial sentiment compared to generic NLP models.",
            "tech_stack": "Hugging Face Transformers, ProsusAI/finbert, PyTorch/ONNX"
        },
        {
            "id": "rag",
            "category": "Knowledge Retrieval",
            "title": "LangChain Retrieval-Augmented Generation (RAG)",
            "where_used": "SEC Form 10-K/10-Q filing exploration, Document Intelligence",
            "why_used": "Ensures factual answers backed by verifiable citations, preventing hallucinations on monetary figures and reporting dates.",
            "tech_stack": "LangChain, Sentence-Transformers, Dense Vector Cosine Index, PostgreSQL pgvector"
        },
        {
            "id": "agents",
            "category": "Autonomous AI",
            "title": "Multi-Stage Autonomous Research Agent",
            "where_used": "AI Research Agent Workspace, Comprehensive Equity Reports",
            "why_used": "Orchestrates multi-step investigation across 8 specialized logical analyst agents with real-time SSE execution tracing.",
            "tech_stack": "LangChain Agentic Patterns, Structured Output Pydantic, SSE Streaming"
        },
        {
            "id": "quant",
            "category": "Financial Technology",
            "title": "Python Quantitative Analytics Engine",
            "where_used": "Stock workspace, Risk indicators, Portfolio Intelligence",
            "why_used": "Guarantees 100% mathematical accuracy for Sharpe, Sortino, VaR 95/99%, Expected Shortfall, RSI, MACD, and Bollinger Bands without LLM approximation.",
            "tech_stack": "NumPy, Pandas, SciPy, Scikit-Learn"
        },
        {
            "id": "ml",
            "category": "Machine Learning",
            "title": "Time-Series Machine Learning Lab",
            "where_used": "Directional return classification, Volatility estimation",
            "why_used": "Enforces strict temporal train/test split without random shuffling to prevent look-ahead bias in non-stationary financial series.",
            "tech_stack": "Scikit-Learn, StandardScaler, LogisticRegression, RandomForest, GradientBoosting"
        },
        {
            "id": "fastapi",
            "category": "Backend Engineering",
            "title": "FastAPI Async Microservice Core",
            "where_used": "Central Application Gateway & REST/SSE Endpoints",
            "why_used": "Provides asynchronous I/O, Pydantic v2 validation, automated OpenAPI docs, and institutional microsecond response latency.",
            "tech_stack": "FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 asyncio, Alembic"
        },
        {
            "id": "react",
            "category": "Frontend Engineering",
            "title": "React 18/19 + TypeScript Institutional Dashboard",
            "where_used": "FinSight AI User Interface & Workspace System",
            "why_used": "Delivers Bloomberg-grade serious FinTech visual design, responsive layouts, Canvas/SVG charts, and accessible ARIA components.",
            "tech_stack": "React, TypeScript, Vite, TanStack Query, React Router, Vanilla CSS Tokens"
        },
        {
            "id": "multimodal",
            "category": "Multimodal AI",
            "title": "Vision-Language Multimodal Analysis",
            "where_used": "Chart inspection, earnings slide OCR and visual table reasoning",
            "why_used": "Extracts operational insights directly from balance sheet tables and technical price charts.",
            "tech_stack": "VLM Vision Architecture, GPT-4o Vision / Claude 3.5 Sonnet hooks"
        },
        {
            "id": "voice",
            "category": "Voice AI",
            "title": "Voice AI Interactive Market Briefing",
            "where_used": "Audio market briefing generator & speech command assistant",
            "why_used": "Hands-free analyst interactions using browser Web Speech STT and synthesized audio briefing summaries.",
            "tech_stack": "Web Speech API, Audio Synthesis Pipeline"
        },
        {
            "id": "cloud",
            "category": "DevOps & Cloud Architecture",
            "title": "AWS Cloud Infrastructure & Docker CI/CD",
            "where_used": "Enterprise Deployment & Containerization",
            "why_used": "Production-ready IaC configuration for ECS Fargate, RDS pgvector, ElastiCache Redis, S3, ALB, and CloudFront.",
            "tech_stack": "Docker, Docker Compose, Terraform, GitHub Actions, AWS ECS/RDS/S3"
        }
    ]
    return capabilities

@router.get("/evaluation-benchmark")
async def get_evaluation_benchmark():
    """Execute and return real-time LLM evaluation metrics and retrieval benchmarks."""
    return llm_evaluator.run_benchmark()

@router.get("/providers")
async def get_available_providers():
    """List available LLM providers and their operational statuses."""
    return provider_manager.list_providers()
