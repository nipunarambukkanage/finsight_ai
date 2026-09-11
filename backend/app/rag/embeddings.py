"""Embedding adapter with an explicit local fallback for zero-credential demos."""

from __future__ import annotations

import hashlib
import os
from typing import Iterable

import numpy as np
from backend.app.config import settings


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._attempted = False
        self.mode = "uninitialized"

    @staticmethod
    def _synthetic_allowed() -> bool:
        configured = os.getenv("FINSIGHT_ALLOW_SYNTHETIC_EMBEDDINGS")
        if configured is not None:
            return configured.lower() == "true"
        return os.getenv("DEMO_MODE", str(settings.DEMO_MODE)).lower() == "true"

    def _load(self):
        if self._model is not None or self._attempted:
            return self._model
        self._attempted = True


        if os.getenv("FINSIGHT_ENABLE_LOCAL_EMBEDDINGS", "false").lower() != "true":
            if not self._synthetic_allowed():
                self.mode = "unavailable"
                return None
            self.mode = "deterministic-demo-fallback"
            return None
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self.mode = "sentence-transformers"
        except Exception:
            self.mode = "deterministic-demo-fallback" if self._synthetic_allowed() else "unavailable"
        return self._model

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        rows = list(texts)
        model = self._load()
        if model is not None:
            return model.encode(rows, normalize_embeddings=True).tolist()
        if self.mode == "unavailable":
            raise RuntimeError("Sentence Transformer embeddings are not provisioned; enable local embeddings or explicit demo mode")
        vectors = []
        for text in rows:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
            vector = rng.normal(size=384).astype(np.float32)
            vector /= np.linalg.norm(vector) or 1.0
            vectors.append(vector.tolist())
        return vectors


embedding_service = EmbeddingService()
