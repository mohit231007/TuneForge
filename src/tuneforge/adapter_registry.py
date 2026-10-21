from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGISTRY_DIR = Path("adapter_registry")
REGISTRY_DIR.mkdir(exist_ok=True)

LIFECYCLE_STATES = {"candidate", "validated", "production", "archived"}
ALLOWED_TRANSITIONS = {
    "candidate": {"validated", "archived"},
    "validated": {"production", "archived"},
    "production": {"archived"},
    "archived": set(),
}


def _adapter_path(adapter_id: str) -> Path:
    return REGISTRY_DIR / f"{adapter_id}.json"


def register_adapter(metadata: dict[str, Any]) -> dict[str, Any]:
    adapter_id = f"ADP-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "adapter_id": adapter_id,
        "created_at": now,
        "updated_at": now,
        "lifecycle": "candidate",
        "lifecycle_history": [
            {
                "from": None,
                "to": "candidate",
                "at": now,
                "reason": "Adapter created by a successful TuneForge training run.",
            }
        ],
        **metadata,
    }

    _adapter_path(adapter_id).write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )
    return record


def list_adapters(workspace_id: str | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for path in REGISTRY_DIR.glob("ADP-*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if workspace_id is None or record.get("workspace_id", "default") == workspace_id:
                records.append(record)
        except Exception:
            continue

    return sorted(
        records,
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )


def get_adapter(adapter_id: str) -> dict[str, Any]:
    path = _adapter_path(adapter_id)

    if not path.exists():
        raise FileNotFoundError(adapter_id)

    return json.loads(path.read_text(encoding="utf-8"))


def transition_adapter(
    adapter_id: str,
    target_state: str,
    reason: str,
) -> dict[str, Any]:
    target = target_state.lower()

    if target not in LIFECYCLE_STATES:
        raise ValueError(f"Unsupported adapter lifecycle state: {target}")

    record = get_adapter(adapter_id)
    current = record.get("lifecycle", "candidate")

    if target == current:
        return record

    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(
            f"Invalid adapter transition: {current} -> {target}"
        )

    now = datetime.now(timezone.utc).isoformat()
    record["lifecycle"] = target
    record["updated_at"] = now
    record.setdefault("lifecycle_history", []).append(
        {
            "from": current,
            "to": target,
            "at": now,
            "reason": reason,
        }
    )

    _adapter_path(adapter_id).write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )
    return record
