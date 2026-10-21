# TuneForge — Recruiter Brief

## 30-second version

TuneForge is a self-service LLM adaptation and evaluation platform for LoRA and QLoRA workflows.

Instead of keeping fine-tuning inside a research notebook, TuneForge separates the workflow into a public product UI, FastAPI control plane, queued GPU workers, reproducible experiment configs, telemetry, deterministic evaluation, and a governed adapter registry.

The measured TinyLlama Experiment 001 trained **1,126,400 of 1,101,174,784 parameters (0.1022908%)**, producing a **7.7659 MiB** adapter on an NVIDIA Tesla T4.

## What this demonstrates

- practical LLM fine-tuning with PEFT / TRL
- LoRA and 4-bit QLoRA
- Hugging Face model and dataset workflows
- deterministic dataset engineering
- GPU-aware precision selection
- FastAPI service design
- asynchronous job orchestration
- experiment telemetry
- model artifact lifecycle management
- reproducible evaluation
- Next.js product engineering
- Dockerized service boundaries
- CI across Python and frontend builds

## The engineering problem

A notebook can train an adapter, but it does not solve:

- who defines an experiment
- how a run is reproduced
- how GPU work is separated from the web tier
- how failures are retried
- how results are compared
- how adapters are versioned
- which adapters are validated for production
- how claims are backed by measurable evidence

TuneForge is designed around those questions.

## Reference result

Observed in the initial TinyLlama LoRA experiment:

- base model: TinyLlama-1.1B-Chat
- trainable parameters: 1,126,400
- total parameters: 1,101,174,784
- trainable fraction: approximately 0.1023%
- LoRA targets: q_proj and v_proj
- reference GPU: NVIDIA Tesla T4
- final training loss: 1.831209
- adapter size: 7.7659 MiB
- same-prompt deterministic evaluation: adapted output followed both requested response formats more closely in the two-prompt reference check

Do not interpret the parameter-efficiency result as a quality benchmark. Model-quality claims require broader evaluation.

## Architecture in one line

Next.js → FastAPI → execution backend → job queue → CUDA worker → TRL/PEFT → telemetry/evaluation → adapter registry.

## What is intentionally not overstated

TuneForge currently uses a reference filesystem queue for local reproducibility, lightweight API-key/workspace controls, and deterministic heuristic evaluation in addition to model-output metrics.

The architecture defines seams for durable queues, remote GPU providers, enterprise identity, object storage, and richer evaluation, but does not claim those are already production infrastructure.
