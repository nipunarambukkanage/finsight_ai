"""Optional ChromaDB fallback for evidence retrieval when the student abstains."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from .contracts import FilingExample, FilingRiskOutput


@dataclass(frozen=True)
class RetrievalDecision:
    output: FilingRiskOutput
    similarity: float
    threshold: float
    used_fallback: bool


def select_confidence_threshold(scores: Iterable[tuple[float, bool]]) -> float:
    """Select the validation threshold that maximizes binary abstention F1."""
    rows = list(scores)
    if not rows:
        return 0.7
    candidates = sorted({round(score, 3) for score, _ in rows})
    best_threshold, best_f1 = candidates[0], -1.0
    for threshold in candidates:
        tp = sum(score >= threshold and relevant for score, relevant in rows)
        fp = sum(score >= threshold and not relevant for score, relevant in rows)
        fn = sum(score < threshold and relevant for score, relevant in rows)
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * precision * recall / max(1e-9, precision + recall)
        if f1 > best_f1:
            best_threshold, best_f1 = threshold, f1
    return best_threshold


def write_threshold_selection(output: str | Path, validation_scores: Iterable[tuple[float, bool]]) -> float:
    scores = list(validation_scores)
    threshold = select_confidence_threshold(scores)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": "completed" if scores else "not_run", "threshold": threshold, "validation_rows": len(scores), "selection": "maximum_binary_abstention_f1"}, indent=2), encoding="utf-8")
    return threshold


def write_before_after_example(output: str | Path, *, before: dict, after: dict, threshold: float) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": "completed", "threshold": threshold, "before_fine_tuning": before, "after_chroma_fallback": after}, indent=2), encoding="utf-8")
    return path


class ChromaRiskFallback:
    """Small, isolated bonus adapter; the main Task 2 result remains fine-tuning-only."""

    def __init__(self, examples: Iterable[FilingExample], collection_name: str = "filing-risk-fallback"):
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("Install chromadb to run the optional RAG fallback") from exc
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)
        self.examples = {example.example_id: example for example in examples}
        if self.examples:
            self.collection.upsert(
                ids=list(self.examples),
                documents=[example.user for example in self.examples.values()],
                metadatas=[{"example_id": example.example_id} for example in self.examples.values()],
            )

    def retrieve(self, excerpt: str, threshold: float = 0.7) -> RetrievalDecision:
        result = self.collection.query(query_texts=[excerpt], n_results=1)
        if not result.get("ids") or not result["ids"][0]:
            return RetrievalDecision(FilingRiskOutput(abstain=True, confidence=0.2), 0.0, threshold, True)
        distance = float(result.get("distances", [[1.0]])[0][0])
        similarity = max(0.0, min(1.0, 1.0 - distance))
        example = self.examples[result["ids"][0][0]]
        if similarity < threshold:
            return RetrievalDecision(FilingRiskOutput(abstain=True, confidence=0.2), similarity, threshold, True)
        return RetrievalDecision(example.assistant, similarity, threshold, True)
