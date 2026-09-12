from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def update_manifest(path: str | Path, *, status: str | None = None, phase: str | None = None, phase_status: str | None = None, artifacts: dict[str, str] | None = None, limitations: list[str] | None = None) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = read_manifest(manifest_path)
    manifest["updated_at"] = utc_now()
    if status:
        manifest["status"] = status
    if phase and phase_status:
        manifest.setdefault("phases", {})[phase] = phase_status
    if artifacts:
        manifest.setdefault("artifacts", {}).update(artifacts)
    if limitations:
        manifest.setdefault("limitations", []).extend(limitations)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def write_status_artifact(path: str | Path, phase: str, status: str, reason: str | None = None, details: dict[str, Any] | None = None) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {"phase": phase, "status": status, "created_at": utc_now()}
    if reason:
        payload["reason"] = reason
    if details:
        payload["details"] = details
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination
