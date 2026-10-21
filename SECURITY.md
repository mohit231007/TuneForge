# Security

## Public demo security model

The public TuneForge deployment is intentionally **read-only** and isolated from the full training stack.

Production URLs:

- Web: https://tuneforge-algosphere1.vercel.app
- API: https://tuneforge-public-api.vercel.app

The public API has:

- no database
- no private dataset
- no model weights
- no GPU worker
- no credentials
- no file upload
- no shell/process execution
- no legitimate POST/PUT/PATCH/DELETE endpoint

Deterministic evaluation runs locally in the browser. The public API is GET/HEAD/OPTIONS-only, edge-cacheable, and all unsafe methods are denied both at the Vercel edge and in FastAPI middleware.

See `docs/PRELAUNCH_SECURITY.md` for the detailed threat model and `docs/SECURITY_INCIDENT_RUNBOOK.md` for incident response.

## Sensitive data

Do not upload confidential, regulated, proprietary, personal, or credential-bearing training data to a public TuneForge deployment.

Local dataset uploads are written to the Studio upload directory in the self-hosted reference implementation.

## Model supply chain

Base models and public datasets may execute custom loading logic or carry their own licenses and usage conditions.

Review model repositories, dataset licenses, remote-code requirements, and dependency provenance before use.

## Secrets

Use environment variables or an external secret manager.

Never commit:

- Hugging Face tokens
- cloud credentials
- API keys
- private model URLs
- production worker tokens

## Automated security controls

The repository includes:

- CodeQL scanning for Python and JavaScript/TypeScript
- Dependabot for Python, npm, and GitHub Actions
- production npm dependency audit in CI
- public API Python dependency audit in CI
- Ruff / Pytest / public API tests
- Next.js production build verification
- secret-pattern pre-launch review

## Multi-user / GPU-backed production boundary

The public portfolio demo is not the same security model as a multi-user hosted training service.

Before exposing authenticated GPU-backed TuneForge to external users, add:

- real identity and role-based authorization
- tenant-isolated storage
- encrypted secrets
- upload scanning and quotas
- durable audit logs
- network isolation for GPU workers
- rate limits and per-tenant budgets
- object-storage access controls
- queue authentication
- model/dataset allowlists where appropriate
- worker heartbeats and leases
- safe running-job cancellation
- abuse monitoring and cost controls

## Vulnerability reporting

Do not publish sensitive vulnerability details in a public issue.

For the current portfolio release, contact the repository owner privately through the contact information linked from the GitHub profile. A dedicated monitored security mailbox should be added before accepting broad third-party vulnerability reports.
