# Limitations and Responsible Use

TuneForge is an engineering demonstration of LoRA-based adaptation, not a guarantee of model quality.

## Current limitations

- The reference experiment uses only 1,000 Dolly examples and one training epoch.
- The evaluation prompt suite is intentionally small.
- Fine-tuning can improve stylistic instruction-following while still preserving or introducing factual errors.
- Training loss is not a complete measure of useful downstream behavior.
- The demo does not provide safety moderation, access control, rate limiting, or production observability.
- GPU behavior depends on CUDA, PyTorch, Transformers, PEFT, and TRL versions.

## Responsible claims

Public project material should distinguish measured evidence, implemented engineering, and future work. Do not present a short LoRA experiment as a newly trained foundation model.
