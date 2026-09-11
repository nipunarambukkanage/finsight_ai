"""Durable memory adapter used by deployments that outgrow process memory."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class PersistentMemoryStore:
    """SQLite reference adapter; PostgreSQL/pgvector uses the same contract.

    ``content_hash`` and tenant/owner fields are mandatory so deduplication and
    authorization remain storage-independent.
    """
    def __init__(self, path: str | Path = "data/memory.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, owner_id TEXT NOT NULL,
                scope TEXT NOT NULL, category TEXT NOT NULL, content TEXT NOT NULL,
                content_hash TEXT NOT NULL, metadata_json TEXT NOT NULL, valid_from TEXT NOT NULL,
                valid_until TEXT, supersedes_id TEXT, created_at TEXT NOT NULL,
                UNIQUE(tenant_id, content_hash))""")

    def put(self, memory_id: str, tenant_id: str, owner_id: str, scope: str, category: str, content: str, content_hash: str, metadata: Optional[dict[str, Any]] = None, supersedes_id: Optional[str] = None, valid_until: Optional[str] = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path) as db:
            db.execute("""INSERT INTO memories(memory_id, tenant_id, owner_id, scope, category, content, content_hash, metadata_json, valid_from, valid_until, supersedes_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(tenant_id, content_hash) DO UPDATE SET metadata_json=excluded.metadata_json, valid_until=excluded.valid_until, created_at=excluded.created_at""",
                       (memory_id, tenant_id, owner_id, scope, category, content, content_hash, json.dumps(metadata or {}, default=str), now, valid_until, supersedes_id, now))

    def search(self, tenant_id: str, owner_id: str, query: str, limit: int = 5) -> list[dict[str, Any]]:
        terms = [term for term in query.lower().split() if term]
        with sqlite3.connect(self.path) as db:
            db.row_factory = sqlite3.Row
            now = datetime.now(timezone.utc).isoformat()
            rows = db.execute("SELECT * FROM memories WHERE tenant_id = ? AND (owner_id = ? OR scope = 'tenant') AND valid_from <= ? AND (valid_until IS NULL OR valid_until > ?) ORDER BY created_at DESC", (tenant_id, owner_id, now, now)).fetchall()
        ranked = []
        for row in rows:
            haystack = f"{row['category']} {row['content']}".lower()
            score = sum(term in haystack for term in terms) / max(1, len(terms))
            ranked.append({"memory_id": row["memory_id"], "tenant_id": row["tenant_id"], "owner_id": row["owner_id"], "scope": row["scope"], "content": row["content"], "category": row["category"], "metadata": json.loads(row["metadata_json"]), "valid_from": row["valid_from"], "valid_until": row["valid_until"], "score": score})
        return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]

    def all_records(self, tenant_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Return currently valid records for startup hydration and audits."""
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path) as db:
            db.row_factory = sqlite3.Row
            if tenant_id:
                rows = db.execute("SELECT * FROM memories WHERE tenant_id = ? AND valid_from <= ? AND (valid_until IS NULL OR valid_until > ?) ORDER BY created_at", (tenant_id, now, now)).fetchall()
            else:
                rows = db.execute("SELECT * FROM memories WHERE valid_from <= ? AND (valid_until IS NULL OR valid_until > ?) ORDER BY created_at", (now, now)).fetchall()
        return [{"memory_id": row["memory_id"], "tenant_id": row["tenant_id"], "owner_id": row["owner_id"], "scope": row["scope"], "content": row["content"], "category": row["category"], "metadata": json.loads(row["metadata_json"]), "valid_from": row["valid_from"], "valid_until": row["valid_until"], "created_at": row["created_at"]} for row in rows]

    def delete(self, memory_id: str, tenant_id: str, owner_id: str) -> bool:
        """Support tenant-scoped deletion required by retention policies."""
        with sqlite3.connect(self.path) as db:
            cursor = db.execute("DELETE FROM memories WHERE memory_id = ? AND tenant_id = ? AND owner_id = ?", (memory_id, tenant_id, owner_id))
            return cursor.rowcount > 0
