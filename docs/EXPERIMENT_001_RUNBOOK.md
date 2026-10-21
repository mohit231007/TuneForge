# Experiment 001 Runbook

## Purpose

Run the canonical TuneForge LoRA experiment on a real NVIDIA T4 and produce the evidence required for Issue #7.

## Recommended path

Open the Colab notebook:

https://colab.research.google.com/github/mohit231007/TuneForge/blob/main/notebooks/TuneForge_Experiment_001.ipynb

Then select:

**Runtime → Change runtime type → T4 GPU**

Run all cells from top to bottom.

## What the notebook does

1. Verifies an NVIDIA T4 is attached.
2. Clones a fresh copy of TuneForge.
3. Prints the exact Git commit.
4. Updates `torchao` to avoid the PEFT incompatibility previously seen in Colab.
5. Installs TuneForge.
6. Prints framework and CUDA versions.
7. Executes the canonical training engine.
8. Releases the training subprocess.
9. Executes deterministic base-vs-adapted evaluation.
10. Verifies the exact configured prompts were reused.
11. Packages launch evidence into a ZIP.
12. Downloads the ZIP.

## One-command equivalent

On any CUDA machine with the repository checked out:

```bash
python -m pip install -U "torchao>=0.16.0"
python -m pip install -e .
python -m tuneforge.experiment_001 \
  --config configs/experiment_001.yaml \
  --clean
```

## Evidence produced

Under `artifacts/experiment-001/`:

- `experiment_config.yaml`
- `telemetry.jsonl`
- `run_metadata.json`
- `final-adapter/`
- `evaluation/comparison.json`
- `evaluation/comparison.csv`
- `experiment_001_evidence.json`
- `EXPERIMENT_001_EVIDENCE.md`
- `experiment_001_evidence.zip`

## Automatic verification

The evidence runner refuses to package results if the evaluation prompt list differs from the configured Experiment 001 prompt list.

It also records:

- Git commit
- Python version
- PyTorch version
- GPU model
- compute capability
- selected precision
- model and dataset configuration
- trainable/total parameter counts
- trainable percentage
- final training loss
- logged loss history
- adapter size
- adapter registry record
- telemetry count
- base/adapted responses
- inference latency
- generated tokens
- tokens per second

## Launch rule

Do not update the README or LinkedIn launch post with Experiment 001 training-loss, adapter-size, or output-quality claims until the generated evidence ZIP has been reviewed.
