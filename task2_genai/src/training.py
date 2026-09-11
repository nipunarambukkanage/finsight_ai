"""QLoRA training entrypoint. Heavy ML dependencies are loaded only when called."""

from __future__ import annotations

import json
import inspect
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QLoRAConfig:
    base_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    load_in_4bit: bool = True
    quant_type: str = "nf4"
    double_quant: bool = True
    compute_dtype: str = "float16"
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: tuple[str, ...] = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
    learning_rate: float = 2e-4
    scheduler: str = "cosine"
    warmup_ratio: float = 0.05
    epochs: int = 3
    batch_size: int = 1
    gradient_accumulation_steps: int = 16
    max_seq_length: int = 1024
    seed: int = 42


QLORA_RATIONALE = {
    "load_in_4bit": "NF4 keeps a 1.5B student within a free Colab GPU memory budget.",
    "compute_dtype": "FP16 matches the T4 baseline and avoids requiring BF16 hardware.",
    "lora": "Rank 16 with alpha 32 adapts attention and MLP projections without full-model updates.",
    "learning_rate": "2e-4 is a conservative SFT starting point for a small instruction model.",
    "epochs": "Three epochs expose an early stopping/validation deterioration decision.",
    "batching": "Batch one with accumulation 16 provides a stable effective batch on a T4.",
    "max_seq_length": "1,024 tokens covers the excerpt and structured answer while bounding memory.",
    "objective": "Assistant-only loss prevents the model from learning to copy system/user instructions.",
    "reproducibility": "Seed 42 and recorded package/model revisions make the Colab run repeatable.",
}


def write_training_config(output: str | Path, config: QLoRAConfig | None = None) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"config": asdict(config or QLoRAConfig()), "rationale": QLORA_RATIONALE}, indent=2), encoding="utf-8")
    return path


def load_model_for_evaluation(model_path: str, *, dtype: str = "float16") -> tuple[Any, Any]:
    """Load a base or merged checkpoint through one reproducible evaluation path."""
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError("Install requirements-training.txt before loading an evaluation model") from exc
    torch_dtype = torch.float16 if dtype == "float16" else torch.bfloat16
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch_dtype, device_map="auto")
    model.eval()
    return model, tokenizer


def train_qlora(train_file: str, validation_file: str, output_dir: str, config: QLoRAConfig | None = None) -> dict[str, Any]:
    """Run SFT with NF4 QLoRA and save per-epoch losses.

    This function intentionally fails with an actionable message when called
    outside the Colab/training dependency profile.
    """
    cfg = config or QLoRAConfig()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "training_config.json").write_text(json.dumps({"config": asdict(cfg), "rationale": QLORA_RATIONALE}, indent=2), encoding="utf-8")
    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments, Trainer
    except ImportError as exc:
        raise RuntimeError("Install requirements-training.txt in Colab before running QLoRA") from exc
    if not torch.cuda.is_available():
        raise RuntimeError("QLoRA requires a CUDA GPU; use a free Colab T4/L4 runtime")
    dtype = torch.float16 if cfg.compute_dtype == "float16" else torch.bfloat16
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type=cfg.quant_type, bnb_4bit_use_double_quant=cfg.double_quant, bnb_4bit_compute_dtype=dtype)
    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model, use_fast=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(cfg.base_model, quantization_config=quant, device_map="auto")
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(r=cfg.lora_r, lora_alpha=cfg.lora_alpha, lora_dropout=cfg.lora_dropout, target_modules=list(cfg.target_modules), task_type="CAUSAL_LM"))
    dataset = load_dataset("json", data_files={"train": train_file, "validation": validation_file})

    def tokenize(row: dict[str, Any]) -> dict[str, Any]:
        messages = row["messages"]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        prompt_text = tokenizer.apply_chat_template(messages[:-1], tokenize=False, add_generation_prompt=True)
        encoded = tokenizer(text, truncation=True, max_length=cfg.max_seq_length, add_special_tokens=False)
        prompt_ids = tokenizer(prompt_text, truncation=True, max_length=cfg.max_seq_length, add_special_tokens=False)["input_ids"]
        encoded["labels"] = [-100] * min(len(prompt_ids), len(encoded["input_ids"])) + encoded["input_ids"][len(prompt_ids):]
        return encoded

    tokenized = dataset.map(tokenize, remove_columns=dataset["train"].column_names)
    training_kwargs = {"output_dir": output_dir, "learning_rate": cfg.learning_rate, "lr_scheduler_type": cfg.scheduler, "warmup_ratio": cfg.warmup_ratio, "num_train_epochs": cfg.epochs, "per_device_train_batch_size": cfg.batch_size, "gradient_accumulation_steps": cfg.gradient_accumulation_steps, "logging_strategy": "epoch", "save_strategy": "epoch", "fp16": True, "max_grad_norm": 1.0, "optim": "paged_adamw_8bit", "seed": cfg.seed, "report_to": "none"}
    eval_key = "eval_strategy" if "eval_strategy" in inspect.signature(TrainingArguments).parameters else "evaluation_strategy"
    training_kwargs[eval_key] = "epoch"
    args = TrainingArguments(**training_kwargs)
    def collate(features: list[dict[str, Any]]) -> dict[str, Any]:
        max_len = min(cfg.max_seq_length, max(len(row["input_ids"]) for row in features))
        input_ids, attention, labels = [], [], []
        for row in features:
            ids = row["input_ids"][:max_len]; mask = row["attention_mask"][:max_len]; target = row["labels"][:max_len]
            pad = max_len - len(ids)
            input_ids.append(ids + [tokenizer.pad_token_id] * pad); attention.append(mask + [0] * pad); labels.append(target + [-100] * pad)
        return {"input_ids": torch.tensor(input_ids), "attention_mask": torch.tensor(attention), "labels": torch.tensor(labels)}
    trainer = Trainer(model=model, args=args, train_dataset=tokenized["train"], eval_dataset=tokenized["validation"], data_collator=collate)
    try:
        trainer.train()
    except Exception as exc:


        (output_path / "training_failure.json").write_text(
            json.dumps({"error": str(exc), "config": asdict(cfg), "rationale": QLORA_RATIONALE}, indent=2),
            encoding="utf-8",
        )
        raise
    history = trainer.state.log_history
    eval_losses = [float(row["eval_loss"]) for row in history if row.get("eval_loss") is not None]
    metrics = {"log_history": history, "config": asdict(cfg), "rationale": QLORA_RATIONALE,
               "gpu_memory_peak_mb": round(torch.cuda.max_memory_allocated() / (1024 ** 2), 2),
               "best_validation_loss": min(eval_losses) if eval_losses else None,
               "validation_deteriorated": bool(eval_losses and eval_losses[-1] > min(eval_losses))}
    (output_path / "loss_history.json").write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")
    merged = model.merge_and_unload()
    merged_path = output_path / "merged"
    merged.save_pretrained(merged_path, safe_serialization=True)
    tokenizer.save_pretrained(merged_path)


    del merged, model
    torch.cuda.empty_cache()
    reloaded = AutoModelForCausalLM.from_pretrained(merged_path, torch_dtype=dtype, device_map="auto")
    del reloaded
    metrics["merged_reload_verified"] = True
    (output_path / "loss_history.json").write_text(json.dumps(metrics, indent=2, default=str), encoding="utf-8")
    return metrics
