# Required status checks for `main`

Branch protection on `main` expects the following workflow names. The strings
must match the `name` configured in the emitting workflow or the
`workflow_run.workflows` array used by gatekeepers.

| Check | Source workflow | Notes |
| --- | --- | --- |
| `build` | `.github/workflows/ci.yml` (job: `build`) | Aggregates build + package verification. |
| `test` | `.github/workflows/ci.yml` (job: `test`) | Runs the full unit/integration suite. |
| `lint` | `.github/workflows/ci.yml` (job: `lint`) | ESLint, prettier, and Go linters. |
| `security` | `.github/workflows/security-sweep.yml` | Dependency scanning and secret detection. |
| `sbom` | `.github/workflows/sbom.yml` | Builds and validates the SBOM artifact. |
| `policy` | `.github/workflows/policy.yml` | Policy-as-code enforcement (OPA/conftest). |
| `eval` | `.github/workflows/eval.yml` | Scenario/regression evaluation harness. |

Update this table before changing branch protection or workflow names so the
settings JSON stays in sync with automation.
# Required status checks

These are the commit status contexts that must stay green before a pull request can
enter the merge queue or merge to `main`. The aliases below match the defaults used
by `repo-ops/enforce-branch-protection.sh`; update the script's `REQ_CHECKS`
environment variable if you need to add or remove contexts.

| Alias | Commit status context(s) to require | Source workflow | Purpose |
| --- | --- | --- | --- |
| `build` | `CI / build` | `.github/workflows/ci.yml` | Builds the web bundles, runs end-to-end packaging, and ensures the Prism service still compiles and ships images. |
| `test` | `CI / test` | `.github/workflows/ci.yml` | Node unit tests plus Playwright UI coverage. |
| `lint` | `CI / lint` | `.github/workflows/ci.yml` | Static analysis across the JavaScript, Go, and Python surfaces that ship from this repo. |
| `security` | `Security Sweep / scan`<br>`Security • gitleaks / scan` | `.github/workflows/security-sweep.yml`<br>`.github/workflows/gitleaks.yml` | Runs Trivy and gitleaks across the repo so leaked credentials or high/critical CVEs fail the gate. |
| `sbom` | `PR Preview Containers / Generate SBOM` | `.github/workflows/preview-containers.yml` | Publishes an SPDX bill of materials for the preview container created from the PR. |
| `policy` | `CI / policy`<br>`policy-guard / org-guard` | `.github/workflows/ci.yml`<br>`.github/workflows/policy-guard.yml` | Confirms the policy job in CI plus the org guardrails stay enforced. |
| `eval` | `quality-gates / pulse-check` | `.github/workflows/quality-gates.yml` | Verifies the quick-release checklist inside the pull request description stays checked. |

## Updating the branch-protection script

Run `REQ_CHECKS='["CI / build", ...]' repo-ops/enforce-branch-protection.sh`
if you need to pin the exact contexts above. The JSON array should contain the
**commit status names** (for example `CI / build`), not just the alias.
