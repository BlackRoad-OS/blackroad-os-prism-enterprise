# Required status checks for `main`

Branch protection on `main` expects the following workflow names. The strings
must match the `name` configured in the emitting workflow or the
`workflow_run.workflows` array used by gatekeepers.

| Check | Source workflow | Notes |
| --- | --- | --- |
| `build` | `.github/workflows/build.yml` | Aggregates build + package verification. |
| `test` | `.github/workflows/test.yml` | Runs the full unit/integration suite. |
| `lint` | `.github/workflows/lint.yml` | ESLint, prettier, and Go linters. |
| `security` | `.github/workflows/security.yml` | Dependency scanning and secret detection. |
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
| `build` | `CI / Web quality checks`<br>`prism-ci / build` | `.github/workflows/ci.yml`<br>`.github/workflows/prism-ci.yml` | Builds the web bundles, runs end-to-end packaging, and ensures the Prism service still compiles and ships images. |
| `test` | `Tests / test`<br>`Tests / site-playwright` | `.github/workflows/test.yml` | Node unit tests plus Playwright UI coverage. |
| `lint` | `lint-suite / eslint`<br>`lint-suite / go-vet`<br>`lint-suite / python-static-analysis` | `.github/workflows/lint.yml` | Static analysis across the JavaScript, Go, and Python surfaces that ship from this repo. |
| `security` | `Security • gitleaks / scan`<br>`Secret Scan / scan`<br>`PR Preview Containers / Vulnerability Scan` | `.github/workflows/gitleaks.yml`<br>`.github/workflows/secret-scan.yml`<br>`.github/workflows/preview-containers.yml` | Detects leaked credentials, enforces quick secret scans, and executes Grype against preview container images. |
| `sbom` | `PR Preview Containers / Generate SBOM` | `.github/workflows/preview-containers.yml` | Publishes an SPDX bill of materials for the preview container created from the PR. |
| `policy` | `policy-guard / org-guard` | `.github/workflows/policy-guard.yml` | Runs OPA checks to confirm branch protections and other guardrails have not drifted. |
| `eval` | `quality-gates / pulse-check` | `.github/workflows/quality-gates.yml` | Verifies the quick-release checklist inside the pull request description stays checked. |

## Updating the branch-protection script

Run `REQ_CHECKS='["CI / Web quality checks", ...]' repo-ops/enforce-branch-protection.sh`
if you need to pin the exact contexts above. The JSON array should contain the
**commit status names** (for example `CI / Web quality checks`), not just the alias.
