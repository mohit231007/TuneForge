from __future__ import annotations

from pathlib import Path

from datasets import Dataset, load_dataset

from tuneforge.config import ExperimentConfig


def format_dolly_to_chat(example: dict) -> dict:
    return format_instruction_example(
        example,
        instruction_field="instruction",
        context_field="context",
        response_field="response",
    )


def format_instruction_example(
    example: dict,
    instruction_field: str,
    context_field: str,
    response_field: str,
) -> dict:
    instruction = str(example[instruction_field]).strip()
    context = example.get(context_field) or ""
    context = str(context).strip()
    response = str(example[response_field]).strip()

    user_content = f"{instruction}\n{context}" if context else instruction

    return {
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": response},
        ]
    }


def _load_source(config: ExperimentConfig) -> Dataset:
    if config.dataset.source == "local":
        if not config.dataset.path:
            raise ValueError("Local dataset source requires dataset.path.")

        path = Path(config.dataset.path)
        suffix = path.suffix.lower()

        if suffix in {".json", ".jsonl"}:
            return load_dataset("json", data_files=str(path), split="train")
        if suffix == ".csv":
            return load_dataset("csv", data_files=str(path), split="train")

        raise ValueError("Supported local dataset formats are .json, .jsonl, and .csv.")

    if not config.dataset_name:
        raise ValueError("Hugging Face dataset source requires dataset_name.")

    return load_dataset(config.dataset_name, split="train")


def prepare_dataset(config: ExperimentConfig) -> Dataset:
    dataset = _load_source(config)

    required = {
        config.dataset.instruction_field,
        config.dataset.response_field,
    }
    missing = required - set(dataset.column_names)
    if missing:
        raise ValueError(f"Dataset is missing required fields: {sorted(missing)}")

    subset_size = min(config.num_train_samples, len(dataset))
    subset = dataset.shuffle(seed=config.seed).select(range(subset_size))

    return subset.map(
        lambda example: format_instruction_example(
            example,
            instruction_field=config.dataset.instruction_field,
            context_field=config.dataset.context_field,
            response_field=config.dataset.response_field,
        )
    )


def prepare_dolly_dataset(dataset_name: str, num_samples: int, seed: int) -> Dataset:
    dataset = load_dataset(dataset_name, split="train")
    subset_size = min(num_samples, len(dataset))
    subset = dataset.shuffle(seed=seed).select(range(subset_size))
    return subset.map(format_dolly_to_chat)
