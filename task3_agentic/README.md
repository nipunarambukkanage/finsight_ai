# Task 3 - Agentic Financial Research

[![Open Task 3 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nipunarambukkanage/finsight_ai/blob/main/task3_agentic/notebooks/task3_agentic_research.ipynb)

The Colab link above points to the public repository on the `main` branch. Run
the notebook with live adapters when available, keep the tool observations and
handoffs visible, and commit the regenerated trace and cache demonstration.

This submission contains a single observation-driven researcher and a two-agent pipeline, each exposed through a compiled LangGraph entrypoint. Typed tools are enforced by role: Data Analyst has price, volatility, and sentiment; Research Writer has news and web search. The writer sends one typed clarification request and the data agent answers from its existing state. No manual action occurs inside the pipeline.

Run from this directory:

```bash
pip install -r ../requirements-assessment.txt
python run_agent.py --ticker AAPL --two-agent
python run_agent.py --ticker AAPL
python run_agent.py --ticker AAPL --two-agent --demo  # explicit offline fixture mode
```

Every tool call is written to `logs/agent_trace.jsonl` with agent, tool, validated arguments, output preview capped at 200 characters, status, duration, and a reference to the complete permitted output under `logs/tool_outputs/`. Completed single-agent and coordinated briefs are cached under `artifacts/cache/` using workflow, ticker, data mode, configuration fingerprint, and UTC date, so live and demo results cannot collide. The second run returns `cached: true` without re-running tools.

The live adapters use yfinance and DDGS when available. Provider failures are represented as limitations. A deterministic fallback is available only when `--demo` (or `allow_demo_fallback=True`) is explicitly selected, and the mode remains visible in the structured output.
