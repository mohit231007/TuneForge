# TuneForge Studio

TuneForge Studio is the self-service product layer on top of the TuneForge training engine.

## What a user can do

- choose a Hugging Face base model
- choose a Hugging Face dataset or upload CSV/JSON/JSONL instruction data
- map instruction, context, and response fields
- configure LoRA rank, alpha, dropout, and target modules
- configure epochs, batch size, gradient accumulation, learning rate, sequence length, and seed
- inspect the generated experiment YAML before execution
- check whether the API host has a CUDA GPU and which precision mode is recommended
- create a reproducible experiment record
- launch training when the host has a CUDA GPU
- review experiment status
- evaluate base and adapted responses through the existing comparison pipeline

## Local run

Start the API:

    uvicorn api.main:app --host 0.0.0.0 --port 8000

Start the Studio UI in another terminal:

    streamlit run app/app.py

The UI defaults to http://localhost:8000 for the API.

## Execution model

Studio intentionally separates experiment definition from GPU execution.

If the API host has no CUDA GPU, a user can still create and inspect a complete experiment configuration. Launch requests are marked blocked instead of pretending that training occurred.

If CUDA is available, Studio launches the existing TuneForge training CLI as a separate process and writes stdout/stderr to the run directory.

## Current scope

Version 0.2 focuses on supervised LoRA adaptation.

Planned extensions include QLoRA, richer dataset diagnostics, adapter registry/versioning, live loss streaming, evaluation scorecards, containerized workers, remote GPU backends, authentication, and production observability.
