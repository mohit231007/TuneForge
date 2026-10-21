from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import torch
import yaml

from tuneforge.execution_backend import get_execution_backend

REGISTRY_DIR = Path("studio_runs")
REGISTRY_DIR.mkdir(exist_ok=True)

TERMINAL_STATUSES = {"completed", "failed", "cancelled"}
RUN_STATUSES = {"ready", "queued", "running", "completed", "failed", "cancelled"}


@dataclass
class StudioRun:
    run_id: str
    workspace_id: str
    status: str
    config_path: str
    created_at: str
    updated_at: str
    worker_id: str | None = None
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


def create_run(
    payload: dict,
    launch: bool = False,
    workspace_id: str = "default",
) -> StudioRun:
    errors = validate_experiment(payload)
    if errors:
        raise ValueError(" ".join(errors))

    run_id = f"TF-{uuid.uuid4().hex[:8].upper()}"
    run_dir = REGISTRY_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    payload = dict(payload)
    payload["workspace_id"] = workspace_id
    payload["output_dir"] = str(run_dir / "artifacts")

    config_path = run_dir / "experiment.yaml"
    config_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )

    now = datetime.now(timezone.utc).isoformat()
    status = "ready"
    message = "Experiment created."

    if launch:
        get_execution_backend().submit(run_id, str(config_path))
        status = "queued"
        message = "Experiment queued for a TuneForge worker."

    run = StudioRun(
        run_id=run_id,
        workspace_id=workspace_id,
        status=status,
        config_path=str(config_path),
        created_at=now,
        updated_at=now,
        worker_id=None,
        message=message,
    )
    _save_run(run)
    return run


def _run_path(run_id: str) -> Path:
    return REGISTRY_DIR / run_id / "run.json"


def _save_run(run: StudioRun) -> None:
    _run_path(run.run_id).write_text(
        json.dumps(asdict(run), indent=2),
        encoding="utf-8",
    )


def get_run(run_id: str) -> StudioRun:
    path = _run_path(run_id)

    if not path.exists():
        raise FileNotFoundError(run_id)

    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("workspace_id", "default")
    data.setdefault("updated_at", data.get("created_at"))
    data.setdefault("worker_id", None)
    data.pop("pid", None)

    run = StudioRun(**data)

    artifact_metadata = REGISTRY_DIR / run_id / "artifacts" / "run_metadata.json"
    if run.status == "running" and artifact_metadata.exists():
        run.status = "completed"
        run.message = "Training completed and metadata was generated."
        run.updated_at = datetime.now(timezone.utc).isoformat()
        _save_run(run)

    return run


def set_run_status(
    run_id: str,
    status: str,
    message: str,
    worker_id: str | None = None,
) -> StudioRun:
    if status not in RUN_STATUSES:
        raise ValueError(f"Unsupported run status: {status}")

    run = get_run(run_id)
    run.status = status
    run.message = message
    run.updated_at = datetime.now(timezone.utc).isoformat()

    if worker_id is not None:
        run.worker_id = worker_id

    _save_run(run)
    return run


def cancel_run(run_id: str) -> StudioRun:
    run = get_run(run_id)

    if run.status in TERMINAL_STATUSES:
        raise ValueError(f"Cannot cancel a {run.status} run.")

    if run.status == "running":
        raise ValueError(
            "Running jobs require worker-level cancellation; "
            "this version only cancels queued/ready jobs safely."
        )

    get_execution_backend().cancel(run_id)
    return set_run_status(run_id, "cancelled", "Run cancelled before execution.")


def retry_run(run_id: str) -> StudioRun:
    run = get_run(run_id)

    if run.status not in {"failed", "cancelled"}:
        raise ValueError("Only failed or cancelled runs can be retried.")

    get_execution_backend().retry(run_id, run.config_path)
    return set_run_status(
        run_id,
        "queued",
        "Run re-queued for another worker attempt.",
        worker_id=None,
    )


def list_runs(workspace_id: str | None = None) -> list[StudioRun]:
    runs: list[StudioRun] = []

    for path in REGISTRY_DIR.glob("TF-*/run.json"):
        try:
            run = get_run(path.parent.name)
            if workspace_id is None or run.workspace_id == workspace_id:
                runs.append(run)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
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

    lines = path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    return lines[-max_lines:]
