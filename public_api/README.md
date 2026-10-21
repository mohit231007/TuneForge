# TuneForge Public Demo API

Lightweight read-only FastAPI deployment used by the public TuneForge portfolio frontend.

It intentionally excludes the training engine and GPU dependencies.

Public endpoints:

- `GET /`
- `GET /health`
- `GET /capabilities`
- `GET /queue`
- `GET /experiments`
- `GET /adapters`
- `POST /evaluation/rules`

Mutation endpoints return HTTP 403.

The full self-service API remains under `api/`.


## Deployment

Vercel project root: `public_api`

Production branch: `main`

This read-only public API is intentionally isolated from the full TuneForge ML training stack.
