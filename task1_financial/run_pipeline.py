"""Run Task 1 in live mode, or explicitly labelled demo mode when offline."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    from task1_financial.src.pipeline import YFinanceMarketAdapter, add_indicators, build_snapshot
    from task1_financial.src.reasoning import analyze_news_and_signal
    from task1_financial.src.render import render_markdown, write_html
except ImportError:
    from src.pipeline import YFinanceMarketAdapter, add_indicators, build_snapshot
    from src.reasoning import analyze_news_and_signal
    from src.render import render_markdown, write_html


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="AAPL")
    parser.add_argument("--evaluation-date", help="Optional UTC evaluation date (YYYY-MM-DD)")
    parser.add_argument("--demo", action="store_true", help="Use deterministic data; never masquerades as live data")
    parser.add_argument("--output", default="artifacts/equity_brief.md")
    args = parser.parse_args()
    result = YFinanceMarketAdapter().fetch(args.ticker, years=2, allow_demo_fallback=args.demo)
    snapshot = build_snapshot(result, evaluation_date=args.evaluation_date)
    caller = None
    if os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"):
        try:
            from backend.app.providers.gateway import ModelRequest, model_gateway
            request = ModelRequest(task_type="financial_classification", complexity="medium", allow_demo_fallback=False)
            if model_gateway.route(request) != "DEMO":
                async def gateway_caller(system: str, user: str) -> str:
                    response, _ = await model_gateway.generate(user, system_prompt=system, request=request)
                    return response if isinstance(response, str) else response.model_dump_json()
                caller = gateway_caller
        except Exception as exc:
            print(f"LLM gateway unavailable; continuing with deterministic validation: {exc}")
    research = __import__("asyncio").run(analyze_news_and_signal(snapshot, caller=caller))
    research.report_markdown = render_markdown(research)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(research.report_markdown, encoding="utf-8")
    write_html(research, output.with_suffix(".html"))
    output.with_suffix(".json").write_text(research.model_dump_json(indent=2), encoding="utf-8")
    if not result.bars.empty:
        safe_ticker = re.sub(r"[^A-Z0-9._-]", "_", args.ticker.upper())
        raw_path = output.with_name(f"{safe_ticker}_market.csv")
        analytical = result.bars.copy()
        analytical["raw_close"] = result.bars["close"]
        if "adj_close" in analytical.columns and analytical["adj_close"].notna().any():
            analytical["close"] = analytical["adj_close"].where(analytical["adj_close"].notna(), analytical["close"])
        add_indicators(analytical).to_csv(raw_path, index_label="timestamp")
        output.with_name(f"{safe_ticker}_metadata.json").write_text(
            json.dumps({"provenance": snapshot.provenance.model_dump(mode="json"), "limitations": snapshot.limitations}, indent=2),
            encoding="utf-8",
        )
    print(json.dumps({"ticker": args.ticker.upper(), "data_mode": snapshot.provenance.data_mode, "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
