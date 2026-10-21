# Security Incident Runbook

## Trigger conditions

Use this runbook for:

- sudden request or function-invocation spikes
- repeated 4xx/5xx bursts
- suspected bot/DDoS traffic
- unexpected write attempts
- credential or dependency exposure
- abnormal Vercel spend/usage

## Immediate containment

### Traffic attack

1. Enable Vercel **Attack Challenge Mode**.
2. Keep the public API read-only.
3. Review Firewall and Observability.
4. Add a temporary deny/challenge rule for a clear malicious signature only when justified.

### Application regression

1. Use Vercel Instant Rollback to the last known-good production deployment.
2. Re-run health and browser smoke checks.
3. Fix through a reviewed GitHub PR.

### Secret exposure

1. Revoke/rotate the exposed secret at the provider.
2. Remove it from current source/config.
3. Treat Git history as compromised for that value even after deletion.
4. Review logs and provider audit data for misuse.

## Recovery checks

- `GET /health` returns 200
- public web loads in Incognito
- Verified Experiment 001 card renders
- unsafe public API methods return 403
- no unexpected runtime errors
- CORS remains restricted to the production frontend origin
- Vercel Authentication remains disabled only because the demo is intentionally public

## Post-incident

Document:

- start/end time
- detection source
- affected route/service
- traffic volume
- mitigation applied
- whether any data/secret was exposed
- follow-up engineering action
