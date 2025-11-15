# Limitations — Quantum-Secure Compliance Copilot

- **PQC demo key** — The SHAKE-256 signer is a deterministic demo implementation. Replace with an approved NIST PQC algorithm (e.g., Dilithium) before production.
- **Rationale generation** — Drafts are deterministic templates, not backed by a live LLM. Integrate a governance-reviewed model for production use.
- **Data storage** — JSONL files are used for speed. Swap for a managed database with encryption-at-rest and retention policies.
- **Policy coverage** — 12 rules provide guardrails, but they are not exhaustive representations of FINRA/SEC obligations. Expand with compliance counsel input.
- **Authentication** — Sandbox lacks authentication. Gate with SSO/OAuth before exposing to advisors in production.
- **Artifacts** — Bundles store full payloads, including PII. Apply redaction/minimization before moving beyond controlled demos.
