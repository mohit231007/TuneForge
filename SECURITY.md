# Security

## Current scope

TuneForge is a portfolio and engineering reference implementation.

It includes an optional API key and workspace identifier to demonstrate a control-plane boundary, but these controls are not presented as enterprise authentication or strong tenant isolation.

## Sensitive data

Do not upload confidential, regulated, proprietary, personal, or credential-bearing training data to a public TuneForge deployment.

Local dataset uploads are written to the Studio upload directory in the reference implementation.

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

## Production hardening

Before using TuneForge in a multi-user environment, add:

- real identity and role-based authorization
- tenant-isolated storage
- encrypted secrets
- upload scanning and quotas
- durable audit logs
- network isolation for GPU workers
- dependency and container scanning
- rate limits
- object-storage access controls
- queue authentication
- model/dataset allowlists where appropriate
- worker heartbeats and leases
- safe running-job cancellation

## Reporting

For a real public deployment, add a monitored security contact before accepting external vulnerability reports.
