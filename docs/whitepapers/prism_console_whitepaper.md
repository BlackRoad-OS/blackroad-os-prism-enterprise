# BlackRoad Prism Console — Product & Architecture Whitepaper

## Overview
BlackRoad Prism Console delivers a layered control plane where operators steer enterprise bots, enforce policy, and retain a tamper-evident history of every action. The console, orchestrator, and bot swarm are wired together through a signed audit log so regulators, security teams, and investors can verify execution against policy in real time.

## System Architecture
The repository documents a three-tier model—Console, Orchestrator, Bots—with policy enforcement converging on an append-only `memory.jsonl` audit trail.【F:docs/ARCHITECTURE.md†L1-L50】 The Typer-based console provides a consistent CLI for creating tasks, routing them, and interrogating history, exposing modular arithmetic utilities that double as health checks for deterministic execution paths.【F:cli.py†L1-L140】 Bots register through the orchestrator registry and inherit the shared protocol that standardises inputs, outputs, and mission metadata, keeping the swarm composable as new agents come online.【F:orchestrator/registry.py†L1-L24】【F:sdk/plugin_api.py†L1-L29】

## Memory & Audit Assurance
Every orchestrated task is redacted, signed, and chained before landing in `memory.jsonl`. The memory log loader signs entries with an HMAC, links each record to the previous hash, and ensures payloads have been redacted before persistence, providing an auditable timeline that can be rebuilt offline.【F:orchestrator/memory.py†L1-L98】 Security guidance codifies the same controls for audit log tamper-proofing and secret handling, reinforcing that the append-only log plus detached signatures are required for compliance narratives.【F:docs/SECURITY.md†L1-L40】

## Security & Privacy Controls
PII redaction is enforced through deterministic tokenisation of emails and phone numbers before storage, guaranteeing that sensitive values are never written to disk without hashing and metadata stripping.【F:orchestrator/redaction.py†L1-L65】 The security manual highlights redaction, environment-scoped secrets, and signature-backed audit logging as baseline defences, aligning procedural guidance with the code-level implementation.【F:docs/SECURITY.md†L19-L32】

## Cadillac Set A Control Panels
Cadillac’s high-trust panel is grounded in three verifiable primitives:

- **Verifiable compute beacons**: Codex entry 24 lays out the verifiable delay function (VDF) pattern used for randomness committees, showing how proofs \(\pi\) and beacons \(R_t\) feed orchestration decisions.【F:codex/entries/024-verifiable-delay-randomness.md†L1-L27】
- **Zero-knowledge access**: Codex entry 14 documents the zero-knowledge proof flow—policy predicates, nullifiers, and replay protections—used to gate privileged operations without exposing identities.【F:codex/entries/014-zero-knowledge-access.md†L1-L27】
- **Supply-chain attestation**: The attestation and SBOM configs bind releases to SLSA provenance and deterministic dependency inventories so downstream verifiers can replay builds and confirm package integrity.【F:supply_chain/attest.config.json†L1-L1】【F:supply_chain/sbom.config.json†L1-L1】

## v0.1 Product Slice
The v0.1 slice is anchored by three runnable surfaces:

1. **Web cockpit** – The Next.js Prism Console Web app ships lint, test, e2e, and Storybook scripts plus mock APIs, delivering the operator-facing overview, agents, runbooks, and settings flows at `http://localhost:3000`.【F:apps/prism-console-web/README.md†L1-L114】
2. **Policy-gated control plane** – The Fastify Prism server wires policy routes, diff intelligence, health probes, and bridge plugins while persisting its current mode and capability overrides in `prism.config.yaml`, enabling dynamic gating across playground, dev, trusted, and prod states.【F:prism/server/README.md†L1-L18】【F:prism/server/src/policy.ts†L1-L64】【F:prism/server/src/server.ts†L1-L31】【F:prism/server/prism.config.yaml†L1-L2】
3. **Demo accelerants** – The Stripe seed script populates demo customers, subscriptions, and charges in test mode so the cockpit can light up billing telemetry instantly, while the Prism web simulation kernel spawns agents from a persisted filesystem to showcase swarm orchestration locally.【F:stripe-seed/README.md†L1-L28】【F:apps/prismweb/src/kernel.ts†L1-L200】

## CI/CD & Workflow Scaffolding
Continuous assurance is enforced via repository-wide Make targets for linting, testing, and formatting, Lefthook hooks that chain npm and Make pipelines (including secret scanning), and a GitHub Actions matrix that runs Node tests plus Playwright coverage on every push and pull request.【F:Makefile†L1-L24】【F:lefthook.yml†L1-L21】【F:.github/workflows/test.yml†L1-L44】 Together these pipelines ensure console releases always land with validated builds, reproducible QA, and traceable artefacts.

## Evidence Hooks
| Claim | Evidence |
| --- | --- |
| Console/Orchestrator/Bots layering with audit chain | `docs/ARCHITECTURE.md` (L1-L50) |
| Typer CLI and deterministic command surface | `cli.py` (L1-L140) |
| Bot registry and shared protocol contract | `orchestrator/registry.py` (L1-L24), `sdk/plugin_api.py` (L1-L29) |
| Signed, redacted memory log implementation | `orchestrator/memory.py` (L1-L98) |
| PII redaction safeguards and security policy | `orchestrator/redaction.py` (L1-L65), `docs/SECURITY.md` (L19-L32) |
| Cadillac Set A primitives (VDF, ZK access, supply-chain attestation) | `codex/entries/024-verifiable-delay-randomness.md` (L1-L27), `codex/entries/014-zero-knowledge-access.md` (L1-L27), `supply_chain/attest.config.json` (L1-L1), `supply_chain/sbom.config.json` (L1-L1) |
| v0.1 cockpit, policy gate, demo accelerants | `apps/prism-console-web/README.md` (L1-L114), `prism/server/README.md` (L1-L18), `prism/server/src/policy.ts` (L1-L64), `prism/server/src/server.ts` (L1-L31), `prism/server/prism.config.yaml` (L1-L2), `stripe-seed/README.md` (L1-L28), `apps/prismweb/src/kernel.ts` (L1-L200) |
| CI/CD guardrails | `Makefile` (L1-L24), `lefthook.yml` (L1-L21), `.github/workflows/test.yml` (L1-L44) |
