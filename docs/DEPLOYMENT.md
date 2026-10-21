# Deployment

TuneForge separates the Studio UI from the API/control plane.

## Local containers

Build and start:

    docker compose up --build

Services:

- Studio UI: http://localhost:8501
- API: http://localhost:8000
- OpenAPI docs: http://localhost:8000/docs

## GPU execution

The default compose file demonstrates the service boundary and persists Studio state, but it does not claim to provide a production GPU scheduler.

For local GPU training, run the API on a CUDA-capable host with the NVIDIA container/runtime stack or run the training worker directly on the GPU host.

A production deployment should separate:

1. Studio web UI
2. API/control plane
3. durable metadata store
4. job queue
5. one or more GPU workers
6. object storage for adapters and evaluation artifacts
7. observability and access control

## Why this boundary matters

Web requests should not hold a GPU training process open. TuneForge currently launches a separate local process as the first orchestration implementation, while the API and UI contracts are structured so that a remote worker/queue can replace the local launcher later.
