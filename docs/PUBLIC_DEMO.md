# Public Demo Strategy

## Goal

The public TuneForge experience should communicate the engineering story in under 30 seconds:

1. TuneForge is more than a fine-tuning notebook.
2. Users can configure LoRA or QLoRA experiments.
3. GPU work is queued and executed by independent workers.
4. Training emits observable evidence.
5. Adapters are reusable, comparable, and promoted through an explicit lifecycle.
6. Evaluation separates measurable facts from subjective quality claims.

## Public frontend

The Next.js app under web/ is the recruiter-facing product surface.

Primary sections:

- Overview — product narrative, queue health, recent experiments, adapter inventory.
- Experiments — create LoRA/QLoRA runs and inspect run state.
- Adapters — inspect and promote adapter artifacts.
- Compare — compare two runs or two adapters.
- Evaluation — deterministic response rules.
- Architecture — system-design explanation and explicit limitations.

The Streamlit app remains useful as an operator/reference UI and is not removed.

## Workspace boundary

The API accepts:

- X-TuneForge-Workspace
- X-TuneForge-API-Key

If TUNEFORGE_API_KEY is configured, the key becomes mandatory.

Workspace identifiers scope run and adapter listing. This is a lightweight portfolio control-plane boundary, not enterprise IAM or strong multi-tenant isolation.

## Remote execution

TUNEFORGE_EXECUTION_BACKEND supports:

- local — filesystem-backed queue used by the local worker.
- webhook — forwards submit/cancel/retry/queue operations to an external worker service.

Required webhook settings:

    TUNEFORGE_EXECUTION_BACKEND=webhook
    TUNEFORGE_REMOTE_WORKER_URL=https://gpu-worker.example.com
    TUNEFORGE_REMOTE_WORKER_TOKEN=...

This creates a clean seam for RunPod, Kubernetes, cloud GPU workers, or an internal scheduler without coupling Studio to a specific vendor.

## Demo evidence

Do not fabricate experiment results.

For a public launch, capture at least one real completed Experiment 001 containing:

- base model and dataset identity
- LoRA/QLoRA settings
- trainable parameter percentage
- loss history
- GPU identity and precision
- adapter size
- identical before/after prompt set
- latency and tokens/sec
- deterministic evaluation checks
- adapter lifecycle transition history

## Public claim discipline

Good claim:

> TuneForge adapted TinyLlama-1.1B with approximately 0.10% trainable parameters in the reference LoRA experiment.

Avoid:

> TuneForge makes models smarter.

The first is measurable. The second requires a broader quality evaluation.
