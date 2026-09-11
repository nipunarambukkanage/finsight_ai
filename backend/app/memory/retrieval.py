"""
FinSight AI - Memory Retrieval & Deduplication
Performs relevance-based semantic retrieval, deduplication, and memory versioning.
"""

from typing import List, Optional
import hashlib
import numpy as np
from backend.app.memory.models import MemoryItemDTO, MemoryCategory
from backend.app.rag.embeddings import embedding_service

class MemoryRetrievalEngine:
    @staticmethod
    def compute_content_hash(title: str, content: str) -> str:
        """Compute deterministic SHA-256 hash of memory content."""
        data = f"{title.strip().lower()}||{content.strip().lower()}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def rank_memories(
        query: str,
        memories: List[MemoryItemDTO],
        category: Optional[MemoryCategory] = None,
        top_k: int = 5
    ) -> List[MemoryItemDTO]:
        """Rank memories by semantic relevance to query using vector similarity."""
        if not memories:
            return []


        candidates = [m for m in memories if not category or m.category == category]
        if not candidates:
            return []

        q_vec = np.array(embedding_service.embed([query])[0], dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        texts = [f"{m.title} {m.content}" for m in candidates]
        c_vecs = embedding_service.embed(texts)

        ranked = []
        for i, m in enumerate(candidates):
            v = np.array(c_vecs[i], dtype=np.float32)
            v_norm = np.linalg.norm(v)
            sim = float(np.dot(q_vec, v) / (q_norm * v_norm + 1e-9))

            m_copy = m.model_copy()
            m_copy.relevance_score = round(max(0.0, sim), 4)
            ranked.append(m_copy)

        ranked.sort(key=lambda x: x.relevance_score or 0.0, reverse=True)
        return ranked[:top_k]
