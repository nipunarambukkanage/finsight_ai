"""Durable workflow run metadata and replayable events.

SQLite is the zero-configuration adapter for local/demo deployments. The same
repository contract is intentionally narrow so a PostgreSQL implementation can
be swapped in without changing API routes or graph nodes.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _envelope(run_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Versioned event envelope shared by SQLite and the future Kafka adapter."""
    return {
        "schema_version": "1.0",
        "event_id": f"evt-{uuid.uuid4().hex[:16]}",
        "trace_id": f"trace-{uuid.uuid4().hex[:12]}",
        "run_id": run_id,
        "event_type": event_type,
        "payload": payload,
        "occurred_at": _utc(),
    }


class RunRepository:
    def __init__(self, path: str | Path = "data/run_state.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                run_id TEXT PRIMARY KEY,
                ticker TEXT NOT NULL,
                workflow_kind TEXT NOT NULL,
                status TEXT NOT NULL,
                idempotency_key TEXT UNIQUE,
                payload_json TEXT NOT NULL,
                lease_owner TEXT,
                lease_expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS workflow_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(run_id) REFERENCES workflow_runs(run_id)
            );
            CREATE INDEX IF NOT EXISTS idx_workflow_events_run ON workflow_events(run_id, sequence);
            CREATE TABLE IF NOT EXISTS outbox_events (
                event_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                attempts INTEGER NOT NULL DEFAULT 0,
                available_at TEXT NOT NULL,
                published_at TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_outbox_pending ON outbox_events(status, available_at);
            """)



            columns = {row[1] for row in db.execute("PRAGMA table_info(workflow_runs)").fetchall()}
            if "lease_owner" not in columns:
                db.execute("ALTER TABLE workflow_runs ADD COLUMN lease_owner TEXT")
            if "lease_expires_at" not in columns:
                db.execute("ALTER TABLE workflow_runs ADD COLUMN lease_expires_at TEXT")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def create(self, ticker: str, workflow_kind: str = "research", payload: Optional[dict[str, Any]] = None, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        with self._lock, self._connect() as db:
            if idempotency_key:
                existing = db.execute("SELECT * FROM workflow_runs WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
                if existing:
                    return self._row(existing)
            run_id = f"run-{uuid.uuid4().hex[:16]}"
            now = _utc()
            row = {"run_id": run_id, "ticker": ticker.strip().upper(), "workflow_kind": workflow_kind, "status": "QUEUED", "idempotency_key": idempotency_key, "payload": payload or {}, "created_at": now, "updated_at": now}
            db.execute("INSERT INTO workflow_runs(run_id, ticker, workflow_kind, status, idempotency_key, payload_json, lease_owner, lease_expires_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (run_id, row["ticker"], workflow_kind, "QUEUED", idempotency_key, json.dumps(row["payload"], default=str), None, None, now, now))
            envelope = _envelope(run_id, "run.created", row)
            db.execute("INSERT INTO workflow_events(run_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)", (run_id, "run.created", json.dumps(envelope, default=str), now))
            self._insert_outbox(db, run_id, "run.created", envelope, now)
            return row

    def get(self, run_id: str) -> Optional[dict[str, Any]]:
        with self._lock, self._connect() as db:
            row = db.execute("SELECT * FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone()
            return self._row(row) if row else None

    def update(self, run_id: str, status: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        with self._lock, self._connect() as db:
            now = _utc()
            current = db.execute("SELECT payload_json FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone()
            if current is None:
                raise KeyError(run_id)
            merged = json.loads(current["payload_json"])
            merged.update(payload or {})
            terminal = status in {"COMPLETED", "FAILED", "CANCELLED"}
            db.execute("UPDATE workflow_runs SET status = ?, payload_json = ?, lease_owner = CASE WHEN ? THEN NULL ELSE lease_owner END, lease_expires_at = CASE WHEN ? THEN NULL ELSE lease_expires_at END, updated_at = ? WHERE run_id = ?", (status, json.dumps(merged, default=str), terminal, terminal, now, run_id))
            event_type = f"run.{status.lower()}"
            envelope = _envelope(run_id, event_type, {"status": status, "payload": merged})
            db.execute("INSERT INTO workflow_events(run_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)", (run_id, event_type, json.dumps(envelope, default=str), now))
            self._insert_outbox(db, run_id, event_type, envelope, now)
            row = db.execute("SELECT * FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone()
            return self._row(row)

    def claim(self, run_id: str, worker_id: str, lease_seconds: int = 30) -> Optional[dict[str, Any]]:
        """Atomically acquire or reclaim a queued/failed/running run lease."""
        with self._lock, self._connect() as db:
            now = datetime.now(timezone.utc)
            now_text = now.isoformat()
            expiry = (now.timestamp() + lease_seconds)
            expiry_text = datetime.fromtimestamp(expiry, tz=timezone.utc).isoformat()
            cursor = db.execute(
                "UPDATE workflow_runs SET status = 'RUNNING', lease_owner = ?, lease_expires_at = ?, updated_at = ? "
                "WHERE run_id = ? AND status IN ('QUEUED', 'FAILED', 'RUNNING') AND (lease_expires_at IS NULL OR lease_expires_at <= ?)",
                (worker_id, expiry_text, now_text, run_id, now_text),
            )
            if cursor.rowcount != 1:
                return None
            event_type = "run.claimed"
            envelope = _envelope(run_id, event_type, {"worker_id": worker_id, "lease_expires_at": expiry_text})
            db.execute("INSERT INTO workflow_events(run_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)", (run_id, event_type, json.dumps(envelope, default=str), now_text))
            self._insert_outbox(db, run_id, event_type, envelope, now_text)
            row = db.execute("SELECT * FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone()
            return self._row(row) if row else None

    def renew(self, run_id: str, worker_id: str, lease_seconds: int = 30) -> bool:
        """Extend a worker lease only when the caller still owns it."""
        expiry = datetime.fromtimestamp(datetime.now(timezone.utc).timestamp() + lease_seconds, tz=timezone.utc).isoformat()
        with self._lock, self._connect() as db:
            cursor = db.execute("UPDATE workflow_runs SET lease_expires_at = ?, updated_at = ? WHERE run_id = ? AND lease_owner = ? AND status = 'RUNNING'", (expiry, _utc(), run_id, worker_id))
            return cursor.rowcount == 1

    def append_event(self, run_id: str, event_type: str, payload: dict[str, Any]) -> None:
        with self._lock, self._connect() as db:
            if db.execute("SELECT 1 FROM workflow_runs WHERE run_id = ?", (run_id,)).fetchone() is None:
                raise KeyError(run_id)
            now = _utc()
            envelope = _envelope(run_id, event_type, payload)
            db.execute("INSERT INTO workflow_events(run_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)", (run_id, event_type, json.dumps(envelope, default=str), now))
            self._insert_outbox(db, run_id, event_type, envelope, now)

    @staticmethod
    def _insert_outbox(db: sqlite3.Connection, run_id: str, topic: str, payload: dict[str, Any], now: str) -> None:
        db.execute(
            "INSERT INTO outbox_events(event_id, run_id, topic, payload_json, status, attempts, available_at, created_at) VALUES (?, ?, ?, ?, 'PENDING', 0, ?, ?)",
            (payload["event_id"], run_id, topic, json.dumps(payload, default=str), now, now),
        )

    def pending_outbox(self, limit: int = 100) -> list[dict[str, Any]]:
        """Read pending integration events; publishing is handled by a worker."""
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT * FROM outbox_events WHERE status = 'PENDING' AND available_at <= ? ORDER BY created_at LIMIT ?", (_utc(), limit)).fetchall()
            return [{"event_id": row["event_id"], "run_id": row["run_id"], "topic": row["topic"], "payload": json.loads(row["payload_json"]), "attempts": row["attempts"], "created_at": row["created_at"]} for row in rows]

    def mark_outbox(self, event_id: str, *, published: bool, retry_after_seconds: int = 30) -> bool:
        """Acknowledge or defer an integration event without losing its envelope."""
        with self._lock, self._connect() as db:
            if published:
                cursor = db.execute("UPDATE outbox_events SET status = 'PUBLISHED', published_at = ? WHERE event_id = ? AND status = 'PENDING'", (_utc(), event_id))
            else:
                available = datetime.fromtimestamp(datetime.now(timezone.utc).timestamp() + retry_after_seconds, tz=timezone.utc).isoformat()
                cursor = db.execute("UPDATE outbox_events SET attempts = attempts + 1, available_at = ? WHERE event_id = ? AND status = 'PENDING'", (available, event_id))
            return cursor.rowcount == 1

    def events(self, run_id: str, after: int = 0) -> list[dict[str, Any]]:
        with self._lock, self._connect() as db:
            rows = db.execute("SELECT sequence, event_type, payload_json, created_at FROM workflow_events WHERE run_id = ? AND sequence > ? ORDER BY sequence", (run_id, after)).fetchall()
            return [{"id": row["sequence"], "event": row["event_type"], "data": json.loads(row["payload_json"]), "created_at": row["created_at"]} for row in rows]

    @staticmethod
    def _row(row: sqlite3.Row) -> dict[str, Any]:
        return {"run_id": row["run_id"], "ticker": row["ticker"], "workflow_kind": row["workflow_kind"], "status": row["status"], "idempotency_key": row["idempotency_key"], "payload": json.loads(row["payload_json"]), "lease_owner": row["lease_owner"], "lease_expires_at": row["lease_expires_at"], "created_at": row["created_at"], "updated_at": row["updated_at"]}


run_repository = RunRepository()
