from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class LoRASettings:
    r: int
    alpha: int
    dropout: float
    target_modules: list[str]


@dataclass(frozen=True)
class TrainingSettings:
    learning_rate: float
    epochs: int
    per_device_batch_size: int
    gradient_accumulation_steps: int
    weight_decay: float
    lr_scheduler_type: str
    warmup_fraction: float
    gradient_checkpointing: bool
    logging_steps: int


@dataclass(frozen=True)
class DatasetSettings:
    source: str
    path: str | None
    instruction_field: str
    context_field: str
    response_field: str


@dataclass(frozen=True)
class QuantizationSettings:
    mode: str


@dataclass(frozen=True)
class ExperimentConfig:
    model_name: str
    dataset_name: str
    dataset: DatasetSettings
    quantization: QuantizationSettings
    seed: int
    num_train_samples: int
    max_seq_length: int
    lora: LoRASettings
    training: TrainingSettings
    generation: dict[str, Any]
    output_dir: str
    evaluation_prompts: list[str]


def load_config(path: str | Path) -> ExperimentConfig:
    with Path(path).open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    dataset_raw = raw.get("dataset", {})
    source = str(dataset_raw.get("source", "huggingface"))
    dataset_name = str(raw.get("dataset_name", dataset_raw.get("name", "")))
    quantization_raw = raw.get("quantization", {})

    return ExperimentConfig(
        model_name=raw["model_name"],
        dataset_name=dataset_name,
        dataset=DatasetSettings(
            source=source,
            path=dataset_raw.get("path"),
            instruction_field=str(dataset_raw.get("instruction_field", "instruction")),
            context_field=str(dataset_raw.get("context_field", "context")),
            response_field=str(dataset_raw.get("response_field", "response")),
        ),
        quantization=QuantizationSettings(
            mode=str(quantization_raw.get("mode", "none")).lower(),
        ),
        seed=int(raw["seed"]),
        num_train_samples=int(raw["num_train_samples"]),
        max_seq_length=int(raw["max_seq_length"]),
        lora=LoRASettings(
            r=int(raw["lora"]["r"]),
            alpha=int(raw["lora"]["alpha"]),
            dropout=float(raw["lora"]["dropout"]),
            target_modules=list(raw["lora"]["target_modules"]),
        ),
        training=TrainingSettings(
            learning_rate=float(raw["training"]["learning_rate"]),
            epochs=int(raw["training"]["epochs"]),
            per_device_batch_size=int(raw["training"]["per_device_batch_size"]),
            gradient_accumulation_steps=int(raw["training"]["gradient_accumulation_steps"]),
            weight_decay=float(raw["training"]["weight_decay"]),
            lr_scheduler_type=str(raw["training"]["lr_scheduler_type"]),
            warmup_fraction=float(raw["training"]["warmup_fraction"]),
            gradient_checkpointing=bool(raw["training"]["gradient_checkpointing"]),
            logging_steps=int(raw["training"]["logging_steps"]),
        ),
        generation=dict(raw["generation"]),
        output_dir=str(raw["output_dir"]),
        evaluation_prompts=list(raw["evaluation_prompts"]),
    )
