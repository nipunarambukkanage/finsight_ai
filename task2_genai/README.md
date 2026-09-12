# Task 2 - Filing Risk Extraction Fine-Tuning

[![Open Task 2 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nipunarambukkanage/finsight_ai/blob/main/task2_genai/notebooks/task2_filing_risk_qlora.ipynb)

The Colab link above points to the public repository on the `main` branch. Use
a free T4 or L4 runtime, keep the cell outputs and loss history visible, and
commit the generated artifacts after the run.

## Current evidence status

The repository contains the complete, reproducible pipeline and honest
not-run templates. The live assessment evidence is created only when the
notebook completes with a teacher provider and a CUDA GPU. The checked-in
templates do not claim a teacher dataset, GPU loss history, merged weights, or
evaluation scores.

| Evidence | File written by the live run | Requirement |
| --- | --- | --- |
| Teacher capability and quota check | `artifacts/teacher_preflight.json` | Provider/model recorded before generation |
| 200-example dataset | `artifacts/dataset/dataset_manifest.json` plus three JSONL files | 160/20/20 source-disjoint groups |
| Training configuration and losses | `artifacts/training_config.json`, `artifacts/loss_history.json` | NF4 QLoRA, per-epoch validation |
| GPU and OOM record | `artifacts/training_preflight.json`, `artifacts/oom_experiment.json` | Hardware and memory evidence |
| Merged model | `artifacts/merged_model_manifest.json`, `artifacts/qlora/merged/` | Clean reload before publication |
| Evaluation | `artifacts/evaluation.json` | ROUGE-L, BERTScore, JSON, grounding, abstention |
| Manual review | `artifacts/manual_review.csv`, `artifacts/manual_review.json` | Ten labelled outputs and hallucination rate |
| Optional RAG bonus | `artifacts/rag_threshold.json`, `artifacts/rag_before_after.json` | Validation-selected Chroma threshold |

The domain task is evidence-linked risk extraction from SEC-style filing excerpts. The student must return a `FilingRiskOutput` JSON object, quote only exact excerpt text, preserve document identity, and abstain when evidence is insufficient.

The submission notebook generates 200 accepted examples from twenty source-document groups, reports prompt/topic diversity and an 80/10/10 source-disjoint split, trains QLoRA on `Qwen/Qwen2.5-1.5B-Instruct`, logs epoch losses, merges the adapter, and compares base versus fine-tuned outputs on the same held-out examples. The model card and loss history belong under `artifacts/` after a real Colab run.

For teacher execution, set `GROQ_API_KEY` in Colab Secrets, instantiate `GroqTeacher`, run `await teacher.health_check()`, and retain that response before calling `generate_dataset(..., teacher=teacher)`. The adapter records the exact model and available rate-limit headers; it does not hide quota or capability failures behind fixture data.

Offline smoke dataset generation is explicit fixture mode. It is useful for testing contracts and does not count as teacher-model execution evidence.

## Run the pipeline

For a local contract smoke run:

```bash
python task2_genai/run_task2.py --mode fixture
```

For the assessment run in Colab:

1. Open the Colab badge above and choose **Runtime → Change runtime type → T4 GPU**.
2. Run `!pip install -r requirements-training.txt` from the repository root.
3. Add `GROQ_API_KEY` to Colab Secrets. Do not paste keys into notebook cells.
4. Set `USE_FIXTURE = False` and run every cell from top to bottom.
5. Stop if the teacher preflight is unavailable. The pipeline never turns a provider failure into fixture evidence.
6. Check that the dataset manifest says `count: 200` and split sizes are `160`, `20`, and `20`.
7. Keep the three epoch losses, peak GPU memory, and merged reload result visible.
8. Label ten rows in `artifacts/manual_review.csv` as `correct`, `partially_correct`, or `hallucinated`.
9. Review `MODEL_CARD.md`, remove private traces, then upload the merged checkpoint to a Hugging Face repository if desired.

The orchestration command is also available in Colab:

```bash
python task2_genai/run_task2.py --mode live
```

The command fails closed when the provider or GPU is unavailable. It returns
an updated `run_manifest.json` with the blocked phase and reason.

The notebook reloads the base and merged checkpoints with greedy decoding,
computes ROUGE-L, BERTScore (or explicitly labelled offline fallback), JSON
validity, quotation/evidence grounding, abstention, and hallucination rate,
then writes `artifacts/evaluation.json`. The optional `src/rag_fallback.py` adapter keeps ChromaDB isolated from the
fine-tuning result. Select its confidence threshold on validation data, then
report before/after examples separately from the student-model metrics.

## Hugging Face publication checklist

The model upload is intentionally separate from training. After a successful
run, verify `merged_model_manifest.json`, confirm `reload_verified`, include
the dataset hash and evaluation results in `MODEL_CARD.md`, and publish only
the merged model and tokenizer. The browser login does not automatically make
a local CLI token available; use a Colab secret or an explicit Hugging Face
token when you perform the upload.

```bash
pip install -r ../requirements-training.txt
python -c "import asyncio,sys; sys.path.insert(0,'..'); from task2_genai.src.dataset import generate_dataset; print(asyncio.run(generate_dataset(200))[1])"
```
