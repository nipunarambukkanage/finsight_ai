"""Assessment trace format required by Task 3C."""

from __future__ import annotations

import time
import uuid
import json
from pathlib import Path
from typing import Any, Callable

from .contracts import ToolCallRecord


class TraceLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.artifact_dir = self.path.parent / "tool_outputs"
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def call(self, agent: str, tool: str, arguments: dict[str, Any], fn: Callable[[], Any]) -> Any:
        trace_id = f"trace-{uuid.uuid4().hex[:12]}"
        started = time.perf_counter()
        try:
            output = fn()
            status = "ok"
            preview = str(output)[:200]
        except Exception as exc:
            output = {"error": str(exc)}
            status = "error"
            preview = str(output)[:200]
        artifact = self.artifact_dir / f"{trace_id}.json"
        try:
            artifact.write_text(json.dumps(output, default=str, indent=2), encoding="utf-8")
            try:
                artifact_ref = str(artifact.relative_to(Path.cwd()))
            except ValueError:
                artifact_ref = str(artifact)
        except (OSError, TypeError):
            artifact_ref = None
        record = ToolCallRecord(trace_id=trace_id, agent=agent, tool=tool, arguments=arguments,
                                output_preview=preview, output_artifact=artifact_ref,
                                duration_ms=round((time.perf_counter() - started) * 1000, 3), status=status)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(record.model_dump_json() + "\n")
        if status == "error":
            raise RuntimeError(preview)
        return output
