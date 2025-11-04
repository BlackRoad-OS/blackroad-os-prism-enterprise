# Deployment Guide

## Prerequisites

- Python 3.11+
- Access to target environment (staging or production)
- Configured environment variables for secrets (see CONFIGURATION.md)

## Single Deployment Script

All deployment actions are handled by `scripts/deploy.py`.

```bash
python scripts/deploy.py push --env staging
python scripts/deploy.py status --env staging
python scripts/deploy.py rollback --env production --release 2025.02.14
```

## Environments

| Environment | Purpose                | Notes                               |
|-------------|------------------------|-------------------------------------|
| staging     | Pre-production testing | Uses sandbox credentials            |
| production  | Live operations        | Requires change-management approval |

## Pipeline Overview

1. Run `make lint test` locally.
2. Commit and push to GitHub.
3. GitHub Actions executes the test workflow.
4. Trigger deployment via `python scripts/deploy.py push --env <env>`.
5. Monitor `python scripts/deploy.py status` until healthy.

## Rollback Procedure

1. Identify release ID using `python scripts/deploy.py status`.
2. Execute `python scripts/deploy.py rollback --env production --release <id>`.
3. Confirm system health metrics.
4. Document the incident in the change log.

## Post-Deployment Checklist

- [ ] Run smoke tests via `make test`.
- [ ] Verify audit log ingestion.
- [ ] Confirm bots respond to sample tasks.
- [ ] Update stakeholders via the comms channel.
