# Pre-Launch Security Posture

## Public architecture

TuneForge's public portfolio deployment is deliberately separated from the full training system.

### Public web

- Next.js on Vercel
- no client secrets
- production API URL is the only public environment value
- clickjacking, MIME-sniffing, referrer, permissions, HSTS, and CSP frame/object protections

### Public API

- lightweight FastAPI service
- no PyTorch / Transformers / PEFT / TRL runtime
- no database
- no model weights
- no private dataset
- no GPU worker
- no credentials
- no legitimate POST/PUT/PATCH/DELETE endpoints
- GET endpoints return static/read-only demo state
- GET responses use edge caching
- all unsafe methods are denied in application middleware and again at the Vercel edge

## Abuse resistance

### Volumetric DDoS

Vercel provides platform-level DDoS mitigation and its edge network absorbs traffic before the application function.

### API spam

The public demo no longer exposes a computational POST endpoint.

Deterministic evaluation runs entirely in the browser. The API therefore has no legitimate write/compute POST surface to rate-limit.

Repeated GET requests are:

1. cheap/static;
2. cacheable at the Vercel edge;
3. behind Vercel's platform DDoS/WAF layer.

A project-level per-IP rate-limit rule remains optional defense-in-depth rather than a launch dependency.

### Write attacks

Unsafe HTTP methods are rejected twice:

- `public_api/vercel.json` denies POST/PUT/PATCH/DELETE at the Vercel edge.
- FastAPI middleware returns HTTP 403 for all unsafe methods if a request reaches the function.

### Injection

The public API has no SQL/database interpreter, shell invocation, template execution, file upload, model loader, or remote worker.

Workspace identifiers are restricted to a short alphanumeric/underscore/hyphen pattern.

### Request amplification

The public API accepts no request bodies in its legitimate interface.

The browser-side deterministic evaluation limits:

- response text to 8,000 characters;
- min/max word thresholds to 0–2,000;
- required/forbidden term lists to 10 entries;
- term length to 100 characters.

## Security headers

Public API responses include:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- restrictive `Permissions-Policy`
- CSP frame/object restrictions
- HSTS

The Next.js public site sends corresponding browser hardening headers.

## Supply-chain controls

- Ruff + Pytest + public API tests
- Next.js production build in CI
- CodeQL for Python and JavaScript/TypeScript
- Dependabot for Python, npm, and GitHub Actions
- no obvious committed token patterns found during the pre-launch scan

## Incident response

If abnormal traffic is observed:

1. open Vercel Firewall / Observability;
2. enable **Attack Challenge Mode** for 1h, 6h, or 24h during a targeted attack;
3. inspect source IP / user-agent / traffic patterns;
4. add temporary IP or custom WAF rules if useful;
5. verify function invocation/error metrics;
6. roll back the latest deployment if application behavior is implicated;
7. rotate credentials if any secret exposure is suspected.

## Remaining production boundary

This security posture applies to the **public read-only portfolio demo**.

A future authenticated multi-user/GPU-backed TuneForge service requires stronger controls including identity/RBAC, durable audit logging, tenant isolation, quotas, authenticated job submission, worker network isolation, secret management, and cost controls.
