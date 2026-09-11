"""
FinSight AI - Persistent Memory Service
Provides high-level memory operations: storage, contextual recall, decision audits, and strategy lessons.
"""

from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timezone
from backend.app.memory.models import MemoryItemDTO, MemoryCategory
from backend.app.memory.policies import MemoryPolicyEnforcer
from backend.app.memory.retrieval import MemoryRetrievalEngine
from backend.app.core.logging import logger
from backend.app.memory.persistent import PersistentMemoryStore

class MemoryService:
    def __init__(self):



        self._memory_store: List[MemoryItemDTO] = []
        self._next_id = 1
        self._persistent = PersistentMemoryStore(os.getenv("FINSIGHT_MEMORY_DB", "data/memory.sqlite3"))
        self._hydrate_persistent()
        self._seed_institutional_memory()

    def _hydrate_persistent(self) -> None:
        for row in self._persistent.all_records():
            try:
                category = MemoryCategory(row["category"])
            except ValueError:
                continue
            metadata = dict(row.get("metadata") or {})
            title = str(metadata.pop("title", f"Persisted memory {row['memory_id']}"))
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except (TypeError, ValueError):
                created_at = datetime.now(timezone.utc)
            item = MemoryItemDTO(id=self._next_id, tenant_id=row["tenant_id"], user_id=row["owner_id"], category=category, title=title, content=row["content"], content_hash=row["metadata"].get("content_hash") if isinstance(row.get("metadata"), dict) else None, version=int(metadata.pop("version", 1)), metadata={**metadata, "scope": row.get("scope", "workflow")}, created_at=created_at)
            self._memory_store.append(item)
            self._next_id += 1

    def _seed_institutional_memory(self):
        """Seed baseline institutional research memories and risk policies."""
        seed_items = [
            (
                MemoryCategory.CLIENT_INSTRUCTION,
                "Mandatory Risk Constraint: Max Drawdown 15%",
                "All quantitative strategies generated for institutional accounts must maintain a Maximum Drawdown threshold under 15% across historical backtest periods.",
                {"source": "Investment Committee Guidelines", "active": True}
            ),
            (
                MemoryCategory.STRATEGY_REJECTION,
                "Rejection Lesson: Overfitted High-Frequency RSI on NVDA",
                "Mean reversion RSI(2) on NVDA was rejected due to excessive slippage and turnover (320% annualized), leading to negative net P&L after transaction costs.",
                {"ticker": "NVDA", "turnover": 3.2, "reason": "Slippage friction"}
            ),
            (
                MemoryCategory.STRATEGY_SUCCESS,
                "Approved Strategy: Dual Moving Average Trend on MSFT",
                "20/50 SMA crossover on MSFT achieved Sharpe 1.42 with 8.4% max drawdown and 24% annual turnover under 5 bps execution costs.",
                {"ticker": "MSFT", "sharpe": 1.42, "max_drawdown": 0.084}
            ),
            (
                MemoryCategory.LESSON_LEARNED,
                "Look-Ahead Bias Guardrail",
                "Ensure signals calculated at time t are never backfilled or executed until t+1 market open to prevent look-ahead bias.",
                {"rule": "non_anticipative"}
            )
        ]
        for cat, title, content, meta in seed_items:
            self.store_memory(
                tenant_id="default_tenant",
                user_id="demo_analyst",
                category=cat,
                title=title,
                content=content,
                metadata=meta
            )

    def store_memory(
        self,
        tenant_id: str,
        user_id: str,
        category: MemoryCategory,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        valid_until: Optional[datetime] = None,
    ) -> MemoryItemDTO:
        """Store a new sanitized memory with deduplication and versioning."""
        meta = metadata or {}
        sanitized_content = MemoryPolicyEnforcer.sanitize_and_verify(content, meta)
        content_hash = MemoryRetrievalEngine.compute_content_hash(title, sanitized_content)


        for existing in self._memory_store:
            if existing.content_hash == content_hash and existing.tenant_id == tenant_id:

                existing.version += 1
                existing.metadata.update(meta)
                if valid_until:
                    existing.metadata["valid_until"] = valid_until.isoformat()
                existing.created_at = datetime.now(timezone.utc)
                self._persistent.put(
                    memory_id=str(existing.id), tenant_id=tenant_id, owner_id=existing.user_id,
                    scope=str(existing.metadata.get("scope", "workflow")), category=existing.category.value,
                    content=existing.content, content_hash=content_hash,
                    metadata={**existing.metadata, "title": existing.title, "version": existing.version, "content_hash": content_hash},
                    valid_until=valid_until.isoformat() if valid_until else None,
                )
                logger.info(f"Updated existing memory version {existing.version}: '{title}'")
                return existing

        scope = str(meta.get("scope", "workflow"))
        memory_metadata = {**meta, "scope": scope}
        if valid_until:
            memory_metadata["valid_until"] = valid_until.isoformat()
        item = MemoryItemDTO(
            id=self._next_id,
            tenant_id=tenant_id,
            user_id=user_id,
            category=category,
            title=title,
            content=sanitized_content,
            content_hash=content_hash,
            version=1,
            metadata=memory_metadata,
            created_at=datetime.now(timezone.utc)
        )
        self._next_id += 1
        self._memory_store.append(item)
        self._persistent.put(
            memory_id=str(item.id), tenant_id=tenant_id, owner_id=user_id,
            scope=scope, category=category.value, content=sanitized_content,
            content_hash=content_hash,
            metadata={**meta, "title": title, "version": item.version, "content_hash": content_hash},
            valid_until=valid_until.isoformat() if valid_until else None,
        )
        logger.info(f"Stored institutional memory [{category.value}]: '{title}' (Hash: {content_hash[:8]})")
        return item

    def retrieve_relevant_memories(
        self,
        query: str,
        tenant_id: str = "default_tenant",
        user_id: str = "demo_analyst",
        category: Optional[MemoryCategory] = None,
        top_k: int = 5
    ) -> List[MemoryItemDTO]:
        """Retrieve relevant memories matching query under tenant and user isolation."""
        accessible = [
            m for m in self._memory_store
            if MemoryPolicyEnforcer.verify_tenant_access(tenant_id, m.tenant_id, user_id, m.user_id, str(m.metadata.get("scope", "workflow")))
            and (not m.metadata.get("valid_until") or str(m.metadata["valid_until"]) > datetime.now(timezone.utc).isoformat())
        ]
        return MemoryRetrievalEngine.rank_memories(query, accessible, category=category, top_k=top_k)

    def get_workflow_context(self, ticker: str, tenant_id: str = "default_tenant", user_id: str = "demo_analyst") -> List[Dict[str, Any]]:
        """Retrieve contextual prior memories for a specific ticker research workflow."""
        results = self.retrieve_relevant_memories(
            query=f"{ticker} equity strategy performance risk",
            tenant_id=tenant_id,
            user_id=user_id,
            top_k=4
        )
        return [
            {
                "id": r.id,
                "category": r.category.value,
                "title": r.title,
                "content": r.content,
                "version": r.version,
                "score": r.relevance_score
            }
            for r in results
        ]

    def record_decision(
        self,
        workflow_id: str,
        title: str,
        decision: str,
        rationale: str,
        tenant_id: str = "default_tenant",
        user_id: str = "demo_analyst"
    ) -> MemoryItemDTO:
        """Store an executive human approval or rejection decision for future reference."""
        return self.store_memory(
            tenant_id=tenant_id,
            user_id=user_id,
            category=MemoryCategory.DECISION,
            title=f"Workflow {workflow_id}: {title}",
            content=f"Decision: {decision}. Rationale: {rationale}",
            metadata={"workflow_id": workflow_id, "decision": decision}
        )

    def delete_memory(self, memory_id: int, tenant_id: str, user_id: str) -> bool:
        """Delete a user-owned memory from both the hot cache and durable store."""
        allowed = False
        for item in list(self._memory_store):
            if item.id == memory_id and item.tenant_id == tenant_id and item.user_id == user_id:
                self._memory_store.remove(item)
                allowed = True
                break
        durable = self._persistent.delete(str(memory_id), tenant_id, user_id)
        return allowed or durable

memory_service = MemoryService()
