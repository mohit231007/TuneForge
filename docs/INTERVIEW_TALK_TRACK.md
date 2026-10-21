# Interview Talk Track

## Opening

I started with a straightforward LoRA fine-tuning exercise and deliberately asked what would be missing if a team had to use it repeatedly.

The answer was most of the engineering around the model: reproducible experiment definition, dataset validation, GPU-aware execution, job orchestration, telemetry, evaluation, model artifact management, and a usable interface.

That became TuneForge.

## Why LoRA / QLoRA

The reference experiment adapts selected attention projection layers instead of updating the full model.

That reduced the trainable fraction to roughly 0.10% in the TinyLlama reference configuration.

TuneForge also supports a 4-bit QLoRA path using NF4 quantization so the base model can be loaded more efficiently on constrained GPUs.

## Why the API does not train directly

GPU training can run for minutes or hours. Keeping that work inside a web request couples HTTP availability to expensive compute.

TuneForge therefore persists a run, queues a job, and lets a CUDA worker claim it.

The current filesystem queue is intentionally simple and locally reproducible. The execution-backend interface allows it to be replaced by a remote scheduler without changing the product API.

## Why adapters have lifecycle states

A successful training process does not imply a production-ready model.

TuneForge registers new adapters as candidate artifacts.

They must be moved through explicit states:

candidate → validated → production → archived

Every transition records a reason and timestamp.

## Evaluation philosophy

I separate three things:

1. training evidence such as loss and parameter counts
2. operational inference metrics such as latency and tokens/sec
3. model-quality evaluation

TuneForge does not use lower loss or longer responses as proof that a model is better.

The reference comparison uses the exact same prompts and deterministic decoding before and after adaptation, while the rule engine supports auditable task constraints.

## Failure I learned from

During the original T4 run, a framework capability check selected BF16 even though the training kernel required compute capability 8.0 or higher.

Tesla T4 is compute capability 7.5.

I changed TuneForge to make precision selection explicitly hardware-aware, using FP16 for pre-Ampere devices and BF16 where the GPU architecture supports it.

## What I would productionize next

For a multi-user production service I would replace local state with PostgreSQL, a durable queue such as Redis/SQS/PubSub, object storage, worker leases/heartbeats, centralized telemetry, real process cancellation, enterprise identity, and workload isolation.

The important design choice is that those components can replace the reference implementations without rewriting the training engine.
