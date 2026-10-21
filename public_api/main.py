from __future__ import annotations

import os
import re

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="TuneForge Public Demo API",
    version="1.2.0",
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
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Content-Type", "X-TuneForge-Workspace"],
)

WORKSPACE_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


@app.middleware("http")
async def public_api_hardening(request: Request, call_next):
    if request.method not in SAFE_METHODS:
        return JSONResponse(
            status_code=403,
            content={
                "detail": (
                    "The public TuneForge API is read-only. "
                    "Self-host TuneForge to use mutation endpoints."
                )
            },
        )

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    )
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    if request.method in {"GET", "HEAD"}:
        response.headers["Cache-Control"] = (
            "public, max-age=60, s-maxage=300, stale-while-revalidate=86400"
        )
    else:
        response.headers["Cache-Control"] = "no-store"

    return response


def workspace(
    x_tuneforge_workspace: str = Header(default="default"),
) -> str:
    if not WORKSPACE_PATTERN.fullmatch(x_tuneforge_workspace):
        raise HTTPException(status_code=422, detail="Invalid workspace identifier.")
    return x_tuneforge_workspace


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
