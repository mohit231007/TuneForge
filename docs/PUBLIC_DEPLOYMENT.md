# Public Deployment

TuneForge's public portfolio deployment is intentionally **read-only**.

## Live production

- **Web:** https://tuneforge-algosphere1.vercel.app
- **API:** https://tuneforge-public-api.vercel.app
- **Repository:** https://github.com/mohit231007/TuneForge

Both services are deployed on Vercel from the same GitHub repository.

## Production topology

### Web

- Vercel project: `tuneforge`
- Framework: Next.js
- Root Directory: `web`
- Production branch: `main`
- Public authentication protection: disabled
- API environment:
  `NEXT_PUBLIC_TUNEFORGE_API_URL=https://tuneforge-public-api.vercel.app`

### Public API

- Vercel project: `tuneforge-public-api`
- Framework: FastAPI
- Root Directory: `public_api`
- Production branch: `main`
- Public authentication protection: disabled
- CORS:
  `TUNEFORGE_ALLOWED_ORIGINS=https://tuneforge-algosphere1.vercel.app`

The public API deliberately excludes PyTorch, Transformers, PEFT, TRL, and GPU-worker dependencies. It is a lightweight read-only portfolio API.

## Public behavior

The public deployment exposes:

- verified Experiment 001 metrics
- read-only capabilities
- empty live experiment/adapter state on a fresh deployment
- deterministic response-rule evaluation
- architecture and product surfaces

Mutation endpoints intentionally return HTTP 403.

The public dashboard always shows measured Experiment 001 evidence:

- 1,126,400 trainable parameters
- 1,101,174,784 total parameters
- 0.1022908% trainable fraction
- 1.831209 final training loss
- 7.7659 MiB adapter
- 3.0898 GiB peak reserved Tesla T4 memory observed

## Why the public site is read-only

A public recruiter demo should not expose an unauthenticated GPU training queue.

Full TuneForge self-service training remains available when self-hosted with:

- a CUDA worker or remote execution backend
- durable run/adapter persistence
- real authentication and authorization
- protected worker credentials
- appropriate model/dataset governance

## Deployment verification

Verified from Vercel:

- Next.js production deployment: READY
- FastAPI production deployment: READY
- frontend Vercel Authentication: disabled
- API Vercel Authentication: disabled
- API CORS restricted to the production frontend origin
- repository CI: Ruff, Pytest, public API tests, and Next.js production build passing

## Remaining human launch checks

Before publishing broadly:

- open the live frontend in an incognito/private browser
- exercise the Evaluation page against the live API
- confirm the Experiments page displays public read-only mode
- capture final live screenshots for the LinkedIn carousel / README
