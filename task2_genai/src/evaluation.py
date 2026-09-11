"""Held-out comparison and grounding metrics."""

from __future__ import annotations

from typing import Any, Iterable
import json
from pathlib import Path

from .contracts import FilingExample, FilingRiskOutput


def generate_model_outputs(model: Any, tokenizer: Any, examples: list[FilingExample], *, max_new_tokens: int = 256) -> list[str]:
    """Generate deterministic held-out responses from a loaded causal model."""
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("Install the training profile before generating model outputs") from exc
    outputs: list[str] = []
    device = next(model.parameters()).device
    for example in examples:
        messages = [{"role": "system", "content": example.system}, {"role": "user", "content": example.user}]
        encoded = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
        if hasattr(encoded, "to"):
            encoded = encoded.to(device)
            generated = model.generate(encoded, max_new_tokens=max_new_tokens, do_sample=False, temperature=0.0)
            prompt_length = encoded.shape[-1]
        else:
            encoded = {key: value.to(device) for key, value in encoded.items()}
            generated = model.generate(**encoded, max_new_tokens=max_new_tokens, do_sample=False)
            prompt_length = encoded["input_ids"].shape[-1]
        outputs.append(tokenizer.decode(generated[0][prompt_length:], skip_special_tokens=True))
    return outputs


def rouge_l_f1(reference: str, prediction: str) -> float:
    ref, pred = reference.split(), prediction.split()
    if not ref or not pred:
        return 0.0
    row = [0] * (len(pred) + 1)
    for token in ref:
        previous = row[:]
        for j, candidate in enumerate(pred, 1):
            row[j] = previous[j - 1] + 1 if token == candidate else max(previous[j], row[j - 1])
    lcs = row[-1]
    precision, recall = lcs / len(pred), lcs / len(ref)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def bertscore_f1(references: list[str], predictions: list[str]) -> tuple[float, str]:
    """Return BERTScore F1 when installed, with an explicit offline fallback."""
    if not references or not predictions:
        return 0.0, "unavailable"
    try:
        from bert_score import score
        _, _, f1 = score(predictions, references, lang="en", verbose=False)
        return float(f1.mean().item()), "bert-score"
    except Exception:


        values = [rouge_l_f1(reference, prediction) for reference, prediction in zip(references, predictions)]
        return sum(values) / max(1, len(values)), "rouge-l-fallback"


def score_grounding(example: FilingExample, output: FilingRiskOutput) -> dict[str, float]:
    expected_quotes = {risk.supporting_quote for risk in example.assistant.risks if risk.supporting_quote}
    actual_quotes = {risk.supporting_quote for risk in output.risks if risk.supporting_quote}
    quote_accuracy = 1.0 if not expected_quotes and not actual_quotes else len(expected_quotes & actual_quotes) / max(1, len(expected_quotes))
    evidence_valid = sum(1 for risk in output.risks if risk.supporting_quote and risk.supporting_quote in example.user) / max(1, len(output.risks))
    abstention = float(output.abstain == example.assistant.abstain)
    hallucinated = sum(1 for risk in output.risks if not risk.supporting_quote or risk.supporting_quote not in example.user or risk.document_id != example.source_document_id)
    hallucination_rate = hallucinated / max(1, len(output.risks))
    return {"quotation_accuracy": quote_accuracy, "evidence_validity": evidence_valid, "abstention_accuracy": abstention, "hallucination_rate": hallucination_rate}


def evaluate_outputs(examples: Iterable[FilingExample], base_outputs: Iterable[FilingRiskOutput], tuned_outputs: Iterable[FilingRiskOutput]) -> dict[str, Any]:
    examples, base_outputs, tuned_outputs = list(examples), list(base_outputs), list(tuned_outputs)
    def coerce(output: FilingRiskOutput | str) -> tuple[FilingRiskOutput | None, float, str]:
        if isinstance(output, FilingRiskOutput):
            return output, 1.0, output.model_dump_json()
        try:
            parsed = FilingRiskOutput.model_validate_json(output)
            return parsed, 1.0, output
        except Exception:
            return None, 0.0, str(output)

    def aggregate(outputs: list[FilingRiskOutput | str]) -> dict[str, float]:
        rows: list[dict[str, float]] = []
        json_validity: list[float] = []
        for example, raw in zip(examples, outputs):
            parsed, valid, _ = coerce(raw)
            json_validity.append(valid)
            rows.append(score_grounding(example, parsed) if parsed is not None else {"quotation_accuracy": 0.0, "evidence_validity": 0.0, "abstention_accuracy": 0.0, "hallucination_rate": 1.0})
        if not rows:
            return {}
        result = {key: round(sum(row[key] for row in rows) / len(rows), 4) for key in rows[0]}
        result["json_validity"] = round(sum(json_validity) / len(json_validity), 4)
        return result
    references = [example.assistant.model_dump_json() for example in examples]
    base_text = [coerce(output)[2] for output in base_outputs]
    tuned_text = [coerce(output)[2] for output in tuned_outputs]
    base_bert, base_bert_backend = bertscore_f1(references, base_text)
    tuned_bert, tuned_bert_backend = bertscore_f1(references, tuned_text)
    return {
        "sample_count": len(examples),
        "rouge_l": {"base": round(sum(rouge_l_f1(a, b) for a, b in zip(references, base_text)) / max(1, len(examples)), 4), "fine_tuned": round(sum(rouge_l_f1(a, b) for a, b in zip(references, tuned_text)) / max(1, len(examples)), 4)},
        "bertscore_f1": {"base": round(base_bert, 4), "fine_tuned": round(tuned_bert, 4), "backend": {"base": base_bert_backend, "fine_tuned": tuned_bert_backend}},
        "base": aggregate(base_outputs), "fine_tuned": aggregate(tuned_outputs),
    }


def evidence_backed_analysis(metrics: dict[str, Any]) -> str:
    """Produce the required two-paragraph comparison from measured metrics."""
    base, tuned = metrics.get("base", {}), metrics.get("fine_tuned", {})
    first = (
        f"On the identical {metrics.get('sample_count', 0)}-example held-out set, the fine-tuned model's JSON validity "
        f"was {tuned.get('json_validity', 0):.1%} versus {base.get('json_validity', 0):.1%} for the prompted base model. "
        f"Evidence validity was {tuned.get('evidence_validity', 0):.1%} versus {base.get('evidence_validity', 0):.1%}, "
        "so the promotion decision must follow measured grounding rather than loss alone."
    )
    second = (
        f"The observed hallucination rate was {tuned.get('hallucination_rate', 0):.1%} for the fine-tuned model and "
        f"{base.get('hallucination_rate', 0):.1%} for the base model, while abstention accuracy was "
        f"{tuned.get('abstention_accuracy', 0):.1%} and {base.get('abstention_accuracy', 0):.1%}, respectively. "
        "These are test-set observations with source-disjoint documents; manual review of at least ten outputs remains required before publishing a model card."
    )
    return f"{first}\n\n{second}"


def write_evaluation(metrics: dict[str, Any], output: str | Path) -> Path:
    """Persist metrics and the required analysis as one reviewable artifact."""
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**metrics, "analysis": evidence_backed_analysis(metrics)}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
