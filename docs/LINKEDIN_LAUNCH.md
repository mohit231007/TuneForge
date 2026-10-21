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
- experiment orchestration and telemetry
- deterministic base-vs-adapted evaluation
- run and adapter comparison
- versioned adapter registry
- candidate → validated → production → archived lifecycle
- Next.js public product UI
- Dockerized service boundaries
- CI and automated quality checks

The measured Experiment 001 trained **1,126,400 parameters out of 1,101,174,784 total — 0.1022908%**.

On an NVIDIA Tesla T4, that produced a **7.7659 MiB adapter** with a final training loss of **1.8312**.

For the two fixed deterministic evaluation prompts, the adapted model also followed the requested response format more closely: the 2–3 sentence request produced 2 sentences, and the three-tip request produced exactly 3 numbered tips. I treat that as a narrow instruction-adherence result, not a claim of broad model superiority.

The part I found most valuable was not simply making training run.

It was engineering everything around the model so the result is reproducible, inspectable and governable.

Live demo: https://tuneforge-algosphere1.vercel.app

GitHub: https://github.com/mohit231007/TuneForge

**TuneForge — A product by The Algosphere.**

#LLM #GenerativeAI #LoRA #QLoRA #PEFT #AIEngineering #MachineLearning #MLOps #PyTorch #HuggingFace #FastAPI #NextJS #DataScience

## Launch gate

Do not publish this post until:

- PR stack is merged cleanly
- CI is green
- [x] one real Experiment 001 run is saved
- [x] actual adapter size is recorded
- [x] actual loss history is recorded
- [x] actual base-vs-adapted outputs are available
- [x] public UI deployed at https://tuneforge-algosphere1.vercel.app
- [ ] final live screenshots captured for the launch carousel
