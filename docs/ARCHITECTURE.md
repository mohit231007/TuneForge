# TuneForge Architecture

## Goal

TuneForge separates experiment definition, data preparation, training, adapter persistence, and evaluation so that results are reproducible and reviewable.

## Flow

Experiment YAML → deterministic Dolly preparation → TinyLlama base model → fixed baseline evaluation → LoRA injection → TRL SFTTrainer → adapter artifact → controlled base-vs-adapted comparison.

## Design decisions

### Target attention projections, not every linear layer

The reference experiment applies adapters to q_proj and v_proj. This keeps the trainable fraction small and makes the adaptation strategy easy to audit.

### Deterministic subset selection

The dataset is shuffled with a fixed seed before taking the first N rows. This avoids relying on the source dataset's original ordering.

### Hardware-aware precision

TuneForge selects FP16 for pre-Ampere CUDA devices such as Tesla T4 and BF16 for compute capability 8.x+ devices. CPU execution disables mixed precision.

### Same prompts before and after

Evaluation prompts live in configuration and are applied unchanged to the untouched base model and the adapted model. This avoids moving the goalposts between baseline and post-training evaluation.

### Adapter-only persistence

The trained PEFT model is saved with save_pretrained, producing adapter weights/configuration instead of another complete 1.1B-parameter model copy.
