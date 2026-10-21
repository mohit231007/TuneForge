from __future__ import annotations

import os
import re

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="TuneForge Public Demo API",
    version="1.0.0",
    description="Read-only public API for the TuneForge recruiter-facing demo.",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "TUNEFORGE_ALLOWED_ORIGINS",
        "http://localhost:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORKSPACE_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")


class EvaluationRequest(BaseModel):
    response: str
    rules: dict = Field(default_factory=dict)


def workspace(
    x_tuneforge_workspace: str = Header(default="default"),
) -> str:
    if not WORKSPACE_PATTERN.fullmatch(x_tuneforge_workspace):
        raise HTTPException(status_code=422, detail="Invalid workspace identifier.")
    return x_tuneforge_workspace


def _readonly() -> None:
    raise HTTPException(
        status_code=403,
        detail=(
            "This is the read-only public TuneForge demo. "
            "Self-host TuneForge with a CUDA worker to launch experiments."
        ),
    )


def _evaluate_response(response: str, rules: dict) -> dict:
    checks = []
    words = response.split()

    if "min_words" in rules:
        target = int(rules["min_words"])
        checks.append({
            "name": "min_words",
            "passed": len(words) >= target,
            "observed": len(words),
            "expected": target,
        })

    if "max_words" in rules:
        target = int(rules["max_words"])
        checks.append({
            "name": "max_words",
            "passed": len(words) <= target,
            "observed": len(words),
            "expected": target,
        })

    for needle in rules.get("contains", []):
        present = needle.lower() in response.lower()
        checks.append({
            "name": f"contains:{needle}",
            "passed": present,
            "observed": present,
            "expected": True,
        })

    for needle in rules.get("not_contains", []):
        absent = needle.lower() not in response.lower()
        checks.append({
            "name": f"not_contains:{needle}",
            "passed": absent,
            "observed": absent,
            "expected": True,
        })

    return {
        "passed": all(check["passed"] for check in checks) if checks else True,
        "check_count": len(checks),
        "passed_count": sum(1 for check in checks if check["passed"]),
        "checks": checks,
    }


@app.get("/")
def root() -> dict:
    return {
        "service": "tuneforge-public-demo",
        "mode": "read-only",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "tuneforge-public-demo"}


@app.get("/capabilities")
def capabilities(
    x_tuneforge_workspace: str = Header(default="default"),
) -> dict:
    workspace_id = workspace(x_tuneforge_workspace)
    return {
        "workspace_id": workspace_id,
        "read_only": True,
        "cuda_available": False,
        "gpu_name": None,
        "compute_capability": None,
        "recommended_precision": "n/a",
        "can_train": False,
    }


@app.get("/queue")
def queue(
    x_tuneforge_workspace: str = Header(default="default"),
) -> dict:
    workspace_id = workspace(x_tuneforge_workspace)
    return {
        "workspace_id": workspace_id,
        "backend": "public-demo",
        "pending": 0,
        "claimed": 0,
        "done": 0,
        "failed": 0,
        "note": "Public demo has no attached GPU job queue.",
    }


@app.get("/experiments")
def experiments(
    x_tuneforge_workspace: str = Header(default="default"),
) -> list[dict]:
    workspace(x_tuneforge_workspace)
    return []


@app.get("/adapters")
def adapters(
    x_tuneforge_workspace: str = Header(default="default"),
) -> list[dict]:
    workspace(x_tuneforge_workspace)
    return []


@app.post("/experiments")
def create_experiment() -> None:
    _readonly()


@app.post("/experiments/{run_id}/cancel")
def cancel_experiment(run_id: str) -> None:
    _ = run_id
    _readonly()


@app.post("/experiments/{run_id}/retry")
def retry_experiment(run_id: str) -> None:
    _ = run_id
    _readonly()


@app.post("/adapters/{adapter_id}/transition")
def transition_adapter(adapter_id: str) -> None:
    _ = adapter_id
    _readonly()


@app.post("/evaluation/rules")
def evaluate_rules(
    request: EvaluationRequest,
    x_tuneforge_workspace: str = Header(default="default"),
) -> dict:
    workspace_id = workspace(x_tuneforge_workspace)
    return {
        "workspace_id": workspace_id,
        "result": _evaluate_response(request.response, request.rules),
    }
