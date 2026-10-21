from __future__ import annotations

from dataclasses import asdict

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from api.security import require_access
from tuneforge.adapter_registry import (
    get_adapter,
    list_adapters,
    transition_adapter,
)
from tuneforge.compare import compare_adapters, compare_runs
from tuneforge.eval_rules import evaluate_response
from tuneforge.queue import queue_snapshot
from tuneforge.studio import (
    cancel_run,
    create_run,
    get_run,
    hardware_capabilities,
    list_runs,
    read_telemetry,
    read_training_log,
    retry_run,
    validate_experiment,
)

app = FastAPI(
    title="TuneForge Studio API",
    version="0.5.0",
    description=(
        "Workspace-aware control plane for queued LLM adaptation, "
        "evaluation, telemetry, and adapter lifecycle management."
    ),
)


class ExperimentRequest(BaseModel):
    config: dict
    launch: bool = False


class AdapterTransitionRequest(BaseModel):
    target_state: str
    reason: str


class ResponseEvaluationRequest(BaseModel):
    response: str
    rules: dict = {}


def _run_for_workspace(run_id: str, workspace_id: str):
    run = get_run(run_id)
    if run.workspace_id != workspace_id:
        raise FileNotFoundError(run_id)
    return run


def _adapter_for_workspace(adapter_id: str, workspace_id: str):
    record = get_adapter(adapter_id)
    if record.get("workspace_id", "default") != workspace_id:
        raise FileNotFoundError(adapter_id)
    return record


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "tuneforge-studio"}


@app.get("/capabilities")
def capabilities(workspace_id: str = Depends(require_access)) -> dict:
    return {
        **hardware_capabilities(),
        "workspace_id": workspace_id,
    }


@app.get("/queue")
def queue(workspace_id: str = Depends(require_access)) -> dict:
    return {
        **queue_snapshot(),
        "workspace_id": workspace_id,
        "note": "Queue counts are host-wide in the local filesystem backend.",
    }


@app.post("/experiments/validate")
def validate(
    request: ExperimentRequest,
    workspace_id: str = Depends(require_access),
) -> dict:
    errors = validate_experiment(request.config)
    return {
        "valid": not errors,
        "errors": errors,
        "workspace_id": workspace_id,
    }


@app.post("/experiments")
def create_experiment(
    request: ExperimentRequest,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        run = create_run(
            request.config,
            launch=request.launch,
            workspace_id=workspace_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return asdict(run)


@app.get("/experiments")
def experiments(
    workspace_id: str = Depends(require_access),
) -> list[dict]:
    return [
        asdict(run)
        for run in list_runs(workspace_id=workspace_id)
    ]


@app.get("/experiments/{run_id}")
def experiment(
    run_id: str,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        return asdict(_run_for_workspace(run_id, workspace_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc


@app.post("/experiments/{run_id}/cancel")
def cancel_experiment(
    run_id: str,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        _run_for_workspace(run_id, workspace_id)
        return asdict(cancel_run(run_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/experiments/{run_id}/retry")
def retry_experiment(
    run_id: str,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        _run_for_workspace(run_id, workspace_id)
        return asdict(retry_run(run_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/experiments/{run_id}/telemetry")
def experiment_telemetry(
    run_id: str,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        _run_for_workspace(run_id, workspace_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc

    return {"run_id": run_id, "points": read_telemetry(run_id)}


@app.get("/experiments/{run_id}/logs")
def experiment_logs(
    run_id: str,
    max_lines: int = 200,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        _run_for_workspace(run_id, workspace_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc

    return {
        "run_id": run_id,
        "lines": read_training_log(
            run_id,
            max_lines=max(1, min(max_lines, 1000)),
        ),
    }


@app.get("/adapters")
def adapters(
    workspace_id: str = Depends(require_access),
) -> list[dict]:
    return list_adapters(workspace_id=workspace_id)


@app.get("/adapters/{adapter_id}")
def adapter(
    adapter_id: str,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        return _adapter_for_workspace(adapter_id, workspace_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Adapter not found.") from exc


@app.post("/adapters/{adapter_id}/transition")
def adapter_transition(
    adapter_id: str,
    request: AdapterTransitionRequest,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        _adapter_for_workspace(adapter_id, workspace_id)
        return transition_adapter(
            adapter_id,
            target_state=request.target_state,
            reason=request.reason,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Adapter not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/compare/runs")
def compare_run_pair(
    left: str,
    right: str,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        _run_for_workspace(left, workspace_id)
        _run_for_workspace(right, workspace_id)
        return compare_runs(left, right)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run metadata not found.") from exc


@app.get("/compare/adapters")
def compare_adapter_pair(
    left: str,
    right: str,
    workspace_id: str = Depends(require_access),
) -> dict:
    try:
        _adapter_for_workspace(left, workspace_id)
        _adapter_for_workspace(right, workspace_id)
        return compare_adapters(left, right)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Adapter not found.") from exc


@app.post("/evaluation/rules")
def evaluate_rules(
    request: ResponseEvaluationRequest,
    workspace_id: str = Depends(require_access),
) -> dict:
    return {
        "workspace_id": workspace_id,
        "result": evaluate_response(request.response, request.rules),
    }
