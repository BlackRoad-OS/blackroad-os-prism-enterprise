# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities via a private issue (label: security) or email [security@blackroad.io](mailto:security@blackroad.io). Provide enough detail to reproduce the issue but do not include personal data or secrets. We will respond as quickly as possible and work with you to resolve the issue. Please do not disclose vulnerabilities publicly until they have been addressed.

We run advisory scans (Semgrep, Trivy, Gitleaks, Checkov, CodeQL) behind feature flags to help ensure safety for all users. This repository is a read-only curated list mirror and has no code execution surface.

## Automation and Workflow Security

- All GitHub Actions workflows run with read-only `GITHUB_TOKEN` scopes by default. Jobs that require elevated permissions explicitly request them and surface the scope in `AUTOMATION_STATUS.md`.
- The `main-automation-orchestrator` workflow coordinates lint, web, and CLI jobs and emits telemetry to the BlackRoad observability bus. It is the only workflow permitted to write back to the repository and uses OIDC (`id-token: write`) for ephemeral credentials.
- Automation pull requests must be reviewed by both `@BlackRoadTeam` and `@Cadillac` per the CODEOWNERS entry.
- Weekly drift detection enforces integrity of `.github/workflows` by alerting on untracked changes.
- Optional Slack, ClickUp, and Asana notifications allow human operators and service agents to receive state changes without exposing credentials in workflow definitions.

## Runtime Security

- API responses enforce HTTP Strict Transport Security (HSTS) with subdomain preload to ensure encrypted connections.
- Responses include `Referrer-Policy: no-referrer` to prevent leaking potentially sensitive URLs.
- The `Secret Scanning Guardrail` workflow queries GitHub's secret scanning API on every push, pull request, and daily schedule to ensure newly detected credentials are triaged quickly.

## Secret Management Policy

- Do not commit secrets. Use `.env` files locally, GitHub Encrypted Secrets in CI/CD, and runtime injection for production systems.
- Scope tokens and API keys with least privilege, and rotate them every 90 days or immediately after any suspected exposure.
- If a secret leaks, follow the incident playbook: (a) revoke/rotate at the provider, (b) scrub the git history, (c) redeploy or restart affected services, and (d) document the post-incident steps in the remediation PR.
- Use OIDC-backed federation (GitHub Actions → cloud provider) instead of long-lived deployment keys wherever possible. Token lifetimes should be capped at 1 hour.
- Track all rotations in `RUNBOOK.md` with ticket links and effective timestamps. Emergency rotations require owner sign-off within 24 hours.

## SOPS Encryption Workflow

- Store persistent secrets as encrypted SOPS documents (`*.sops.yaml`, `*.sops.json`, etc.) using `age` recipients from the platform keyring. Plaintext `.env` files are forbidden in the repository and the `ops/security/check_env_secrets.sh` gate enforces this automatically.
- A small number of historical `.env` files remain for documentation inside `_trash/`, `etc/blackroad/`, `lucidia/`, `ops/backup/`, `opt/blackroad/`, and `tools/tools-adapter/`. Do not modify them—migrate to SOPS equivalents before making any changes.
- To create a new secret file:
  1. `sops --encrypt --age $(cat sops/age.pub) secret.env > secret.env.sops`
  2. Commit only the `.sops` output and reference it in the deployment runbook.
- To rotate a value: `sops secret.env.sops` → edit → save; the encryption metadata is updated automatically.
- Never share age private keys in chat or tickets. Use the secure key escrow described in `SECURITY_BASELINE.md` for recovery.

Report issues privately to security@blackroad.io. Do not disclose publicly until fixed. This project operates in offline environments; please avoid any network-based exploits in reports.
