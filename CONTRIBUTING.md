# Contributing

TuneForge is organized around reviewable changes rather than direct commits to the default branch.

## Development setup

    make install
    make lint
    make test

For QLoRA development:

    make install-qlora

## Local product stack

Terminal 1:

    make api

Terminal 2:

    make web

Optional operator UI:

    make studio

A CUDA-capable worker can be started with:

    make worker

## Pull request expectations

A change should explain:

- the user or engineering problem
- the implementation
- how it was tested
- any model/GPU assumptions
- rollback or compatibility concerns
- whether public claims or evaluation behavior changed

## Model engineering rules

- keep experiment seeds explicit
- do not silently change evaluation prompts between baseline and adapted models
- do not commit downloaded base-model weights
- do not commit secrets
- do not claim quality improvement from training loss alone
- keep hardware-specific precision behavior explicit
- preserve adapter metadata needed to reproduce a run

## Frontend

The Next.js app lives in web/.

Before opening a UI PR:

    cd web
    npm install
    npm run build

## Security

Read SECURITY.md before adding uploads, authentication, external workers, or secret-bearing integrations.
