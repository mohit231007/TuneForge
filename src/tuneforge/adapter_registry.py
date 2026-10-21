from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGISTRY_DIR = Path("adapter_registry")
REGISTRY_DIR.mkdir(exist_ok=True)


def register_adapter(metadata: dict[str, Any]) -> dict[str, Any]:
    adapter_id = f"ADP-{uuid.uuid4().hex[:8].upper()}"
    record = {
        "adapter_id": adapter_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **metadata,
    }

    path = REGISTRY_DIR / f"{adapter_id}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def list_adapters() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for path in REGISTRY_DIR.glob("ADP-*.json"):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue

    return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)


def get_adapter(adapter_id: str) -> dict[str, Any]:
    path = REGISTRY_DIR / f"{adapter_id}.json"
    if not path.exists():
        raise FileNotFoundError(adapter_id)

    return json.loads(path.read_text(encoding="utf-8"))
