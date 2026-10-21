from __future__ import annotations

from datasets import Dataset, load_dataset


def format_dolly_to_chat(example: dict) -> dict:
    """Convert one Dolly record into user/assistant chat messages."""
    instruction = str(example["instruction"]).strip()
    context = example.get("context") or ""
    context = str(context).strip()
    response = str(example["response"]).strip()

    user_content = f"{instruction}\n{context}" if context else instruction

    return {
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": response},
        ]
    }


def prepare_dolly_dataset(
    dataset_name: str,
    num_samples: int,
    seed: int,
) -> Dataset:
    """Load Dolly, shuffle deterministically, select a subset, and add chat messages."""
    dataset = load_dataset(dataset_name, split="train")
    subset_size = min(num_samples, len(dataset))
    subset = dataset.shuffle(seed=seed).select(range(subset_size))
    return subset.map(format_dolly_to_chat)
