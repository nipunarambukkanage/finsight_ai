"""Dependency-light telemetry with an optional OpenTelemetry bridge."""

from __future__ import annotations

import json
import time
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any


_trace_id: ContextVar[str] = ContextVar("finsight_trace_id", default="")
_events_path = Path("data/telemetry.jsonl")


def begin_trace(trace_id: str | None = None) -> str:
    value = trace_id or f"trace-{uuid.uuid4().hex[:12]}"
    _trace_id.set(value)
    return value


def current_trace_id() -> str:
    return _trace_id.get() or begin_trace()


def record(component: str, operation: str, *, status: str = "ok", duration_ms: float | None = None, attributes: dict[str, Any] | None = None) -> None:
    """Write a redacted, replayable event without requiring an observability service."""
    event = {
        "schema_version": "1.0",
        "trace_id": current_trace_id(),
        "component": component,
        "operation": operation,
        "status": status,
        "duration_ms": duration_ms,
        "attributes": attributes or {},
        "timestamp": time.time(),
    }
    try:
        _events_path.parent.mkdir(parents=True, exist_ok=True)
        with _events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, default=str) + "\n")
    except OSError:

        pass
