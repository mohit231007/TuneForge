from __future__ import annotations

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

from tuneforge.config import ExperimentConfig


def load_tokenizer(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return tokenizer


def select_precision() -> dict[str, bool]:
    """Return precision flags that are safe for the active CUDA device."""
    if not torch.cuda.is_available():
        return {"fp16": False, "bf16": False}

    major, _minor = torch.cuda.get_device_capability(0)
    if major >= 8:
        return {"fp16": False, "bf16": True}
    return {"fp16": True, "bf16": False}


def load_base_model(model_name: str):
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    kwargs = {"dtype": dtype}
    if torch.cuda.is_available():
        kwargs["device_map"] = "auto"

    model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)
    return model


def build_lora_config(config: ExperimentConfig) -> LoraConfig:
    return LoraConfig(
        r=config.lora.r,
        lora_alpha=config.lora.alpha,
        lora_dropout=config.lora.dropout,
        target_modules=config.lora.target_modules,
        bias="none",
        task_type="CAUSAL_LM",
    )


def parameter_summary(model) -> dict[str, float | int]:
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return {
        "trainable_parameters": trainable,
        "total_parameters": total,
        "trainable_percentage": (100.0 * trainable / total) if total else 0.0,
    }
