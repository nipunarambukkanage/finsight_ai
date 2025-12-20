# Security Policy & LLM Guardrails

## 1. Overview
FinSight AI adheres to rigorous defense-in-depth security standards designed specifically for modern financial technology and Generative AI applications. This document details our security boundaries, prompt injection mitigations, and data protection practices.

---

## 2. Core Security Architecture

### 2.1 Secrets & Environment Isolation
- **Zero Committed Secrets:** All credentials, private tokens, and database passwords reside strictly in environment variables (`.env`).
- **Sensitive Log Redaction:** The logging system enforces a `SensitiveDataFilter` that automatically masks authorization headers, bearer tokens, API keys, and passwords before records hit stdout.
- **Failover Security:** If external credentials are absent, the application securely falls back to `DemoProvider` rather than logging connection failure credentials or crashing.

### 2.2 API Security & Transport Protection
- **CORS Configuration:** Explicit origin allowlisting restricting browser API access to authorized frontend domains.
- **Security Headers:** Nginx and FastAPI middleware enforce:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- **Session Boundaries:** Stateless JWT authentication using HMAC SHA-256 with role-based access control (`analyst`, `senior_analyst`).

---

## 3. Generative AI & LLM Security

### 3.1 Prompt Injection Protection
- **System Prompt Isolation:** System instructions and user inputs are strictly segmented using structured messages rather than raw concatenated string templates.
- **Retrieved Document Trust Boundary:** Unstructured filing text retrieved via RAG is treated as untrusted external content and demarcated within explicit XML / JSON citation blocks.
- **No Unsafe Execution:** The LLM does not execute arbitrary code or shell commands. Tool calling is restricted to an allowlist of deterministic Python methods.

### 3.2 Hallucination Mitigation & Financial Integrity
- **Calculation Architecture:** Financial values (Sharpe, VaR, CVaR, RSI, MACD, returns) are **never calculated by the LLM**. They are computed exclusively by Python engines (`NumPy`, `Pandas`, `SciPy`) and passed as verified facts.
- **Evidence-First Grounding:** All RAG answers require explicit source citations (`[Doc: AAPL-2024-10K, Page 4]`). When evidence is insufficient, the system explicitly reports data limitations.

### 3.3 Agentic Boundedness
- **Strict Iteration Caps:** Multi-stage research agents operate with bounded step execution (maximum 8 stages) and execution timeouts.
- **No Trading Execution:** The platform is strictly an investment intelligence research system. It has **no automated order execution capability or broker trading APIs**.

---

## 4. Reporting a Vulnerability
To report a security vulnerability or concern, please open a private security advisory on GitHub or email security@finsight.ai with reproduction steps.
