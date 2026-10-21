# TuneForge v1.0.0 — Public Portfolio Release

**Release status:** READY

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

## Security

A dedicated pre-launch security review was completed for the public deployment.

Detailed defensive controls, thresholds, and operational procedures are intentionally not published.

## Verification

The release passed the project's automated quality, dependency, security-analysis, build, deployment, and human browser-review gates.

## Deliberate boundaries

v1.0.0 is a **public portfolio/recruiter demo plus self-hostable engineering reference**, not a hosted multi-tenant GPU training SaaS.

## Release decision

No known blocker remains for the public portfolio release.

Routine dependency-maintenance work continues after release and is not considered a release blocker when current release gates remain green.
