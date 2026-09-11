# Filing Risk Extractor (QLoRA)

This file is a template to complete after the Colab training run. Record the
base-model revision, dataset hash, training configuration, per-epoch training
and validation losses, evaluation metrics, known limitations, and the public
merged-model URL. Do not publish tokens or private filing content.

Base model: `Qwen/Qwen2.5-1.5B-Instruct` (Apache-2.0)
Task: evidence-linked risk extraction with abstention
Data splits: 160 train / 20 validation / 20 test, source-disjoint
Promotion rule: improve held-out quality without reducing evidence grounding

