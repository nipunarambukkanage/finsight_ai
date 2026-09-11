# Task 2 - Filing Risk Extraction Fine-Tuning

[![Open Task 2 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nipunarambukkanage/finsight_ai/blob/main/task2_genai/notebooks/task2_filing_risk_qlora.ipynb)

The Colab link above points to the public repository on the `main` branch. Use
a free T4 or L4 runtime, keep the cell outputs and loss history visible, and
commit the generated artifacts after the run.

The domain task is evidence-linked risk extraction from SEC-style filing excerpts. The student must return a `FilingRiskOutput` JSON object, quote only exact excerpt text, preserve document identity, and abstain when evidence is insufficient.

The submission notebook generates 200 accepted examples, reports prompt/topic diversity and an 80/10/10 source-disjoint split, trains QLoRA on `Qwen/Qwen2.5-1.5B-Instruct`, logs epoch losses, merges the adapter, and compares base versus fine-tuned outputs on the same held-out examples. The model card and loss history belong under `artifacts/` after a real Colab run.

For teacher execution, set `GROQ_API_KEY` in Colab Secrets, instantiate `GroqTeacher`, run `await teacher.health_check()`, and retain that response before calling `generate_dataset(..., teacher=teacher)`. The adapter records the exact model and available rate-limit headers; it does not hide quota or capability failures behind fixture data.

Offline smoke dataset generation is explicit fixture mode. It is useful for testing contracts and does not count as teacher-model execution evidence.

The notebook reloads the base and merged checkpoints with greedy decoding,
computes ROUGE-L, BERTScore (or explicitly labelled offline fallback), JSON
validity, quotation/evidence grounding, abstention, and hallucination rate,
then writes `artifacts/evaluation.json`. The optional `src/rag_fallback.py` adapter keeps ChromaDB isolated from the
fine-tuning result. Select its confidence threshold on validation data, then
report before/after examples separately from the student-model metrics.

```bash
pip install -r ../requirements-training.txt
python -c "import asyncio,sys; sys.path.insert(0,'..'); from task2_genai.src.dataset import generate_dataset; print(asyncio.run(generate_dataset(200))[1])"
```
