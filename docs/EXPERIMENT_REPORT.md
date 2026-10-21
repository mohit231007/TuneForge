# Experiment 001 — TinyLlama + Dolly LoRA

## Objective

Demonstrate an end-to-end parameter-efficient fine-tuning workflow using TinyLlama-1.1B-Chat, Databricks Dolly-15K, and LoRA adapters.

## Measured run

Experiment 001 completed successfully on:

- Git commit: `a9637758949925ea6eb2a4d2fc46e4ad87636319`
- GPU: NVIDIA Tesla T4
- Compute capability: 7.5
- Precision: FP16
- PyTorch: 2.11.0+cu130

## Configuration

| Parameter | Value |
|---|---|
| Base model | TinyLlama/TinyLlama-1.1B-Chat-v1.0 |
| Dataset | databricks/databricks-dolly-15k |
| Training subset | 1,000 |
| Shuffle seed | 42 |
| Max sequence length | 512 |
| LoRA rank | 8 |
| LoRA alpha | 16 |
| LoRA dropout | 0.05 |
| Target modules | q_proj, v_proj |
| Learning rate | 2e-4 |
| Epochs | 1 |
| Per-device batch | 4 |
| Gradient accumulation | 4 |
| Effective batch | 16 |
| Global steps | 63 |

## Measured parameter efficiency

- Trainable parameters: **1,126,400**
- Total parameters: **1,101,174,784**
- Trainable percentage: **0.10229075496%**
- Adapter size: **8,143,176 bytes / 7.7659 MiB**

## Training result

- Final training loss: **1.8312092433**
- Logged loss entries: **6**
- Logged loss moved from **2.108998** at step 10 to **1.725705** at step 60.
- Peak reserved GPU memory observed in telemetry: **3.0898 GiB**

## Controlled evaluation

TuneForge evaluated the untouched base model and adapted model on the **exact same two prompts** with deterministic generation.

Aggregate descriptive metrics:

| Metric | Base | Adapted |
|---|---:|---:|
| Latency (s) | 5.4772 | 2.4638 |
| Generated tokens | 193.0 | 70.5 |
| Tokens/s | 34.5038 | 28.5311 |
| Word count | 132.5 | 44.0 |
| Repetition ratio | 0.3375 | 0.2986 |

The adapted model followed the requested response format more closely on both prompts:
- requested 2–3 sentences → adapted returned 2; baseline returned 5
- requested three sleep tips → adapted returned 3 numbered tips; baseline continued to 7 numbered items

This is a narrow instruction-adherence observation, not evidence of general semantic superiority.

## Evidence

See `docs/evidence/EXPERIMENT_001_EVIDENCE.md` for provenance and SHA256 hashes.

## Limitations

- 1,000 examples and one epoch are an engineering demonstration, not production alignment.
- The evaluation suite contains only two prompts.
- Dolly is a broad instruction dataset, not a domain corpus.
- Runtime metrics do not substitute for factuality, safety, human review, or benchmark evaluation.
