# TuneForge Experiment 001 — Measured Evidence

This report is generated from the real Experiment 001 evidence bundle produced by TuneForge on a Google Colab NVIDIA Tesla T4.

## Provenance

- Git commit: `a9637758949925ea6eb2a4d2fc46e4ad87636319`
- Python: 3.13.15
- PyTorch: 2.11.0+cu130
- GPU: NVIDIA Tesla T4
- Compute capability: 7.5
- Precision: FP16 enabled, BF16 disabled

## Experiment configuration

| Item | Value |
|---|---|
| Base model | TinyLlama/TinyLlama-1.1B-Chat-v1.0 |
| Dataset | databricks/databricks-dolly-15k |
| Training samples | 1,000 |
| Seed | 42 |
| Max sequence length | 512 |
| LoRA rank | 8 |
| LoRA alpha | 16 |
| LoRA dropout | 0.05 |
| Target modules | q_proj, v_proj |
| Learning rate | 2e-4 |
| Epochs | 1 |
| Batch size | 4 |
| Gradient accumulation | 4 |
| Effective batch size | 16 |
| Global steps | 63 |

## Parameter efficiency

- Trainable parameters: **1,126,400**
- Total parameters: **1,101,174,784**
- Trainable percentage: **0.1022908%**

## Training

- Final training loss: **1.8312092433**
- Logged losses:
  - step 10: 2.1089977264
  - step 20: 1.8755998611
  - step 30: 1.7602792740
  - step 40: 1.7375190735
  - step 50: 1.7824848175
  - step 60: 1.7257045746
- Telemetry points captured: **7**
- Logged loss entries: **6**
- Peak reserved GPU memory observed in telemetry: **3.0898 GiB**

## Adapter artifact

- Registry ID: `ADP-8C052915`
- Lifecycle: `candidate`
- Adapter size: **8,143,176 bytes**
- Adapter size: **7.7659 MiB**

## Controlled evaluation

The same two configured prompts were used for the base and adapted models with deterministic generation.

Prompt identity preserved: **true**

### Aggregate runtime/output metrics

| Metric | Base model | Adapted model |
|---|---:|---:|
| Average latency (s) | 5.4772 | 2.4638 |
| Average generated tokens | 193.0 | 70.5 |
| Average tokens/s | 34.5038 | 28.5311 |
| Average word count | 132.5 | 44.0 |
| Average repetition ratio | 0.3375 | 0.2986 |

These are descriptive runtime/output metrics, not semantic-quality scores.

### Prompt-level observation

For the prompt asking for a neural-network explanation in **2–3 sentences**, the adapted model returned **2 sentences**, while the baseline returned **5 sentences**.

For the prompt asking for **three tips** for better sleep, the adapted model returned **3 numbered tips**, while the baseline continued to **7 numbered items** and hit the generation limit.

This small two-prompt check suggests improved instruction-format adherence in this reference run, but it is not sufficient to claim broad model-quality improvement.

## Evidence integrity

The evidence bundle verified the following SHA256 hashes:

- `run_metadata.json` — `0b1423e784127aa66368ae74ac5c07ba294d202fbcb276865bb631e296f63dde`
- `telemetry.jsonl` — `d7c9394e44af00fdd8478ac1909c18a04c0e63f32afc8b285031970009adbc68`
- `evaluation/comparison.json` — `482e016356803483513f409a1f6464bae6537f653a49d3ed6ad3231a63f46859`
- `evaluation/comparison.csv` — `67419ec2695432081cbb2266f32e7ff23f51107173c4dd76cfa23381fb733c69`
- `experiment_config.yaml` — `1eaddba7bb5e6f056f8ff619d7e7621a8c4b4999c532b0694e8a70768bc63ba9`

## Claim boundary

Experiment 001 validates the engineering path, parameter efficiency, artifact size, telemetry capture, deterministic comparison flow, and instruction-format observations above.

It does **not** establish production readiness, factual reliability, safety, domain expertise, or general benchmark superiority.
