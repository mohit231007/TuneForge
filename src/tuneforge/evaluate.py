from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel

from tuneforge.config import load_config
from tuneforge.inference import generate_response_with_metrics
from tuneforge.modeling import load_base_model, load_tokenizer
from tuneforge.persistence import save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare base and adapted responses.")
    parser.add_argument("--config", default="configs/tinyllama_dolly.yaml")
    parser.add_argument("--adapter", required=True)
    return parser.parse_args()


def _aggregate(records: list[dict]) -> dict:
    if not records:
        return {}

    keys = [
        "latency_seconds",
        "generated_tokens",
        "tokens_per_second",
        "word_count",
        "repetition_ratio",
    ]

    return {
        key: round(sum(float(record[key]) for record in records) / len(records), 4)
        for key in keys
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    prompts = config.evaluation_prompts
    tokenizer = load_tokenizer(config.model_name)

    base_model = load_base_model(config.model_name)
    base_records = [
        generate_response_with_metrics(
            base_model,
            tokenizer,
            prompt,
            max_new_tokens=int(config.generation["max_new_tokens"]),
        )
        for prompt in prompts
    ]

    del base_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    fresh_base = load_base_model(config.model_name)
    adapted_model = PeftModel.from_pretrained(fresh_base, args.adapter)

    adapted_records = [
        generate_response_with_metrics(
            adapted_model,
            tokenizer,
            prompt,
            max_new_tokens=int(config.generation["max_new_tokens"]),
        )
        for prompt in prompts
    ]

    comparisons = []

    for prompt, baseline, adapted in zip(
        prompts,
        base_records,
        adapted_records,
    ):
        comparisons.append(
            {
                "prompt": prompt,
                "baseline_response": baseline["response"],
                "adapted_response": adapted["response"],
                "baseline_metrics": {
                    key: value
                    for key, value in baseline.items()
                    if key != "response"
                },
                "adapted_metrics": {
                    key: value
                    for key, value in adapted.items()
                    if key != "response"
                },
            }
        )

    scorecard = {
        "baseline_average": _aggregate(base_records),
        "adapted_average": _aggregate(adapted_records),
        "prompt_count": len(prompts),
        "generation_is_deterministic": True,
    }

    output_dir = Path(config.output_dir) / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "scorecard": scorecard,
        "comparisons": comparisons,
    }

    save_json(payload, output_dir / "comparison.json")

    flat_rows = []
    for item in comparisons:
        row = {
            "prompt": item["prompt"],
            "baseline_response": item["baseline_response"],
            "adapted_response": item["adapted_response"],
        }
        for key, value in item["baseline_metrics"].items():
            row[f"baseline_{key}"] = value
        for key, value in item["adapted_metrics"].items():
            row[f"adapted_{key}"] = value
        flat_rows.append(row)

    pd.DataFrame(flat_rows).to_csv(
        output_dir / "comparison.csv",
        index=False,
    )

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
