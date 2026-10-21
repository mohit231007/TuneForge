from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tuneforge.adapter_registry import get_adapter
from tuneforge.studio import REGISTRY_DIR, get_run


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def run_metadata(run_id: str) -> dict[str, Any]:
    get_run(run_id)
    path = REGISTRY_DIR / run_id / "artifacts" / "run_metadata.json"
    return _read_json(path)


def compare_runs(left_run_id: str, right_run_id: str) -> dict[str, Any]:
    left = run_metadata(left_run_id)
    right = run_metadata(right_run_id)

    def view(payload: dict[str, Any]) -> dict[str, Any]:
        training = payload.get("training", {})
        parameters = payload.get("parameters", {})
        adapter = payload.get("adapter", {})
        hardware = payload.get("hardware", {})
        config = payload.get("config", {})

        return {
            "model_name": config.get("model_name"),
            "dataset_name": config.get("dataset_name"),
            "quantization_mode": adapter.get("quantization_mode"),
            "training_loss": training.get("training_loss"),
            "global_step": training.get("global_step"),
            "effective_batch_size": training.get("effective_batch_size"),
            "trainable_percentage": parameters.get("trainable_percentage"),
            "adapter_size_bytes": adapter.get("size_bytes"),
            "gpu_name": hardware.get("gpu_name"),
            "precision": hardware.get("precision"),
        }

    left_view = view(left)
    right_view = view(right)

    deltas: dict[str, float | None] = {}
    for key in [
        "training_loss",
        "global_step",
        "effective_batch_size",
        "trainable_percentage",
        "adapter_size_bytes",
    ]:
        left_value = left_view.get(key)
        right_value = right_view.get(key)
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            deltas[key] = right_value - left_value
        else:
            deltas[key] = None

    return {
        "left_run_id": left_run_id,
        "right_run_id": right_run_id,
        "left": left_view,
        "right": right_view,
        "delta_right_minus_left": deltas,
    }


def compare_adapters(left_adapter_id: str, right_adapter_id: str) -> dict[str, Any]:
    left = get_adapter(left_adapter_id)
    right = get_adapter(right_adapter_id)

    def view(payload: dict[str, Any]) -> dict[str, Any]:
        params = payload.get("parameters", {})
        return {
            "adapter_id": payload.get("adapter_id"),
            "model_name": payload.get("model_name"),
            "lifecycle": payload.get("lifecycle"),
            "quantization_mode": payload.get("quantization_mode"),
            "size_bytes": payload.get("size_bytes"),
            "trainable_percentage": params.get("trainable_percentage"),
            "lora": payload.get("lora"),
            "created_at": payload.get("created_at"),
        }

    return {
        "left": view(left),
        "right": view(right),
    }
