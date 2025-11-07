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
