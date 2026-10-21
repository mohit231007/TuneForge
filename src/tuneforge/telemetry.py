from __future__ import annotations

import json
import time
from pathlib import Path

import torch
from transformers import TrainerCallback


class TelemetryCallback(TrainerCallback):
    """Persist training telemetry as JSONL so Studio can render progress."""

    def __init__(self, output_dir: str | Path) -> None:
        self.path = Path(output_dir) / "telemetry.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.started_at = time.time()

    def on_log(self, args, state, control, logs=None, **kwargs):
        logs = logs or {}
        payload = {
            "step": int(state.global_step),
            "epoch": float(state.epoch) if state.epoch is not None else None,
            "elapsed_seconds": round(time.time() - self.started_at, 3),
            "loss": logs.get("loss"),
            "learning_rate": logs.get("learning_rate"),
            "grad_norm": logs.get("grad_norm"),
        }

        if torch.cuda.is_available():
            payload["gpu_allocated_gb"] = round(
                torch.cuda.memory_allocated() / (1024 ** 3),
                4,
            )
            payload["gpu_reserved_gb"] = round(
                torch.cuda.memory_reserved() / (1024 ** 3),
                4,
            )

        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
