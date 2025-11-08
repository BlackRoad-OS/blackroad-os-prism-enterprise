# Quantum-Secure Compliance Copilot — Threat Model

## LLM misuse & prompt injection
- **Risk:** Advisors could embed malicious instructions in marketing copy to coerce the rationale generator into producing unsanctioned language.
- **Mitigation:** Deterministic prompt template with guard clauses; marketing copy is sanitised and evaluated against language-safety policies before inclusion in the audit bundle.

## Evidence tampering
- **Risk:** Generated artifacts could be modified prior to audits.
- **Mitigation:** Each bundle produces a SHA-256 hash and optional PQC signature. Console exposes hashes to enable independent verification.

## Policy drift
- **Risk:** Rego policies may fall out of sync with Python evaluation logic.
- **Mitigation:** Policies live under `policies/compliance_copilot/*.rego` with unit tests mirroring expected behaviour. Manifest embeds policy file paths and version identifiers.

## Secrets leakage
- **Risk:** PQC signing key or advisor PII could leak via logs.
- **Mitigation:** Signing uses a static demo key for today. Production would source keys from a vault and redact PII before logging. Current implementation stores only hashes, not full payloads, in metrics.

## Availability
- **Risk:** Sandbox overload could degrade latency.
- **Mitigation:** FastAPI app is stateless; deploy behind autoscaling platform (e.g., DO App Platform). Metrics capture latency to guide scaling.
