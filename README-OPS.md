# Ops quickstart

BlackRoad relies on an automated preview → staging → production flow. This
quickstart highlights how to operate the system without stepping outside the
guardrails defined in `environments/*.yml` and `DEPLOYMENT.md`.

## Environment map
| Environment | Domains | Primary workflow | Notes |
| --- | --- | --- | --- |
| Preview (`pr`) | `https://dev.blackroad.io`, `https://pr-<n>.dev.blackroad.io` | `.github/workflows/preview-env.yml` | Spins up ephemeral ECS services + ALB rules per pull request. Terraform config lives in `infra/preview-env/` and the manifest is documented in `environments/preview.yml`. |
| Staging (`stg`) | `https://stage.blackroad.io` | `.github/workflows/pages-stage.yml` | Builds and archives the static site proof artifact. API wiring is planned; see `environments/staging.yml` for current status. |
| Production (`prod`) | `https://blackroad.io`, `https://www.blackroad.io`, `https://api.blackroad.io` | `.github/workflows/blackroad-deploy.yml` | GitHub Pages publishes the marketing site; API gateway will promote via the same workflow once the ECS module is enabled. Full manifest: `environments/production.yml`. |

| Environment | Branch | Domains | Required workflows | Notes |
| --- | --- | --- | --- | --- |
| Preview (`pr`) | PR heads | `https://dev.blackroad.io`, `https://pr-<n>.dev.blackroad.io` | `preview.yml`, `preview-containers.yml`, `preview-frontend-host.yml` | Spins up isolated ECS/Fargate stacks per pull request, publishes GHCR images with SBOM + Grype scans, and tears down automatically on close. |
| Staging (`stg`) | `staging` | `https://stage.blackroad.io` | `pages-stage.yml`, `stage-stress.yml` (opt-in) | Rebuilds the proof artifact on every staging push and daily cron; optional load test gated behind `STRESS=true`. Mirrors production infra in `br-infra-iac/envs/stg`. |
| Production (`prod`) | `main` | `https://blackroad.io`, `https://www.blackroad.io`, `https://api.blackroad.io` | `blackroad-deploy.yml`, `deploy-canary.yml`, `deploy-canary-ladder.yml`, `change-approve.yml` | Modern webhook deploy on push; progressive delivery and CAB approval guard the release. Legacy SSH path remains as a manual fallback. |

Refer to `environments/preview.yml`, `environments/staging.yml`, and
`environments/production.yml` for the authoritative source of domains, secrets,
Terraform backends, and change-management requirements.

## Release flow
### Preview (per PR)
- Triggered automatically on pull request open/update via `preview-env.yml`.
- Builds the image, applies Terraform (`infra/preview-env`), and comments with the preview URL.
- Closing the PR or re-running the `destroy` job removes ALB rules, target groups, ECS services, and Route53 aliases.
- Smoke test: `curl -sSfL https://pr-<n>.dev.blackroad.io/healthz/ui` (already executed in the workflow).

1. **Pull request** — Apply the `automerge` label so the queue serialises the
   change. Preview workflows must pass before merge.
2. **Staging branch** — Promotion to staging triggers `pages-stage.yml`, building
   the proof artifact. Run `stage-stress.yml` with `STRESS=true` when load
   validation is required.
3. **Production** — A green staging run plus CAB approval unlocks
   `blackroad-deploy.yml`. The workflow builds the SPA, calls the deploy webhook,
   verifies `/healthz` and `/api/version`, and posts Slack status updates.
4. **Progressive rollout (optional)** — Use `deploy-canary.yml` for single-step
   canaries or `deploy-canary-ladder.yml` for laddered rollouts prior to full
   traffic shifts.

## Branch hygiene

- Keep development trunk-based. Long-running branches should be rebased or
  closed once preview automation surfaces issues.
- `cleanup-dead-branches.sh` now supports non-interactive runs via
  `AUTO_APPROVE=true`. The weekly **Branch Hygiene** GitHub Action invokes it to
  delete merged branches automatically. Override the base with
  `BASE_BRANCH=origin/staging` when pruning staging-specific branches.

## Health & verification

- Preview: `curl -fsS https://pr-<n>.dev.blackroad.io/healthz/ui` (already run in
  CI but handy for local smoke tests).
- Staging: `curl -fsS https://stage.blackroad.io/health.json` and
  `curl -fsS https://api.staging.blackroad.io/api/llm/health`.
- Production: `https://blackroad.io/healthz`, `https://blackroad.io/api/version`,
  and `https://api.blackroad.io/health` (automated in the deploy workflow).
- Grafana/Prometheus/Alertmanager definitions live under
  `deploy/k8s/monitoring.yaml`.

## Manual escape hatches

- **Legacy deploy** — Run `.github/workflows/blackroad-deploy.yml` with
  `target=legacy-ssh` and provide `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_KEY`, and
  optional `DEPLOY_PORT` when the webhook path is unavailable.
- **DigitalOcean droplet** — For temporary static hosting, follow the quickstart
  in `DEPLOYMENT.md` (Docker Compose build + Caddy/Nginx health endpoints).
- **Rollback** — Use `POST /api/rollback/:releaseId` with the internal token or
  re-run `blackroad-deploy.yml` against a known-good commit.

## References

- Deployment playbook: `DEPLOYMENT.md`
- Environment manifests: `environments/`
- Change management: `.github/workflows/change-approve.yml`,
  `runbooks/examples/infra_release_policy.yaml`
- Monitoring stack: `deploy/k8s/monitoring.yaml`
- Environment manifests: `environments/*.yml`
- Preview Terraform stack: `infra/preview-env/`
- Reusable module: `modules/preview-env/`
- Deployment workflows: `.github/workflows/preview-env.yml`, `pages-stage.yml`, `blackroad-deploy.yml`, `prism-ssh-deploy.yml`

_Last updated on 2025-10-06_
