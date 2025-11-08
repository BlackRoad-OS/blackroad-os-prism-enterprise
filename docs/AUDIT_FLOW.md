# Audit Evidence Flow — Quantum-Secure Compliance Copilot

1. **Intake** — Advisor submits client profile and marketing copy through `/sandbox` or `/api/reviews`.
2. **Rationale drafting** — Deterministic generator produces suitability rationale and remediation guidance.
3. **Policy evaluation** — `PolicyEngine` runs 12 rules spanning `finra_2210`, `sec_204_2`, and `language_safety` packages. Python implementation mirrors Rego source files located in `policies/compliance_copilot/`.
4. **Manifest creation** — `create_manifest` fingerprints the input payload, references policy versions, and stores rule outcomes.
5. **Bundle emission** — `emit_bundle` writes:
   - `artifact.json` (inputs + outputs)
   - `manifest.json` (schema-aligned manifest)
   - `report.pdf` (human-readable summary)
   - optional SHAKE-256 PQC signature
6. **Console exposure** — `/console` displays case status, hashes, PQC signature, and provides download links for artifacts.
7. **Verification** — Auditors can recompute hashes or use the PQC signature to prove integrity using the same `QuantumSigner`.
