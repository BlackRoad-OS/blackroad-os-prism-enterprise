# Security Policy

## Supported Versions

The `main` branch of this repository is actively supported with security updates.

## Reporting a Vulnerability

Please report security vulnerabilities via a private issue (label: security) or email [security@blackroad.io](mailto:security@blackroad.io). Provide enough detail to reproduce the issue but do not include personal data or secrets. We will respond as quickly as possible and work with you to resolve the issue. Please do not disclose vulnerabilities publicly until they have been addressed.

We run advisory scans (Semgrep, Trivy, Gitleaks, Checkov, CodeQL) behind feature flags to help ensure safety for all users. This repository is a read-only curated list mirror and has no code execution surface.

## Runtime Security

- API responses enforce HTTP Strict Transport Security (HSTS) with subdomain preload to ensure encrypted connections.
- Responses include `Referrer-Policy: no-referrer` to prevent leaking potentially sensitive URLs.
- The `Secret Scanning Guardrail` workflow queries GitHub's secret scanning API on every push, pull request, and daily schedule to ensure newly detected credentials are triaged quickly.

## Secret Management Policy

- Do not commit secrets. Use `.env` files locally, GitHub Encrypted Secrets in CI/CD, and runtime injection for production systems.
- Scope tokens and API keys with least privilege, and rotate them every 90 days or immediately after any suspected exposure.
- If a secret leaks, follow the incident playbook: (a) revoke/rotate at the provider, (b) scrub the git history, (c) redeploy or restart affected services, and (d) document the post-incident steps in the remediation PR.

## CI/CD Hardening After GhostAction

Recent supply-chain campaigns (for example, the 2025 "GhostAction" incident that exfiltrated repository secrets through malicious GitHub Actions workflows) reaffirmed that CI pipelines are high-value targets. To reduce blast radius inside this repository we enforce the following practices:

- **Default read-only tokens** – Set the repository's default `GITHUB_TOKEN` permissions to read-only and only elevate access per job when required. This ensures unexpected workflows cannot push commits, create releases, or tamper with issues by default.
- **Ephemeral cloud credentials via OIDC** – Prefer GitHub's OIDC integration to request short-lived, audience-scoped credentials from our cloud providers instead of storing long-lived secrets in Actions. IAM trust policies must restrict which repositories, branches, and environments can request tokens.
- **Action pinning and allow-lists** – While referencing third-party actions by immutable commit SHA is the recommended security practice, most workflows currently use tag-based references (e.g., `actions/checkout@v4`). This is a known gap and tracked for remediation. We enforce an allow-list at the organization level to prevent retagging attacks or execution of unreviewed actions.
- **Workflow change monitoring** – Alert on new or modified workflow files, and require review before merging to mainline branches. Unexpected additions (for example, anonymous curl uploads) should trigger incident response.
- **Network egress controls** – Block unapproved outbound destinations from CI runners where possible and log HTTP(S) requests to detect credential exfiltration attempts.

The security team reviews GitHub Actions logs weekly and after every critical alert, rotating any cloud or package registry credentials if anomalous access is detected. Following the GhostAction retro, we also run quarterly tabletop exercises that simulate credential exfiltration to verify notification paths, and we re-validate OIDC trust relationships any time new environments are added.
