from __future__ import annotations

import json
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import torch
import yaml

REGISTRY_DIR = Path("studio_runs")
REGISTRY_DIR.mkdir(exist_ok=True)


@dataclass
class StudioRun:
    run_id: str
    status: str
    config_path: str
    created_at: str
    pid: int | None = None
    message: str | None = None


def hardware_capabilities() -> dict:
    if not torch.cuda.is_available():
        return {
            "cuda_available": False,
            "gpu_name": None,
            "compute_capability": None,
            "recommended_precision": "fp32",
            "can_train": False,
        }

    major, minor = torch.cuda.get_device_capability(0)

    return {
        "cuda_available": True,
        "gpu_name": torch.cuda.get_device_name(0),
        "compute_capability": f"{major}.{minor}",
        "recommended_precision": "bf16" if major >= 8 else "fp16",
        "can_train": True,
    }


def validate_experiment(payload: dict) -> list[str]:
    errors: list[str] = []

    if not payload.get("model_name"):
        errors.append("model_name is required.")
    if payload.get("num_train_samples", 0) <= 0:
        errors.append("num_train_samples must be > 0.")
    if payload.get("max_seq_length", 0) <= 0:
        errors.append("max_seq_length must be > 0.")

    lora = payload.get("lora", {})
    if lora.get("r", 0) <= 0:
        errors.append("LoRA rank must be > 0.")
    if lora.get("alpha", 0) <= 0:
        errors.append("LoRA alpha must be > 0.")
    if not lora.get("target_modules"):
        errors.append("At least one LoRA target module is required.")

    training = payload.get("training", {})
    if training.get("per_device_batch_size", 0) <= 0:
        errors.append("Batch size must be > 0.")
    if training.get("gradient_accumulation_steps", 0) <= 0:
        errors.append("Gradient accumulation must be > 0.")

    dataset = payload.get("dataset", {})
    if dataset.get("source", "huggingface") == "local" and not dataset.get("path"):
        errors.append("Local dataset source requires a path.")

    quantization = payload.get("quantization", {})
    quantization_mode = str(quantization.get("mode", "none")).lower()
    if quantization_mode not in {"none", "4bit"}:
        errors.append("quantization.mode must be either 'none' or '4bit'.")

    return errors


def create_run(payload: dict, launch: bool = False) -> StudioRun:
    errors = validate_experiment(payload)
    if errors:
        raise ValueError(" ".join(errors))

    run_id = f"TF-{uuid.uuid4().hex[:8].upper()}"
    run_dir = REGISTRY_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    payload = dict(payload)
    payload["output_dir"] = str(run_dir / "artifacts")

    config_path = run_dir / "experiment.yaml"
    config_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    status = "ready"
    pid = None
    message = "Experiment created."

    if launch:
        hardware = hardware_capabilities()

        if not hardware["can_train"]:
            status = "blocked"
            message = (
                "No CUDA GPU detected on the TuneForge host; "
                "the config was saved but training was not launched."
            )
        else:
            log_handle = (run_dir / "train.log").open("w", encoding="utf-8")
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "tuneforge.train",
                    "--config",
                    str(config_path),
                ],
                stdout=log_handle,
                stderr=subprocess.STDOUT,
            )
            status = "running"
            pid = process.pid
            message = "Training process launched."

    run = StudioRun(
        run_id=run_id,
        status=status,
        config_path=str(config_path),
        created_at=datetime.now(timezone.utc).isoformat(),
        pid=pid,
        message=message,
    )
    _save_run(run)
    return run


def _save_run(run: StudioRun) -> None:
    path = REGISTRY_DIR / run.run_id / "run.json"
    path.write_text(json.dumps(asdict(run), indent=2), encoding="utf-8")


def get_run(run_id: str) -> StudioRun:
    path = REGISTRY_DIR / run_id / "run.json"

    if not path.exists():
        raise FileNotFoundError(run_id)

    data = json.loads(path.read_text(encoding="utf-8"))
    run = StudioRun(**data)

    if run.status == "running":
        artifact_metadata = REGISTRY_DIR / run_id / "artifacts" / "run_metadata.json"

        if artifact_metadata.exists():
            run.status = "completed"
            run.message = "Training completed and metadata was generated."
            _save_run(run)

    return run


def list_runs() -> list[StudioRun]:
    runs: list[StudioRun] = []

    for path in REGISTRY_DIR.glob("TF-*/run.json"):
        try:
            runs.append(get_run(path.parent.name))
        except Exception:
            continue

    return sorted(runs, key=lambda run: run.created_at, reverse=True)


def read_telemetry(run_id: str) -> list[dict]:
    path = REGISTRY_DIR / run_id / "artifacts" / "telemetry.jsonl"

    if not path.exists():
        return []

    points: list[dict] = []

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                points.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return points


def read_training_log(run_id: str, max_lines: int = 200) -> list[str]:
    path = REGISTRY_DIR / run_id / "train.log"

    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-max_lines:]
