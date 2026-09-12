from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


LABELS = ("correct", "partially_correct", "hallucinated")


def create_manual_review_template(output: str | Path, example_ids: list[str]) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [{"example_id": example_id, "label": "", "notes": "", "reviewer": ""} for example_id in example_ids[:10]]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["example_id", "label", "notes", "reviewer"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def validate_manual_review(path: str | Path) -> dict[str, Any]:
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    invalid = [row["example_id"] for row in rows if row.get("label") not in LABELS]
    counts = {label: sum(row.get("label") == label for row in rows) for label in LABELS}
    hallucination_rate = counts["hallucinated"] / len(rows) if rows else None
    return {"required_rows": 10, "rows": len(rows), "complete": len(rows) >= 10 and not invalid, "invalid_example_ids": invalid, "label_counts": counts, "hallucination_rate": hallucination_rate}


def write_manual_review_status(output: str | Path, review: dict[str, Any] | None = None) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = review or {"status": "not_run", "reason": "Candidate manual labelling is required after model evaluation"}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
