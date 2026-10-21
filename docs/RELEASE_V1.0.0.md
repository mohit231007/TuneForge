# TuneForge v1.0.0 — Public Portfolio Release

**Release status:** READY

**Release commit baseline:** `7469c7edfa3af807332224727ee358bb92418dc5`

## Live services

- Web: https://tuneforge-algosphere1.vercel.app
- Public API: https://tuneforge-public-api.vercel.app
- Source: https://github.com/mohit231007/TuneForge

## What ships in v1.0.0

### LLM engineering

- reproducible LoRA training workflow
- 4-bit QLoRA support
- Hugging Face and uploaded instruction datasets
- hardware-aware FP16/BF16 selection
- TinyLlama + Dolly reference experiment
- trainable-parameter accounting
- adapter-only persistence
- training telemetry
- deterministic base-vs-adapted evaluation
- run and adapter comparison

### Platform

- Next.js recruiter-facing web application
- FastAPI control plane
- Streamlit operator UI
- queued CUDA worker architecture
- local and remote execution backend boundary
- versioned adapter registry
- adapter lifecycle:
  `candidate → validated → production → archived`
- Dockerized API/web/worker services

### Verified Experiment 001

Measured on NVIDIA Tesla T4:

- trainable parameters: **1,126,400**
- total parameters: **1,101,174,784**
- trainable fraction: **0.1022908%**
- final training loss: **1.831209**
- adapter size: **7.7659 MiB**
- global steps: **63**
- peak reserved GPU memory observed: **3.0898 GiB**
- exact before/after evaluation prompt identity preserved

The two-prompt comparison is reported only as narrow instruction-format adherence, not a general model-quality benchmark.

## Public security model

The public portfolio deployment is intentionally read-only.

- public API accepts legitimate GET/HEAD/OPTIONS traffic only
- unsafe HTTP methods are denied at the Vercel edge and in FastAPI middleware
- deterministic evaluation executes locally in the browser
- no public GPU queue
- no public model inference
- no database
- no private training dataset or model weights
- no public file upload
- no application credentials in the browser
- API CORS restricted to the production frontend origin
- GET responses are edge-cacheable
- security headers applied to web and API
- Vercel edge DDoS/WAF protections remain in front of both services

## Release verification

All release gates passed on the hardened release:

- Ruff — PASS
- full Pytest — PASS
- public API tests — PASS
- public API pip-audit — PASS
- npm production audit — PASS
- Next.js production build — PASS
- CodeQL Python — PASS
- CodeQL JavaScript/TypeScript — PASS
- Vercel API production deployment — READY
- Vercel web production deployment — READY
- Incognito browser walkthrough — PASS
- obvious committed credential-pattern scan — no matches found

## Maintenance controls

- Dependabot: enabled for Python, npm and GitHub Actions
- CodeQL: runs on main, pull requests and weekly schedule
- security incident runbook included
- Vercel Attack Challenge Mode documented as emergency containment
- Instant Rollback documented for application regressions

## Deliberate boundaries

v1.0.0 is a **public portfolio/recruiter demo plus self-hostable engineering reference**, not a hosted multi-tenant GPU training SaaS.

A future externally writable/GPU-backed service must add:

- strong identity/RBAC
- tenant isolation
- durable audit logs
- authenticated job submission
- per-user quotas/budgets
- worker-network isolation
- secure object storage
- upload scanning
- stronger cost/abuse controls
- production-safe running-job cancellation

## Release decision

No known blocker remains for the public portfolio release.

Routine Dependabot upgrade pull requests are maintenance work and are not release blockers because the production dependency audits and CodeQL gates are currently green.
