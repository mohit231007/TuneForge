# TuneForge Orchestration

## Purpose

TuneForge separates the web control plane from GPU execution.

The API creates and validates experiments, persists run metadata, and places launch requests into a queue. A dedicated TuneForge worker claims queued jobs and executes the training CLI on a CUDA host.

## Run lifecycle

    ready
      |
      v
    queued
      |
      v
    running
     /   \
    v     v
completed failed
            |
            v
          queued   (retry)

A ready or queued run may be cancelled before a worker starts it.

Running-process cancellation is deliberately not faked in this milestone. Safe remote termination needs a worker control channel and process ownership semantics.

## Queue implementation

The current implementation is filesystem-backed:

- job_queue/pending
- job_queue/claimed
- job_queue/done
- job_queue/failed

This keeps the architecture understandable and locally reproducible while preserving the contract needed to replace the queue later with Redis, SQS, Pub/Sub, or another durable broker.

## Worker

Run one worker:

    python -m tuneforge.worker

Process one job and exit:

    python -m tuneforge.worker --once

The worker refuses to claim training jobs when CUDA is unavailable.

## Adapter lifecycle

Successful training registers each adapter as:

    candidate

Allowed transitions:

    candidate -> validated
    candidate -> archived
    validated -> production
    validated -> archived
    production -> archived

TuneForge records transition history and a reason for every lifecycle change.

This makes adapter promotion explicit rather than treating every training result as production-ready.

## Production evolution

A production-grade next step should replace filesystem state with:

- PostgreSQL for run and adapter metadata
- Redis/SQS/PubSub for durable job delivery
- object storage for adapters and evaluation artifacts
- worker heartbeats and leases
- idempotency keys
- real cancellation signals
- retries with backoff and attempt limits
- authentication and tenant isolation
- centralized metrics/logging/tracing
