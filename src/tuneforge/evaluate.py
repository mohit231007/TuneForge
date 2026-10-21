from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel

from tuneforge.config import load_config
from tuneforge.inference import generate_many
from tuneforge.modeling import load_base_model, load_tokenizer
from tuneforge.persistence import save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare base and LoRA-adapted responses.")
    parser.add_argument("--config", default="configs/tinyllama_dolly.yaml")
    parser.add_argument("--adapter", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    prompts = config.evaluation_prompts
    tokenizer = load_tokenizer(config.model_name)

    base_model = load_base_model(config.model_name)
    base_responses = generate_many(
        base_model,
        tokenizer,
        prompts,
        max_new_tokens=int(config.generation["max_new_tokens"]),
    )

    del base_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    fresh_base = load_base_model(config.model_name)
    adapted_model = PeftModel.from_pretrained(fresh_base, args.adapter)
    adapted_responses = generate_many(
        adapted_model,
        tokenizer,
        prompts,
        max_new_tokens=int(config.generation["max_new_tokens"]),
    )

    rows = [
        {
            "prompt": prompt,
            "baseline_response": baseline,
            "adapted_response": adapted,
        }
        for prompt, baseline, adapted in zip(prompts, base_responses, adapted_responses)
    ]

    output_dir = Path(config.output_dir) / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    save_json({"comparisons": rows}, output_dir / "comparison.json")
    pd.DataFrame(rows).to_csv(output_dir / "comparison.csv", index=False)

    print(json.dumps({"comparisons": rows}, indent=2))


if __name__ == "__main__":
    main()
