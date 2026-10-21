from __future__ import annotations

import argparse
import gc
import json
import math
from dataclasses import asdict
from pathlib import Path

import torch
from trl import SFTConfig, SFTTrainer

from tuneforge.adapter_registry import register_adapter
from tuneforge.config import load_config
from tuneforge.data import prepare_dataset
from tuneforge.modeling import (
    build_lora_config,
    load_base_model,
    load_tokenizer,
    parameter_summary,
    select_precision,
)
from tuneforge.persistence import directory_size_bytes, save_json
from tuneforge.telemetry import TelemetryCallback


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a LoRA or QLoRA adapter with TuneForge.")
    parser.add_argument("--config", default="configs/tinyllama_dolly.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)

    tokenizer = load_tokenizer(config.model_name)
    dataset = prepare_dataset(config)

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    model = load_base_model(
        config.model_name,
        quantization_mode=config.quantization.mode,
    )
    model.config.use_cache = False

    precision = select_precision()
    lora_config = build_lora_config(config)

    effective_batch = (
        config.training.per_device_batch_size
        * config.training.gradient_accumulation_steps
    )
    steps_per_epoch = math.ceil(len(dataset) / effective_batch)
    total_steps = max(1, steps_per_epoch * config.training.epochs)
    warmup_steps = max(1, round(total_steps * config.training.warmup_fraction))

    training_args = SFTConfig(
        output_dir=config.output_dir,
        per_device_train_batch_size=config.training.per_device_batch_size,
        gradient_accumulation_steps=config.training.gradient_accumulation_steps,
        learning_rate=config.training.learning_rate,
        num_train_epochs=config.training.epochs,
        lr_scheduler_type=config.training.lr_scheduler_type,
        warmup_steps=warmup_steps,
        weight_decay=config.training.weight_decay,
        gradient_checkpointing=config.training.gradient_checkpointing,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        fp16=precision["fp16"],
        bf16=precision["bf16"],
        max_length=config.max_seq_length,
        logging_strategy="steps",
        logging_steps=config.training.logging_steps,
        report_to="none",
        save_strategy="no",
        seed=config.seed,
    )

    telemetry = TelemetryCallback(config.output_dir)

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=lora_config,
        callbacks=[telemetry],
    )

    summary = parameter_summary(trainer.model)

    if summary["trainable_percentage"] >= 1.0:
        raise RuntimeError(
            f"Expected <1% trainable parameters, got "
            f"{summary['trainable_percentage']:.4f}%"
        )

    result = trainer.train()

    adapter_dir = Path(config.output_dir) / "final-adapter"
    trainer.model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)

    losses = [
        entry["loss"]
        for entry in trainer.state.log_history
        if "loss" in entry
    ]

    adapter_size = directory_size_bytes(adapter_dir)

    metadata = {
        "config": asdict(config),
        "hardware": {
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": (
                torch.cuda.get_device_name(0)
                if torch.cuda.is_available()
                else None
            ),
            "precision": precision,
        },
        "parameters": summary,
        "training": {
            "global_step": trainer.state.global_step,
            "training_loss": float(result.training_loss),
            "logged_losses": losses,
            "effective_batch_size": effective_batch,
            "warmup_steps": warmup_steps,
        },
        "adapter": {
            "path": str(adapter_dir),
            "size_bytes": adapter_size,
            "quantization_mode": config.quantization.mode,
        },
    }

    adapter_record = register_adapter(
        {
            "workspace_id": config.workspace_id,
            "model_name": config.model_name,
            "adapter_path": str(adapter_dir),
            "size_bytes": adapter_size,
            "quantization_mode": config.quantization.mode,
            "lora": asdict(config.lora),
            "dataset_name": config.dataset_name,
            "parameters": summary,
        }
    )
    metadata["adapter"]["registry"] = adapter_record

    save_json(metadata, Path(config.output_dir) / "run_metadata.json")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
