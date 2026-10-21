# TuneForge

**Parameter-efficient LLM adaptation, evaluation, and adapter packaging on commodity GPUs.**

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
