"""Observation-driven single and two-agent LangGraph-compatible workflows."""

from __future__ import annotations

import time
import re
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

from .contracts import ClarificationRequest, ClarificationResponse, DataBrief, ResearchBrief, RiskEvidence
from .tools import AgentRole, AuthorizedTools
from .tracing import TraceLogger


class RunBudget:
    def __init__(self, deadline_seconds: float = 180.0, max_tools: int = 12, max_model_calls: int = 10):
        self.started = time.monotonic()
        self.deadline_seconds, self.max_tools, self.max_model_calls = deadline_seconds, max_tools, max_model_calls
        self.tool_calls = 0
        self.model_calls = 0

    def consume_tool(self) -> None:
        self.tool_calls += 1
        if self.tool_calls > self.max_tools or time.monotonic() - self.started > self.deadline_seconds:
            raise TimeoutError("assessment run budget exhausted")

    def consume_model(self) -> None:
        self.model_calls += 1
        if self.model_calls > self.max_model_calls or time.monotonic() - self.started > self.deadline_seconds:
            raise TimeoutError("assessment model-call budget exhausted")


def _config_fingerprint(mode: str) -> str:
    config = {"mode": mode, "groq": bool(os.getenv("GROQ_API_KEY")), "openrouter": bool(os.getenv("OPENROUTER_API_KEY")), "search": "ddgs"}
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]


def _cache_path(cache_dir: str | Path, ticker: str, mode: str = "live", workflow: str = "single") -> Path:
    safe_ticker = re.sub(r"[^A-Z0-9._-]", "_", ticker.upper())
    config_hash = _config_fingerprint(mode)
    return Path(cache_dir) / f"{safe_ticker}-{workflow}-{mode}-{config_hash}-{datetime.now(timezone.utc).date().isoformat()}.json"


def _data_brief(ticker: str, tools: AuthorizedTools, budget: RunBudget) -> DataBrief:
    budget.consume_tool()
    prices = tools.get_price_data(ticker, "2y")
    budget.consume_tool()
    vol = tools.calculate_volatility(ticker, 20)

    return DataBrief(ticker=ticker.upper(), current_price=prices.get("current_price"), period="2y",
                     annualized_volatility=vol.get("annualized_volatility"), limitations=prices.get("limitations", []),
                     source=prices.get("data_mode", "unknown"))


def _choose_next_action(observation: dict[str, Any], completed: set[str]) -> str | None:
    """Planner decision is based on observed fields, not a fixed call list."""
    if "price" not in observation:
        return "price"
    if observation.get("volatility") is None and "volatility" not in completed:
        return "volatility"
    if "news" not in observation:
        return "news"
    if "sentiment" not in observation:
        return "sentiment"


    if observation.get("volatility", 0) and observation["volatility"] > 0.35 and "web" not in observation:
        return "web"
    if "web" not in observation:
        return "web"
    return None


def run_single_research(ticker: str = "AAPL", trace_path: str | Path = "logs/agent_trace.jsonl", cache_dir: str | Path = "artifacts/cache", *, allow_demo_fallback: bool = False) -> ResearchBrief:
    cache = _cache_path(cache_dir, ticker, "demo" if allow_demo_fallback else "live", "single")
    if cache.exists():
        loaded = ResearchBrief.model_validate_json(cache.read_text(encoding="utf-8"))
        return loaded.model_copy(update={"cached": True})
    trace = TraceLogger(trace_path)
    tools = AuthorizedTools(AgentRole.SINGLE_RESEARCH, trace, allow_demo_fallback=allow_demo_fallback)
    budget = RunBudget()
    observation: dict[str, Any] = {}
    completed: set[str] = set()
    incomplete = False
    try:
        while (action := _choose_next_action(observation, completed)) is not None:
            if action == "price":
                budget.consume_tool(); observation["price"] = tools.get_price_data(ticker, "2y")
            elif action == "volatility":
                budget.consume_tool(); observation["volatility"] = tools.calculate_volatility(ticker, 20).get("annualized_volatility")
            elif action == "sentiment":
                headlines = [item["headline"] for item in observation.get("news", [])]
                budget.consume_model(); budget.consume_tool(); observation["sentiment"] = tools.llm_sentiment(headlines)
            elif action == "news":
                budget.consume_tool(); observation["news"] = tools.get_news(ticker, 10)
            elif action == "web":
                budget.consume_tool(); observation["web"] = tools.web_search(f"{ticker} analyst risks next 90 days")
            completed.add(action)
    except TimeoutError:
        incomplete = True
    prices, volatility, sentiment = observation.get("price", {}), observation.get("volatility"), observation.get("sentiment", {})
    news = observation.get("news", [])
    web = observation.get("web", [])
    risks = [RiskEvidence(title="Market volatility", evidence=f"Annualized {volatility:.1%}" if volatility is not None else "Volatility unavailable", severity="high" if (volatility or 0) > .35 else "medium"),
             RiskEvidence(title="Company and sector news", evidence=(news[0].get("headline") if news else "No live headline returned"), source_url=(news[0].get("url") if news else None)),
             RiskEvidence(title="External commentary", evidence=(web[0].get("snippet") if web else "No external commentary returned"), source_url=(web[0].get("url") if web else None))]
    limitations = list(prices.get("limitations", []))
    recovery = []
    if prices.get("data_mode") == "unavailable":
        recovery.append("price-provider failure observed; planner continued and preserved an unavailable limitation")
    if sentiment.get("provider") == "unavailable":
        recovery.append("sentiment-provider failure observed; clarification completed with an unavailable score")
    if web and web[0].get("title") == "Search unavailable":
        recovery.append("web-search failure observed; report retained an explicit evidence limitation")
    if incomplete:
        limitations.append("Run deadline or model/tool budget exhausted; report contains collected evidence only.")
    brief = ResearchBrief(ticker=ticker.upper(), generated_at=datetime.now(timezone.utc).isoformat(),
                          financial_health_summary=f"{ticker.upper()} last price {prices.get('current_price', 'N/A')}; annualized volatility {volatility if volatility is not None else 'N/A'}; news sentiment {sentiment.get('label', 'neutral')}.",
                          top_three_risks=risks, hedge_strategy_recommendation="Consider a defined-risk protective put or collar sized from the portfolio's risk budget; position size must be determined by a licensed professional.",
                          data_brief=DataBrief(ticker=ticker.upper(), current_price=prices.get("current_price"), period="2y", annualized_volatility=volatility, sentiment_score=sentiment.get("overall_score"), sentiment_label=sentiment.get("label"), limitations=limitations, source=prices.get("data_mode", "unknown")), limitations=limitations, incomplete=incomplete,
                          run_metadata={"workflow": "single_research", "data_mode": prices.get("data_mode", "unknown"), "freshness": datetime.now(timezone.utc).isoformat(), "config_fingerprint": _config_fingerprint("demo" if allow_demo_fallback else "live"), "recovery": recovery, "budget": {"max_seconds": budget.deadline_seconds, "max_tools": budget.max_tools, "max_model_calls": budget.max_model_calls, "used_tools": budget.tool_calls, "used_model_calls": budget.model_calls}})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    return brief


def run_two_agent_research(ticker: str = "AAPL", trace_path: str | Path = "logs/agent_trace.jsonl", cache_dir: str | Path = "artifacts/cache", *, allow_demo_fallback: bool = False) -> ResearchBrief:
    cache = _cache_path(cache_dir, ticker, "demo" if allow_demo_fallback else "live", "two-agent")
    if cache.exists():
        loaded = ResearchBrief.model_validate_json(cache.read_text(encoding="utf-8"))
        return loaded.model_copy(update={"cached": True})
    trace = TraceLogger(trace_path)
    budget = RunBudget()
    data_tools = AuthorizedTools(AgentRole.DATA_ANALYST, trace, allow_demo_fallback=allow_demo_fallback)
    writer_tools = AuthorizedTools(AgentRole.RESEARCH_WRITER, trace, allow_demo_fallback=allow_demo_fallback)
    incomplete = False
    limitations: list[str] = []
    news: list[dict[str, Any]] = []
    web: list[dict[str, Any]] = []


    try:
        data_brief = _data_brief(ticker, data_tools, budget)
    except TimeoutError as exc:
        incomplete = True
        limitations.append(str(exc))
        data_brief = DataBrief(ticker=ticker.upper(), period="2y", source="unavailable", limitations=[str(exc)])
    handoffs = [{"from": "data_analyst", "to": "research_writer", "schema": "DataBrief", "payload": data_brief.model_dump()}]
    try:
        budget.consume_tool(); news = writer_tools.get_news(ticker, 10)
        budget.consume_tool(); web = writer_tools.web_search(f"{ticker} analyst commentary risks 90 days")
    except TimeoutError as exc:
        incomplete = True
        limitations.append(str(exc))



    handed_headlines = [item.get("headline", "") for item in news]
    request = ClarificationRequest(question="Please score the headlines and confirm volatility/data mode for risk calibration.", requested_fields=["headlines", "annualized_volatility", "source"], headlines=handed_headlines)
    sentiment: dict[str, Any] = {}
    try:
        budget.consume_tool()
        budget.consume_model()
        sentiment = data_tools.llm_sentiment(handed_headlines)
        data_brief = data_brief.model_copy(update={"sentiment_score": sentiment.get("overall_score"), "sentiment_label": sentiment.get("label")})
    except TimeoutError as exc:
        incomplete = True
        limitations.append(str(exc))
    response = ClarificationResponse(request=request, answer={"annualized_volatility": data_brief.annualized_volatility, "source": data_brief.source, "sentiment": sentiment, "headline_count": len(handed_headlines)}, source="Data Analyst sentiment tool over Writer-provided headlines; no news call")
    handoffs.extend([{ "from": "research_writer", "to": "data_analyst", "schema": "ClarificationRequest", "payload": request.model_dump()}, {"from": "data_analyst", "to": "research_writer", "schema": "ClarificationResponse", "payload": response.model_dump()}])
    risks = [RiskEvidence(title="Headline risk", evidence=(news[0].get("headline") if news else "No live headline returned"), source_url=(news[0].get("url") if news else None)),
             RiskEvidence(title="Analyst commentary risk", evidence=(web[0].get("snippet") if web else "No external commentary returned"), source_url=(web[0].get("url") if web else None)),
             RiskEvidence(title="Observed volatility", evidence=f"Annualized volatility {data_brief.annualized_volatility:.1%}" if data_brief.annualized_volatility is not None else "Volatility unavailable")]
    all_limitations = [*data_brief.limitations, *limitations]
    if incomplete:
        all_limitations.append("Run deadline or model/tool budget exhausted; report contains collected evidence only.")
    recovery = []
    if data_brief.source == "unavailable":
        recovery.append("data-provider failure was handed off as a typed limitation")
    if sentiment.get("provider") == "unavailable":
        recovery.append("sentiment-provider failure was answered during the single clarification cycle")
    if web and web[0].get("title") == "Search unavailable":
        recovery.append("web-search failure was retained as an explicit writer limitation")
    brief = ResearchBrief(ticker=ticker.upper(), generated_at=datetime.now(timezone.utc).isoformat(), financial_health_summary=f"Data Analyst reports price {data_brief.current_price or 'N/A'}, volatility {data_brief.annualized_volatility or 'N/A'}, and {data_brief.sentiment_label or 'unavailable'} sentiment.", top_three_risks=risks, hedge_strategy_recommendation="Use a defined-risk collar or protective put only after validating option liquidity and portfolio exposure; this system does not execute trades.", data_brief=data_brief, handoff_trace=handoffs, limitations=all_limitations, incomplete=incomplete, run_metadata={"workflow": "two_agent_research", "data_mode": data_brief.source, "freshness": datetime.now(timezone.utc).isoformat(), "config_fingerprint": _config_fingerprint("demo" if allow_demo_fallback else "live"), "recovery": recovery, "budget": {"max_seconds": budget.deadline_seconds, "max_tools": budget.max_tools, "max_model_calls": budget.max_model_calls, "used_tools": budget.tool_calls, "used_model_calls": budget.model_calls}})
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    return brief


def run_two_agent_research_langgraph(
    ticker: str = "AAPL",
    trace_path: str | Path = "logs/agent_trace.jsonl",
    cache_dir: str | Path = "artifacts/cache",
    *,
    allow_demo_fallback: bool = False,
) -> ResearchBrief:
    """Execute the coordinated handoff through a compiled LangGraph boundary."""
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError("Install langgraph to run the coordinated assessment graph") from exc

    class State(TypedDict, total=False):
        ticker: str
        trace_path: str
        cache_dir: str
        result: dict[str, Any]

    graph = StateGraph(State)

    def execute(state: State) -> State:
        result = run_two_agent_research(
            state["ticker"], state["trace_path"], state["cache_dir"],
            allow_demo_fallback=allow_demo_fallback,
        )
        return {"result": result.model_dump(mode="json")}

    graph.add_node("coordinated_research", execute)
    graph.add_edge(START, "coordinated_research")
    graph.add_edge("coordinated_research", END)
    final = graph.compile().invoke({"ticker": ticker, "trace_path": str(trace_path), "cache_dir": str(cache_dir)})
    return ResearchBrief.model_validate(final["result"])


def build_langgraph():
    """Return a small LangGraph planner graph when LangGraph is installed."""
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError("Install langgraph to build the assessment graph") from exc
    class State(TypedDict, total=False):
        ticker: str
        observation: dict[str, Any]
        completed: list[str]
        done: bool
    graph = StateGraph(State)
    def planner(state: State) -> State:
        action = _choose_next_action(state.get("observation", {}), set(state.get("completed", [])))
        return {"done": action is None, "observation": {**state.get("observation", {}), "next_action": action}}
    def observe(state: State) -> State:
        action = state.get("observation", {}).get("next_action")
        observation = dict(state.get("observation", {}))
        if action:
            observation[action] = {"observed": True} if action in {"price", "news", "web", "sentiment"} else 0.2
            observation.pop("next_action", None)
        return {"completed": [*state.get("completed", []), action] if action else state.get("completed", []), "observation": observation}
    def route(state: State) -> str:
        return "finish" if state.get("done") else "observe"
    graph.add_node("planner", planner); graph.add_node("observe", observe)
    graph.add_edge(START, "planner"); graph.add_conditional_edges("planner", route, {"observe": "observe", "finish": END}); graph.add_edge("observe", "planner")
    return graph.compile()


def run_single_research_langgraph(ticker: str = "AAPL", trace_path: str | Path = "logs/agent_trace.jsonl", cache_dir: str | Path = "artifacts/cache", *, allow_demo_fallback: bool = False) -> ResearchBrief:
    """Execute the assessment researcher through a LangGraph run boundary.

    The autonomous planner/tool loop remains a pure application function so it
    is testable without a server; LangGraph supplies the explicit run state and
    future checkpoint integration point.
    """
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError("Install langgraph to run the assessment graph") from exc
    class State(TypedDict, total=False):
        ticker: str
        trace_path: str
        cache_dir: str
        result: dict[str, Any]
    graph = StateGraph(State)
    def execute(state: State) -> State:
        result = run_single_research(state["ticker"], state["trace_path"], state["cache_dir"], allow_demo_fallback=allow_demo_fallback)
        return {"result": result.model_dump(mode="json")}
    graph.add_node("autonomous_research", execute)
    graph.add_edge(START, "autonomous_research")
    graph.add_edge("autonomous_research", END)
    final = graph.compile().invoke({"ticker": ticker, "trace_path": str(trace_path), "cache_dir": str(cache_dir)})
    return ResearchBrief.model_validate(final["result"])
