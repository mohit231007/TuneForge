# Experiment 001 — TinyLlama + Dolly LoRA

## Objective

Demonstrate an end-to-end parameter-efficient fine-tuning workflow using TinyLlama-1.1B-Chat, Databricks Dolly-15K, and LoRA adapters.

## Reference configuration

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
| Reference GPU | Tesla T4 |
| T4 precision | FP16 |

## Observed parameter efficiency

In the reference notebook run, LoRA injection into q_proj and v_proj yielded approximately:

- Trainable parameters: 1,126,400
- Total parameters: 1,101,174,784
- Trainable percentage: ~0.1023%

These figures should be regenerated and stored in run_metadata.json for each reproducible run rather than treated as universal constants.

## Evaluation policy

TuneForge does not claim improvement merely because training loss decreases. Base and adapted models are evaluated on the same fixed prompts with the same deterministic generation settings.

## Known limitations

- A 1,000-example, one-epoch run is an engineering demonstration, not a production-quality alignment exercise.
- Dolly is a broad instruction dataset rather than a domain-specific corpus.
- Manual response inspection remains subjective.
- The current evaluation suite is intentionally small and should be expanded before production use.
