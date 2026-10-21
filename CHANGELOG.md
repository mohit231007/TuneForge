# Changelog

## v1.0.0 — Public Portfolio Release

### Added

- LoRA and QLoRA adaptation engine
- reproducible experiment configuration
- GPU-aware precision selection
- custom/Hugging Face dataset ingestion
- training telemetry
- deterministic evaluation
- adapter registry and promotion lifecycle
- queued CUDA worker architecture
- Next.js public UI
- FastAPI control plane
- run/adapter comparison
- measured Experiment 001 evidence
- Vercel public web/API deployment
- Docker service boundaries
- security headers and read-only public API
- CodeQL, Dependabot, npm audit and pip-audit
- security incident response documentation

### Security

- removed all legitimate public write/compute API operations
- moved public deterministic evaluation into the browser
- denied unsafe methods at both Vercel edge and API middleware
- upgraded Next.js to resolve the high-severity PostCSS advisory found by pre-launch audit
- restricted production CORS to the exact TuneForge web origin
- added edge caching for public GET responses

### Verified

- production web/API Ready on Vercel
- all CI/security gates passing
- public Incognito browser walkthrough completed

See `docs/RELEASE_V1.0.0.md` for the complete release record.
