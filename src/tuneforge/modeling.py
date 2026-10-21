from __future__ import annotations

import torch
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from tuneforge.config import ExperimentConfig


def load_tokenizer(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return tokenizer


def select_precision() -> dict[str, bool]:
    """Return mixed-precision flags that are safe for the active CUDA device."""
    if not torch.cuda.is_available():
        return {"fp16": False, "bf16": False}

    major, _minor = torch.cuda.get_device_capability(0)
    if major >= 8:
        return {"fp16": False, "bf16": True}
    return {"fp16": True, "bf16": False}


def load_base_model(model_name: str, quantization_mode: str = "none"):
    mode = quantization_mode.lower()

    if mode not in {"none", "4bit"}:
        raise ValueError(f"Unsupported quantization mode: {mode}")

    if mode == "4bit":
        if not torch.cuda.is_available():
            raise RuntimeError("QLoRA 4-bit loading requires a CUDA GPU.")

        major, _minor = torch.cuda.get_device_capability(0)
        compute_dtype = torch.bfloat16 if major >= 8 else torch.float16

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=compute_dtype,
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quant_config,
            device_map="auto",
        )
        return prepare_model_for_kbit_training(model)

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    kwargs = {"dtype": dtype}
    if torch.cuda.is_available():
        kwargs["device_map"] = "auto"

    return AutoModelForCausalLM.from_pretrained(model_name, **kwargs)


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
