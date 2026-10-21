from __future__ import annotations

import os
import re

from fastapi import Header, HTTPException

WORKSPACE_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")


def require_access(
    x_tuneforge_workspace: str = Header(default="default"),
    x_tuneforge_api_key: str | None = Header(default=None),
) -> str:
    expected_key = os.getenv("TUNEFORGE_API_KEY")

    if expected_key and x_tuneforge_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid TuneForge API key.")

    if not WORKSPACE_PATTERN.fullmatch(x_tuneforge_workspace):
        raise HTTPException(status_code=422, detail="Invalid workspace identifier.")

    return x_tuneforge_workspace
