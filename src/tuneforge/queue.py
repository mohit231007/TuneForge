from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

QUEUE_DIR = Path("job_queue")
PENDING_DIR = QUEUE_DIR / "pending"
CLAIMED_DIR = QUEUE_DIR / "claimed"
DONE_DIR = QUEUE_DIR / "done"
FAILED_DIR = QUEUE_DIR / "failed"

for directory in [PENDING_DIR, CLAIMED_DIR, DONE_DIR, FAILED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def _job_path(directory: Path, run_id: str) -> Path:
    return directory / f"{run_id}.json"


def enqueue_job(run_id: str, config_path: str) -> dict[str, Any]:
    payload = {
        "run_id": run_id,
        "config_path": config_path,
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "attempt": 1,
    }
    _job_path(PENDING_DIR, run_id).write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return payload


def claim_next_job(worker_id: str) -> dict[str, Any] | None:
    for pending in sorted(PENDING_DIR.glob("TF-*.json")):
        claimed = CLAIMED_DIR / pending.name
        try:
            pending.rename(claimed)
        except FileNotFoundError:
            continue

        payload = json.loads(claimed.read_text(encoding="utf-8"))
        payload["worker_id"] = worker_id
        payload["claimed_at"] = datetime.now(timezone.utc).isoformat()
        claimed.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    return None


def finish_job(run_id: str, success: bool, details: dict[str, Any] | None = None) -> None:
    source = _job_path(CLAIMED_DIR, run_id)
    destination_dir = DONE_DIR if success else FAILED_DIR
    destination = _job_path(destination_dir, run_id)

    payload: dict[str, Any] = {}
    if source.exists():
        payload = json.loads(source.read_text(encoding="utf-8"))

    payload["finished_at"] = datetime.now(timezone.utc).isoformat()
    payload["success"] = success
    if details:
        payload.update(details)

    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if source.exists():
        source.unlink()


def cancel_pending_job(run_id: str) -> bool:
    path = _job_path(PENDING_DIR, run_id)
    if not path.exists():
        return False
    path.unlink()
    return True


def retry_job(run_id: str, config_path: str) -> dict[str, Any]:
    previous_attempt = 0

    for directory in [FAILED_DIR, DONE_DIR]:
        path = _job_path(directory, run_id)
        if path.exists():
            try:
                previous_attempt = int(
                    json.loads(path.read_text(encoding="utf-8")).get("attempt", 0)
                )
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                previous_attempt = 0
            path.unlink()

    payload = enqueue_job(run_id, config_path)
    payload["attempt"] = max(1, previous_attempt + 1)
    _job_path(PENDING_DIR, run_id).write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return payload


def queue_snapshot() -> dict[str, int]:
    return {
        "pending": len(list(PENDING_DIR.glob("*.json"))),
        "claimed": len(list(CLAIMED_DIR.glob("*.json"))),
        "done": len(list(DONE_DIR.glob("*.json"))),
        "failed": len(list(FAILED_DIR.glob("*.json"))),
    }
