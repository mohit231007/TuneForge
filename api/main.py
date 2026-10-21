from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tuneforge.adapter_registry import (
    get_adapter,
    list_adapters,
    transition_adapter,
)
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
    version="0.4.0",
    description=(
        "Control plane for queued parameter-efficient LLM adaptation, "
        "telemetry, and adapter lifecycle management."
    ),
)


class ExperimentRequest(BaseModel):
    config: dict
    launch: bool = False


class AdapterTransitionRequest(BaseModel):
    target_state: str
    reason: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "tuneforge-studio"}


@app.get("/capabilities")
def capabilities() -> dict:
    return hardware_capabilities()


@app.get("/queue")
def queue() -> dict:
    return queue_snapshot()


@app.post("/experiments/validate")
def validate(request: ExperimentRequest) -> dict:
    errors = validate_experiment(request.config)
    return {"valid": not errors, "errors": errors}


@app.post("/experiments")
def create_experiment(request: ExperimentRequest) -> dict:
    try:
        run = create_run(request.config, launch=request.launch)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return asdict(run)


@app.get("/experiments")
def experiments() -> list[dict]:
    return [asdict(run) for run in list_runs()]


@app.get("/experiments/{run_id}")
def experiment(run_id: str) -> dict:
    try:
        return asdict(get_run(run_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc


@app.post("/experiments/{run_id}/cancel")
def cancel_experiment(run_id: str) -> dict:
    try:
        return asdict(cancel_run(run_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/experiments/{run_id}/retry")
def retry_experiment(run_id: str) -> dict:
    try:
        return asdict(retry_run(run_id))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/experiments/{run_id}/telemetry")
def experiment_telemetry(run_id: str) -> dict:
    try:
        get_run(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Experiment not found.") from exc

    return {"run_id": run_id, "points": read_telemetry(run_id)}


@app.get("/experiments/{run_id}/logs")
def experiment_logs(run_id: str, max_lines: int = 200) -> dict:
    try:
        get_run(run_id)
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
def adapters() -> list[dict]:
    return list_adapters()


@app.get("/adapters/{adapter_id}")
def adapter(adapter_id: str) -> dict:
    try:
        return get_adapter(adapter_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Adapter not found.") from exc


@app.post("/adapters/{adapter_id}/transition")
def adapter_transition(
    adapter_id: str,
    request: AdapterTransitionRequest,
) -> dict:
    try:
        return transition_adapter(
            adapter_id,
            target_state=request.target_state,
            reason=request.reason,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Adapter not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
