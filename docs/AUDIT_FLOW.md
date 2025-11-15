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
# Evidence Bundle & Signing

The Prism Console produces an attestation bundle for each policy evaluation
when the caller opts in (`bundle: true`). Bundles combine:

1. `manifest.json` – canonical metadata with hashes, policy context, and
   signatures.
2. `report.pdf` – a human friendly cover sheet summarising the decision and
   hashes.
3. Detached signatures – Ed25519 is always produced, PQC is added when the
   optional `OQS_CLI` tool is available.

## Request flow

```
POST /api/policy/evaluate
{
  "inputs": { ... },
  "prompt": "...",
  "model": "gpt-4o",
  "policy": "RiskOps",
  "bundle": true
}
```

The API returns the evaluation plus bundle metadata:

```
{
  "ok": true,
  "decision": { ... },
  "bundle": {
    "url": "/api/attest/bundles/<id>",
    "sha256": "...",
    "signatures": {
      "ed25519": { "publicKey": "...", "signature": "..." },
      "pqc": { "mode": "unavailable" }
    }
  }
}
```

The URL streams the tarball (`manifest.json` + `report.pdf`).

## Determinism & hashing

- Inputs, prompt, and manifest objects are serialised with lexicographically
  sorted keys.
- Bundle hashes are SHA-256 over the canonical manifest (with the `signatures`
  section removed) concatenated with the PDF bytes.
- Ed25519 signing uses a deterministic private key derived from `ATTEST_SEED`
  (32 byte hex) to ease automated testing.
- PQC signing (if enabled) runs `oqs-sig sig default` against the canonical
  manifest/report tarball. The base64 signature is embedded in the manifest.

## Verification

`POST /api/attest/verify` accepts either a local upload (base64) or URL to a
bundle. Verification steps:

1. Extract `manifest.json` + `report.pdf`.
2. Recompute the canonical hash and compare with `manifest.bundle.hash`.
3. Verify the Ed25519 signature with the embedded public key.
4. Optionally run PQC verification (if `OQS_CLI` is available on the verifier).

Responses include `valid`, `reasons[]`, and the parsed manifest for further
inspection.

## Operational notes

- Store bundles under `var/attest/bundles/` (created automatically).
- Rotate `ATTEST_SEED` from secrets management. Because manifests include the
  public key, historical bundles remain verifiable after rotation.
- PQC is optional. When the CLI is absent the manifest will include
  `{ "mode": "unavailable" }` so the UI can show a neutral badge. When the
  caller explicitly turns PQC off the manifest records `{ "mode": "disabled" }`.
