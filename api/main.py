from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tuneforge.studio import create_run, get_run, hardware_capabilities, list_runs, validate_experiment

app = FastAPI(
    title="TuneForge Studio API",
    version="0.2.0",
    description="Self-service orchestration API for parameter-efficient LLM adaptation experiments.",
)


class ExperimentRequest(BaseModel):
    config: dict
    launch: bool = False


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "tuneforge-studio"}


@app.get("/capabilities")
def capabilities() -> dict:
    return hardware_capabilities()


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
