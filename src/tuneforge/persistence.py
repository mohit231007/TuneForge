from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def directory_size_bytes(path: str | Path) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for filename in files:
            total += os.path.getsize(os.path.join(root, filename))
    return total


def save_json(payload: dict[str, Any], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
