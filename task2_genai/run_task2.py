from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from task2_genai.src.artifacts import update_manifest, write_status_artifact
from task2_genai.src.dataset import generate_dataset, write_dataset_artifacts
from task2_genai.src.model_artifacts import render_model_card, write_merged_manifest
from task2_genai.src.teacher import GroqTeacher
from task2_genai.src.training import write_oom_experiment, write_training_config, write_training_preflight, train_qlora


async def run(mode: str, artifacts: Path) -> dict:
    artifacts.mkdir(parents=True, exist_ok=True)
    manifest_path = artifacts / "run_manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps({"task": "task2_genai", "status": "not_run", "phases": {}, "artifacts": {}}, indent=2), encoding="utf-8")
    teacher = GroqTeacher() if mode == "live" else None
    preflight = await teacher.health_check() if teacher else {"available": False, "reason": "fixture mode selected", "model": "fixture"}
    (artifacts / "teacher_preflight.json").write_text(json.dumps(preflight, indent=2), encoding="utf-8")
    update_manifest(manifest_path, phase="teacher_preflight", phase_status="ready" if preflight.get("available") else "blocked", artifacts={"teacher_preflight": "teacher_preflight.json"}, limitations=[] if preflight.get("available") else [preflight.get("reason", "teacher unavailable")])
    if mode == "live" and not preflight.get("available"):
        update_manifest(manifest_path, status="blocked")
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    examples, metadata = await generate_dataset(200, teacher=teacher)
    dataset_paths = write_dataset_artifacts(examples, metadata, artifacts / "dataset")
    update_manifest(manifest_path, phase="dataset_generation", phase_status="complete" if metadata.get("complete") else "incomplete", artifacts={key: str(Path(value).relative_to(artifacts)) for key, value in dataset_paths.items()})
    write_training_config(artifacts / "training_config.json")
    preflight_path = write_training_preflight(artifacts / "training_preflight.json")
    write_oom_experiment(artifacts / "oom_experiment.json")
    update_manifest(manifest_path, phase="qlora_training", phase_status="ready" if json.loads(preflight_path.read_text(encoding="utf-8")).get("ready") else "blocked", artifacts={"training_preflight": "training_preflight.json", "oom_experiment": "oom_experiment.json"})
    if mode != "live":
        update_manifest(manifest_path, status="smoke_complete")
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    metrics = train_qlora(str(artifacts / "dataset" / "train.jsonl"), str(artifacts / "dataset" / "validation.jsonl"), str(artifacts / "training"))
    (artifacts / "loss_history.json").write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")
    merged_manifest = write_merged_manifest(artifacts / "merged_model_manifest.json", artifacts / "training" / "merged")
    render_model_card(artifacts / "MODEL_CARD.md", metrics)
    update_manifest(manifest_path, status="complete", phase="qlora_training", phase_status="complete", artifacts={"loss_history": "loss_history.json", "merged_model_manifest": merged_manifest.name, "model_card": "MODEL_CARD.md"})
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Task 2 in fixture smoke or live teacher/GPU mode")
    parser.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--artifacts", default=str(Path(__file__).parent / "artifacts"))
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.mode, Path(args.artifacts))), indent=2))


if __name__ == "__main__":
    main()
