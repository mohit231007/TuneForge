# LinkedIn Launch Draft

## Hook

**I adapted a 1.1B-parameter LLM while training only ~0.10% of its parameters — then turned the experiment into an LLM engineering platform.**

## Post

A fine-tuning notebook can prove that LoRA works.

It does not answer what happens when a team needs to run the workflow repeatedly, compare experiments, manage GPU jobs, evaluate outputs, or decide which adapter is actually ready to ship.

That is the problem I wanted to explore with **TuneForge**.

TuneForge started with a TinyLlama + Databricks Dolly LoRA experiment and evolved into a self-service LLM adaptation and evaluation studio.

The current system includes:

- LoRA and 4-bit QLoRA
- Hugging Face and custom instruction datasets
- GPU-aware FP16/BF16 execution
- FastAPI experiment control plane
- queued CUDA workers
- loss and GPU-memory telemetry
- deterministic base-vs-adapted evaluation
- run and adapter comparison
- versioned adapter registry
- candidate → validated → production → archived lifecycle
- Next.js public product UI
- Dockerized service boundaries
- Python + frontend CI

The initial reference LoRA setup trained approximately **1.13M parameters out of 1.10B total — ~0.1023%**.

The part I found most valuable was not simply making training run.

It was engineering everything around the model so the result is reproducible, inspectable and governable.

GitHub: https://github.com/mohit231007/TuneForge

**TuneForge — A product by The Algosphere.**

#LLM #GenerativeAI #LoRA #QLoRA #PEFT #AIEngineering #MachineLearning #MLOps #PyTorch #HuggingFace #FastAPI #NextJS #DataScience

## Launch gate

Do not publish this post until:

- PR stack is merged cleanly
- CI is green
- one real Experiment 001 run is saved
- actual adapter size is recorded
- actual loss history is recorded
- actual base-vs-adapted outputs are available
- public UI has been deployed or screenshots are captured
