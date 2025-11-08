# Prism Console Operational Status

## Architecture touchpoints
- **CLI orchestration:** Typer entry points route tasks through the orchestrator, loading policy approvals, shared config, lineage tracking, and bots in one place.
- **Routing core:** The orchestrator manages task persistence, consent-aware routing, SEC gating, lineage, and bot execution hooks that power the console flows.
- **Compliance slice:** A FastAPI app persists account-opening decisions to SQLite and exposes evaluation/history endpoints.

## Production-ready slices
- **Audit & privacy:** Memory append operations hash-link and sign redacted payloads, ensuring the append-only `memory.jsonl` trail stays verifiable.
- **Deterministic PII redaction:** Email/phone tokens are tokenised with deterministic hashes before landing in memory or downstream stores.
- **CLI workflows:** `task:create`, `task:route`, and `task:history` drive JSON-backed storage, policy enforcement, and consent checks for registered bots.
- **Safety pack:** `SAFE_MODE` defaults to read-only operations across local + CI flows, with guards for panic stops and explicit write opt-in.
- **Persona voting demo:** Lucidia Encompass normalises persona packets, computes balanced-ternary consensus, and is callable via `scripts/encompass_demo.py`.

## Scaffolded or needs wiring
- **Web cockpit data:** Next.js data hooks still fall back to mock JSON whenever `BLACKROAD_API_URL` is absent or errors, so the UI operates against stubs by default.
- **Preview/staging secrets:** Environment manifests outline workflows and required AWS/ECS wiring, but secrets/variables must be populated before deploys succeed.
- **Expanded compliance coverage:** The compliance engine only ships account-opening policy checks today; other policy verticals remain TBD for the router.

## 1–2 day cut list
1. **Wire cockpit to live gateway:** Add environment bootstrapping (Next.js runtime config + `.env` docs) so `apps/prism-console-web` reads `BLACKROAD_API_URL/TOKEN` at build time, retries gracefully, and surfaces auth errors in the UI instead of silently swapping to mocks.
2. **Memory audit verifier CLI:** Extend the Typer console with `task:audit` commands that replay `memory.jsonl`, re-hash records, and surface signature drift to operators, proving the append-only chain on demand.
3. **Broaden compliance policies:** Implement additional FastAPI routes plus policy evaluators (e.g., ongoing monitoring, vendor diligence) backed by the existing `ComplianceStore`, keeping schema parity with `AccountOpeningPolicy`.
4. **Preview pipeline secrets manifest:** Produce a checked-in template or `scripts/bootstrap_preview_secrets.py` that maps `environments/preview.yml` requirements to concrete AWS/GitHub secret names so release tooling can hydrate Fly/ECS configs without manual spelunking.
