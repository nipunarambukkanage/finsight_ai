import asyncio
import json

from task2_genai.src.contracts import FilingRiskOutput, RiskItem
from task2_genai.src.dataset import generate_dataset, split_source_disjoint, validate_example
from task2_genai.src.manual_review import validate_manual_review
from task2_genai.src.rag_fallback import select_confidence_threshold
from task2_genai.src.training import QLoRAConfig


def test_contract_rejects_wrong_document_reference():
    output = FilingRiskOutput(risks=[RiskItem(category="liquidity", explanation="x", supporting_quote="Cash", document_id="wrong")], confidence=0.8)
    example = asyncio.run(generate_dataset(100))[0][0].model_copy(update={"assistant": output})
    valid, errors = validate_example(example)
    assert not valid
    assert any("document id" in error for error in errors)


def test_teacher_path_uses_twenty_source_groups():
    async def teacher(system: str, user: str) -> str:
        source_id = user.splitlines()[0].replace("Document: ", "")
        quote = user.split("Filing excerpt:\n", 1)[1].split("\n\nTask:", 1)[0]
        topic = "insufficient_evidence" if "no quantified" in quote or "does not identify" in quote else "liquidity"
        if topic == "insufficient_evidence":
            return json.dumps({"risks": [], "abstain": True, "confidence": 0.4})
        return json.dumps({"risks": [{"category": "liquidity", "explanation": "Exposure is described.", "supporting_quote": quote, "document_id": source_id, "abstain": False}], "abstain": False, "confidence": 0.8})

    examples, metadata = asyncio.run(generate_dataset(200, teacher=teacher))
    assert metadata["mode"] == "teacher"
    assert metadata["count"] == 200
    splits = split_source_disjoint(examples)
    assert {name: len(rows) for name, rows in splits.items()} == {"train": 160, "validation": 20, "test": 20}
    assert not (set(x.source_document_id for x in splits["train"]) & set(x.source_document_id for x in splits["validation"]))


def test_threshold_selection_and_training_defaults():
    assert select_confidence_threshold([(0.9, True), (0.2, False)]) == 0.9
    assert QLoRAConfig().max_seq_length == 1024


def test_manual_review_requires_ten_rows(tmp_path):
    path = tmp_path / "review.csv"
    path.write_text("example_id,label,notes,reviewer\nex-1,correct,,candidate\n", encoding="utf-8")
    assert validate_manual_review(path)["complete"] is False
