# TuneForge

**Parameter-efficient LLM adaptation, evaluation, and adapter packaging on commodity GPUs.**

## Live Demo

- **TuneForge Web:** https://tuneforge-algosphere1.vercel.app
- **Public read-only API:** https://tuneforge-public-api.vercel.app
- **GitHub:** https://github.com/mohit231007/TuneForge

The public deployment is intentionally read-only. It exposes verified Experiment 001 evidence, evaluation tooling, and the product interface without attaching an unauthenticated public GPU training queue.

TuneForge turns a one-off LoRA notebook into a reproducible engineering project: prepare instruction data, establish a fixed baseline, inject LoRA adapters, fine-tune with TRL, persist only the adapter, and compare the adapted model against the untouched base model using the exact same prompts.

## Why this project exists

Full fine-tuning duplicates and updates billions of parameters. TuneForge demonstrates a lighter alternative using **LoRA (Low-Rank Adaptation)**, where a small set of trainable adapter weights is injected into selected attention projection layers.

The reference experiment uses:

- **Base model:** `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- **Dataset:** `databricks/databricks-dolly-15k`
- **LoRA targets:** `q_proj`, `v_proj`
- **Rank / alpha / dropout:** `8 / 16 / 0.05`
- **Reference hardware:** NVIDIA Tesla T4
- **Precision:** FP16 on T4
- **Training subset:** 1,000 deterministic examples
- **Trainable fraction observed in the reference setup:** ~0.10%

> TuneForge is an independent portfolio project built from first principles around a reproducible PEFT workflow. It is not a wrapper around the original course notebook.

## Measured Experiment 001

A real Experiment 001 run was completed on an NVIDIA Tesla T4 using commit `a9637758949925ea6eb2a4d2fc46e4ad87636319`.

| Measure | Result |
|---|---:|
| Trainable parameters | **1,126,400** |
| Total parameters | **1,101,174,784** |
| Trainable fraction | **0.1022908%** |
| Final training loss | **1.831209** |
| Adapter size | **7.7659 MiB** |
| Global steps | **63** |
| Peak reserved GPU memory observed | **3.0898 GiB** |

The same two deterministic prompts were used before and after adaptation. On this small check, the adapted model followed the requested output format more closely: it answered the 2–3 sentence prompt in 2 sentences and the three-tip prompt with exactly 3 numbered tips. This is useful evidence of instruction-format adherence for this run, **not** a broad quality benchmark.

See [the measured Experiment 001 evidence](docs/evidence/EXPERIMENT_001_EVIDENCE.md).

## TuneForge Studio

TuneForge now includes a self-service Studio layer for creating LLM adaptation experiments from a web UI.

Studio users can:

- select a Hugging Face base model
- use a Hugging Face dataset or upload CSV/JSON/JSONL instruction data
- map instruction/context/response fields
- choose LoRA or 4-bit QLoRA
- configure LoRA rank, alpha, dropout, and target modules
- configure batch size, gradient accumulation, epochs, learning rate, sequence length, and seed
- inspect the generated experiment configuration before execution
- detect host GPU capability and recommended precision
- persist experiment runs with unique IDs
- launch the real training engine when CUDA is available
- inspect live run telemetry including loss and GPU memory
- manage versioned adapters in the adapter registry
- review base-vs-adapted evidence after evaluation

Run the API:

    uvicorn api.main:app --host 0.0.0.0 --port 8000

Then run the Studio UI:

    streamlit run app/app.py

See docs/STUDIO.md for the execution model and current scope.

## What TuneForge includes

- Deterministic dataset preparation with a fixed seed
- Dolly instruction/context/response → chat-message formatting
- Baseline generation retained for later comparison
- LoRA configuration targeting attention projections only
- Trainable-parameter accounting
- T4-aware supervised fine-tuning
- Adapter-only persistence and size measurement
- Base-vs-adapted evaluation on identical prompts
- Experiment metadata export
- Streamlit comparison demo
- Unit tests and CI for CPU-safe components

## Repository structure

```text
TuneForge/
├── app/                    # Interactive comparison UI
├── configs/                # Reproducible experiment configuration
├── docs/                   # Architecture, experiment notes, limitations
├── src/tuneforge/          # Reusable Python package
├── tests/                  # CPU-safe unit tests
├── .github/workflows/      # CI
├── pyproject.toml
└── requirements.txt
```

## Quick start

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 2. Train on a GPU machine

```bash
python -m tuneforge.train --config configs/tinyllama_dolly.yaml
```

The training command writes the LoRA adapter plus run metadata under the configured output directory.

### 3. Compare base and adapted responses

```bash
python -m tuneforge.evaluate \
  --config configs/tinyllama_dolly.yaml \
  --adapter ./artifacts/tinyllama-dolly/final-adapter
```

### 4. Launch the demo

```bash
streamlit run app/app.py
```

## Evaluation principle

A fine-tuned model should not be compared against a different prompt set. TuneForge stores a fixed evaluation suite and applies the **same prompts and decoding configuration** to both the untouched base model and the adapted model.

That makes any improvement claim auditable.

## Reference architecture

```text
Dolly-15K
   │
   ▼
deterministic shuffle + formatting
   │
   ▼
TinyLlama base ──► fixed baseline responses
   │
   ▼
LoRA(q_proj, v_proj)
   │
   ▼
TRL SFTTrainer on T4 / FP16
   │
   ▼
adapter-only artifact
   │
   ├──────────────► size + metadata
   │
   ▼
same evaluation prompts
   │
   ▼
base vs adapted comparison
```

## Portfolio evidence

The project is designed to surface evidence rather than only code:

- model and dataset identity
- seed and sample count
- LoRA hyperparameters
- trainable vs total parameters
- training loss history
- GPU / precision mode
- adapter size on disk
- exact baseline and adapted responses
- experiment configuration saved alongside artifacts

## Responsible use

The reference dataset is a general instruction-following dataset. TuneForge does not claim domain expertise, factual reliability, or production readiness from a single short fine-tuning run. Evaluation quality depends on the prompt suite and should be expanded before making production claims.

## License

See [LICENSE](LICENSE).


## Containerized Studio

TuneForge ships separate API and Studio containers.

    docker compose up --build

Then open:

- Studio: http://localhost:8501
- API: http://localhost:8000
- OpenAPI: http://localhost:8000/docs

The default compose stack demonstrates the service boundary and persistent run/adapter state. Production GPU execution should move to dedicated workers rather than blocking the web tier.

## Evaluation evidence

The evaluation pipeline records the exact same prompts against the base and adapted model and stores:

- response text
- generation latency
- generated token count
- tokens per second
- word count
- repetition ratio

These are descriptive runtime/output metrics, not standalone semantic-quality scores. TuneForge deliberately separates measurable evidence from subjective claims.


## Queue and GPU workers

TuneForge no longer requires the web API to execute GPU training directly.

Launch requests are persisted as queued jobs. A dedicated CUDA worker claims a job, runs the training engine, writes logs/telemetry, and updates the run to completed or failed.

    python -m tuneforge.worker

The Studio exposes queue depth, run status, worker identity, safe pre-execution cancellation, and retry for failed/cancelled runs.

## Adapter lifecycle

Every successful adapter starts as a candidate and can be promoted through an explicit lifecycle:

    candidate -> validated -> production -> archived

Adapters can also be archived before production. Every transition records a timestamp and reason.

See docs/ORCHESTRATION.md for the current local implementation and the intended production evolution.


## Public Web Experience

TuneForge now includes a recruiter-facing Next.js product UI in `web/`.

Run locally:

    cd web
    npm install
    npm run dev

Open locally:

- Public web UI: http://localhost:3000
- API: http://localhost:8000
- Operator Streamlit UI: http://localhost:8501

Production:

- Public web UI: https://tuneforge-algosphere1.vercel.app
- Public read-only API: https://tuneforge-public-api.vercel.app

The public UI includes:

- workspace-scoped overview
- LoRA / QLoRA experiment builder
- experiment status and safe retry/cancel actions
- adapter registry and lifecycle promotion
- run comparison
- adapter comparison
- deterministic evaluation checks
- architecture / limitations view

## Lightweight Access Boundary

The API supports an optional environment key:

    TUNEFORGE_API_KEY=change-me

Clients send:

    X-TuneForge-API-Key: change-me
    X-TuneForge-Workspace: demo

If no API key is configured, local development remains open.

Workspace scoping is intentionally described as a lightweight control-plane boundary. It is not a replacement for enterprise identity, authorization, audit, or tenant isolation.

## Execution Backends

By default TuneForge uses the local filesystem-backed queue:

    TUNEFORGE_EXECUTION_BACKEND=local

A remote worker/scheduler can be connected through the webhook backend:

    TUNEFORGE_EXECUTION_BACKEND=webhook
    TUNEFORGE_REMOTE_WORKER_URL=https://gpu-worker.example.com
    TUNEFORGE_REMOTE_WORKER_TOKEN=...

This keeps the product independent of any specific GPU vendor while preserving the same Studio/API contract.

See `docs/PUBLIC_DEMO.md` for launch positioning and claim discipline.
