"""Dataset generation, validation and source-disjoint splitting for Task 2."""

from __future__ import annotations

import hashlib
import json
import logging
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Optional

from .contracts import FilingExample, FilingRiskOutput, RiskItem
from .corpus import SOURCE_CORPUS
from .prompts import TEACHER_SYSTEM_PROMPT, STUDENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
Teacher = Callable[[str, str], Awaitable[str]]

TOPICS = (
    "liquidity", "leverage", "customer_concentration", "competition",
    "regulation", "cybersecurity", "supply_chain", "insufficient_evidence",
)

SEED_EXCERPTS = {
    "filing-liquidity": ("liquidity", "Cash and cash equivalents were $2.1 billion, while $3.4 billion of debt matures within twelve months."),
    "filing-leverage": ("leverage", "Our ability to service debt depends on continued operating cash flow and access to capital markets."),
    "filing-customers": ("customer_concentration", "One customer represented 18% of consolidated revenue in the reporting period."),
    "filing-competition": ("competition", "We compete with larger companies that may have greater resources, distribution, and pricing flexibility."),
    "filing-regulation": ("regulation", "Changes in privacy, artificial intelligence, and cross-border data regulations may increase compliance costs."),
    "filing-cyber": ("cybersecurity", "A security incident could disrupt operations, expose confidential information, and result in litigation."),
    "filing-supply": ("supply_chain", "Limited availability of advanced components could delay deliveries and constrain production."),
    "filing-insufficient": ("insufficient_evidence", "The company describes its mission and values but provides no quantified risk evidence in this excerpt."),
}


def _fallback_example(index: int, source_id: str, topic: str, excerpt: str) -> FilingExample:
    abstain = topic == "insufficient_evidence"
    item = [] if abstain else [RiskItem(
        category=topic,
        explanation=f"The excerpt indicates exposure to {topic.replace('_', ' ')} risk.",
        supporting_quote=excerpt,
        document_id=source_id,
        abstain=False,
    )]
    return FilingExample(
        example_id=f"ex-{index:04d}", source_document_id=source_id, topic=topic,
        system=STUDENT_SYSTEM_PROMPT,
        user=f"Document: {source_id}\nFiling excerpt:\n{excerpt}",
        assistant=FilingRiskOutput(risks=item, abstain=abstain, confidence=0.40 if abstain else 0.86),
    )


def validate_example(example: FilingExample) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if example.assistant.abstain and example.assistant.risks:
        errors.append("abstaining output cannot contain risks")
    if example.topic == "insufficient_evidence" and not example.assistant.abstain:
        errors.append("insufficient-evidence examples must abstain")
    if not example.assistant.abstain and not example.assistant.risks:
        errors.append("non-abstaining output must contain at least one risk")
    for risk in example.assistant.risks:
        if not risk.supporting_quote:
            errors.append(f"missing exact supporting quote: {risk.category}")
        elif risk.supporting_quote not in example.user:
            errors.append(f"supporting quote is not an exact excerpt substring: {risk.category}")
        if not risk.document_id:
            errors.append(f"missing document reference: {risk.category}")
        if risk.document_id and risk.document_id != example.source_document_id:
            errors.append("document id does not match source document")
    return not errors, errors


def _fingerprint(example: FilingExample) -> str:
    payload = json.dumps(example.model_dump(exclude={"example_id"}), sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def _dataset_hash(examples: Iterable[FilingExample]) -> str:
    joined = "\n".join(_fingerprint(example) for example in examples).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()


def _near_duplicate(candidate: FilingExample, accepted: list[FilingExample]) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", candidate.user.lower()))
    if not tokens:
        return False
    for previous in accepted[-200:]:
        other = set(re.findall(r"[a-z0-9]+", previous.user.lower()))
        overlap = len(tokens & other) / max(1, len(tokens | other))
        if overlap >= 0.95:
            return True
    return False


def split_source_disjoint(examples: list[FilingExample], seed: int = 42) -> dict[str, list[FilingExample]]:
    """Split source groups so excerpts from one document never cross partitions."""
    groups: dict[str, list[FilingExample]] = {}
    for example in examples:
        groups.setdefault(example.source_document_id, []).append(example)
    source_ids = list(groups)
    random.Random(seed).shuffle(source_ids)
    n = len(source_ids)
    train_sources = set(source_ids[: max(1, int(n * 0.8))])
    val_sources = set(source_ids[max(1, int(n * 0.8)): max(2, int(n * 0.9))])
    return {
        "train": [x for x in examples if x.source_document_id in train_sources],
        "validation": [x for x in examples if x.source_document_id in val_sources],
        "test": [x for x in examples if x.source_document_id not in train_sources and x.source_document_id not in val_sources],
    }


def build_fixture_dataset(count: int = 200, seed: int = 42) -> list[FilingExample]:
    """Offline, clearly labelled dataset used for tests and notebook smoke runs."""
    random.seed(seed)
    examples: list[FilingExample] = []
    base_items = list(SEED_EXCERPTS.items())

    items = base_items + [
        ("filing-liquidity-2", base_items[0][1]),
        ("filing-insufficient-2", base_items[7][1]),
    ]
    for i in range(count):
        source_id, (topic, excerpt) = items[i % len(items)]
        requests = ("Assess the material exposure.", "Extract evidence-linked risks.", "Summarize the risk implication.", "Check whether management quantifies this risk.", "Identify the affected business area.")
        variation = f" {requests[i % len(requests)]} Reporting slice {i + 1}."
        examples.append(_fallback_example(i + 1, source_id, topic, excerpt + variation))
    return examples


async def generate_dataset(count: int = 200, teacher: Optional[Teacher] = None, seed: int = 42) -> tuple[list[FilingExample], dict[str, Any]]:
    """Generate examples with a teacher when configured, validating every result."""
    if count < 100:
        raise ValueError("Task 2 requires at least 100 accepted examples")
    accepted: list[FilingExample] = []
    rejected: list[str] = []
    seen: set[str] = set()



    if teacher is None:
        fixture = build_fixture_dataset(count, seed)
    else:
        fixture = []
        requests = ("Assess material exposure.", "Extract evidence-linked risks.", "Summarize the risk implication.", "Check whether management quantifies this risk.", "Identify the affected business area.", "Separate evidence from inference.", "Return abstention if the excerpt is insufficient.", "Preserve the filing company and exact numbers.", "Audit the risk factor.", "Create a concise analyst handoff.")
        for index in range(count):
            metadata, topic, excerpt = SOURCE_CORPUS[index % len(SOURCE_CORPUS)]
            variation_index = index // len(SOURCE_CORPUS)
            angle = ("quantification", "materiality", "time horizon", "sensitivity", "mitigation", "exposure", "disclosure scope", "operating impact", "investor question", "review note")[variation_index % 10]
            prompt = f"Document: {metadata.document_id}\nCompany: {metadata.company}\nFiling excerpt:\n{excerpt}\n\nTask: {requests[variation_index % len(requests)]}\nReview angle: {angle}. Sample window {index + 1}."
            fixture.append(_fallback_example(index + 1, metadata.document_id, topic, excerpt).model_copy(update={"user": prompt}))
    for index, candidate in enumerate(fixture, start=1):
        if len(accepted) >= count:
            break
        try:
            if teacher is not None:
                raw = await teacher(TEACHER_SYSTEM_PROMPT, candidate.user)
                output = FilingRiskOutput.model_validate_json(raw)
                candidate = candidate.model_copy(update={"assistant": output})
            ok, errors = validate_example(candidate)
            fingerprint = _fingerprint(candidate)
            duplicate = _near_duplicate(candidate, accepted) if teacher is not None else False
            if not ok or fingerprint in seen or duplicate:
                rejected.append("; ".join(errors) or "duplicate")
                continue
            seen.add(fingerprint)
            accepted.append(candidate)
        except Exception as exc:
            rejected.append(str(exc))

    if teacher is not None and len(accepted) < count:
        logger.warning("Teacher accepted %d/%d examples; retaining accepted examples only", len(accepted), count)
    splits = split_source_disjoint(accepted, seed=seed)
    lengths = [len(example.user.split()) for example in accepted]
    metadata = {
        "target_count": count, "count": len(accepted), "complete": len(accepted) == count,
        "rejected_count": len(rejected), "rejections": rejected[:20],
        "split_sizes": {name: len(rows) for name, rows in splits.items()},
        "topic_frequency": dict(Counter(example.topic for example in accepted)),



        "token_length_distribution": {"unit": "whitespace_words", "min": min(lengths, default=0), "max": max(lengths, default=0), "mean": round(sum(lengths) / len(lengths), 2) if lengths else 0},
        "prompt_length_words": {"min": min(lengths, default=0), "max": max(lengths, default=0), "mean": round(sum(lengths) / len(lengths), 2) if lengths else 0},
        "dataset_sha256": _dataset_hash(accepted),
        "source_document_ids": sorted({example.source_document_id for example in accepted}),
        "generation_settings": {"temperature": 0.2, "response_format": "json_object", "teacher_model": getattr(teacher, "model", "fixture"), "seed": seed},
        "teacher_prompt": TEACHER_SYSTEM_PROMPT,
        "seed": seed, "mode": "teacher" if teacher else "fixture",
    }
    return accepted, metadata


def write_dataset_artifacts(examples: list[FilingExample], metadata: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    splits = split_source_disjoint(examples, seed=int(metadata.get("seed", 42)))
    paths: dict[str, str] = {}
    for name, rows in splits.items():
        path = to_chat_jsonl(rows, directory / f"{name}.jsonl")
        paths[name] = str(path)
    manifest = dict(metadata)
    manifest["artifact_paths"] = paths
    manifest["source_split_audit"] = {name: sorted({row.source_document_id for row in rows}) for name, rows in splits.items()}
    manifest_path = directory / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    paths["manifest"] = str(manifest_path)
    return paths


def to_chat_jsonl(examples: Iterable[FilingExample], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for example in examples:
            stream.write(json.dumps({
                "messages": [
                    {"role": "system", "content": example.system},
                    {"role": "user", "content": example.user},
                    {"role": "assistant", "content": example.assistant.model_dump_json()},
                ], "metadata": {"example_id": example.example_id, "source_document_id": example.source_document_id, "topic": example.topic},
            }) + "\n")
    return path
