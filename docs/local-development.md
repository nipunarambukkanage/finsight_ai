# FinSight AI - Local Development & Setup Guide

## 1. Quick Local Setup (< 5 Minutes)
FinSight AI is built to run out-of-the-box on Windows, macOS, and Linux without external cloud dependencies or API keys.

### 1.1 Prerequisites
- **Python 3.12+**
- **Node.js 20+** and **npm**
- (Optional) **Ollama** for local offline LLM inference

---

## 2. Backend Setup
```bash
# 1. Navigate to project root
cd finsight_ai

# 2. Create and activate a Python virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS / Linux:
# source .venv/bin/activate

# 3. Install core dependencies
pip install -r backend/requirements.txt

# 4. Launch FastAPI development server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

---

## 3. Frontend Setup
```bash
# In a new terminal window
cd frontend

# 1. Install dependencies
npm install

# 2. Run local Vite development server
npm run dev
```
- Access application UI: `http://localhost:5173`

When the full Docker Compose stack is used and port 8000 is occupied by another
local service, the backend is exposed on `http://localhost:18000` and the
frontend is built to use that address. The PostgreSQL container is exposed on
host port `55432`.

---

## 4. Zero-Credential Demo Mode vs Local LLM (Ollama)

### 4.1 Explicit Demo Mode
Set `DEMO_MODE=True` for a zero-credential demonstration. The mode is visible in
API metadata and output provenance; production should set `DEMO_MODE=False`:
- **Market Data**: Parquet-cached analytical datasets (`backend/app/data/pipeline.py`) with reproducible geometric Brownian motion synthesis for `AAPL`, `MSFT`, and `NVDA`.
- **LLM Gateway**: `DemoProvider` generates structured, verifiable financial analyses, SEC citations, and candidate strategy code with zero network latency or external costs.

### 4.2 Local Offline LLM with Ollama
For private, air-gapped on-device LLM inference:
1. Install and run [Ollama](https://ollama.ai/):
   ```bash
   ollama run llama3.2
   ```
2. Set the environment variable in `.env`:
   ```env
   DEFAULT_LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```
FinSight AI's `OllamaProvider` (`backend/app/providers/manager.py`) routes research and code-generation tasks to your local model with bounded retries and timeouts. If the provider is unavailable, production mode returns an explicit error; demo fallback remains opt-in through `DEMO_MODE`.

---

## 5. Running Automated Verification Suites

### 5.1 Backend Pytest Suite
Run the backend test suite across workflow orchestration, AST sandbox, backtesting, RAG, memory, and assessment contracts:
```bash
# Windows
.\.venv\Scripts\pytest.exe tests/backend/

# macOS / Linux
pytest tests/backend/
```

### 5.2 Frontend Vitest & TypeScript Verification
```bash
cd frontend

# Run unit tests
npm test

# Run TypeScript type check and production build
npm run build
```
