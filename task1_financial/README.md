# Task 1 - Financial AI Equity Research

[![Open Task 1 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nipunarambukkanage/finsight_ai/blob/main/task1_financial/notebooks/task1_equity_research.ipynb)

The Colab link above points to the public repository on the `main` branch. After
opening it, run every cell from top to bottom and keep the outputs visible in
the committed notebook.

This is an executable two-year equity research pipeline. It fetches OHLCV and news through yfinance, retains raw bars, adjusted close, and corporate-action hashes, computes SMA-50/SMA-200, Wilder RSI-14, MACD 12/26/9, and Bollinger Bands 20/2 from first principles, validates LLM JSON with Pydantic, and renders a one-page brief.

Run from this directory:

```bash
pip install -r ../requirements-assessment.txt
python run_pipeline.py --ticker AAPL
python run_pipeline.py --ticker AAPL --evaluation-date 2026-08-31
python run_pipeline.py --ticker AAPL --demo
```

Live output is labelled `live` and includes a SHA-256 dataset fingerprint. Demo output is deterministic and labelled `demo`; it is never presented as live evidence. Provider failures produce a typed limitation instead of silently changing tickers.

The notebook `notebooks/task1_equity_research.ipynb` is the submission entry point. Before submission, execute it in Colab or locally and commit the resulting outputs.
