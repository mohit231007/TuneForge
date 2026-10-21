# Public Deployment

TuneForge's public portfolio deployment is intentionally **read-only**.

The public site demonstrates the product, measured Experiment 001 evidence, comparison surfaces, and architecture without exposing unauthenticated GPU-training or adapter-promotion actions.

## Recommended topology

- **Web:** Vercel, Root Directory = `web`
- **API:** Render Blueprint from `render.yaml`
- **GPU workers:** not attached to the public read-only demo

This separation keeps the public portfolio deployment lightweight and safe while preserving the self-hosted/full-worker architecture in the repository.

## 1. Deploy the API on Render

The repository includes `render.yaml`.

Create a Blueprint from the TuneForge repository.

The Blueprint creates:

- service name: `tuneforge-api`
- runtime: Docker
- Dockerfile: `Dockerfile.api`
- plan: free
- region: Singapore
- health check: `/health`
- `TUNEFORGE_READ_ONLY=true`
- `TUNEFORGE_EXECUTION_BACKEND=local`

During Blueprint creation, provide:

`TUNEFORGE_ALLOWED_ORIGINS`

After the frontend is deployed, set this to the exact Vercel production origin, for example:

```text
https://your-tuneforge-project.vercel.app
```

Render's Blueprint/Docker support allows environment variables to be provided to Docker services; secrets should not be committed into the YAML.

## 2. Deploy the Next.js web app on Vercel

Import the same GitHub repository as a Vercel project.

Set:

- Framework: Next.js
- Root Directory: `web`
- Build Command: default
- Output Directory: default

Add:

```text
NEXT_PUBLIC_TUNEFORGE_API_URL=https://<your-render-api>.onrender.com
```

Then deploy/redeploy.

`NEXT_PUBLIC_*` values are compiled into the client bundle, so never put secrets in them.

## 3. Verify

Public API:

```bash
curl https://<your-render-api>.onrender.com/health
```

Expected:

```json
{"status":"ok","service":"tuneforge-studio"}
```

Then confirm the frontend:

- renders Verified Experiment 001 without API state
- can read `/capabilities`, `/experiments`, `/adapters`, and `/queue`
- shows public demo read-only messaging in the experiment builder
- receives HTTP 403 for experiment creation in read-only mode

## 4. Public demo behavior

The public dashboard always shows the verified Experiment 001 measurements from the evidence report:

- 1,126,400 trainable parameters
- 0.1022908% trainable fraction
- 1.831209 final training loss
- 7.7659 MiB adapter
- 3.0898 GiB peak reserved T4 GPU memory observed

Live run and adapter lists can remain empty on a fresh public API. They represent current server-side workspace state, not fabricated demo records.

## 5. Full self-service mode

To allow actual fine-tuning:

- run TuneForge outside read-only mode
- attach a CUDA worker or remote execution backend
- add real authentication/authorization
- persist run/adapter state in durable infrastructure
- do not expose an unauthenticated public GPU queue

## Launch gate

The deployment is public-launch-ready only after:

- Render API URL is live
- Vercel web URL is live
- CORS is verified
- incognito/private-browser test passes
- read-only mutation blocking is verified
- screenshots are captured from the real live deployment
