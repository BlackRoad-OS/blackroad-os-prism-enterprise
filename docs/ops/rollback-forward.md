# Rollback and Forward Strategies

The gated promotion workflows ship with pre-baked recovery paths so operators
can revert unhealthy releases without leaving GitHub Actions.

## Rollback script

`scripts/rollback.sh` abstracts the environment-specific commands:

- `--env preview` uses `flyctl deploy --image <previous>` to push the prior build
  back to `prism-console-preview`.
- `--env staging` and `--env production` invoke `aws ecs update-service
  --force-new-deployment` against the `prism-console-web` service in the
  appropriate cluster.

The script is invoked automatically by the reusable promotion workflows when a
canary or blue/green health check fails, and can be executed manually from a
terminal:

```bash
./scripts/rollback.sh --env staging --to-image ghcr.io/blackroad/prism-console:previous
```

## Canary rollback flow

`reusable-canary.yml` gradually increases traffic through `1,50,100` slices while
watching CloudWatch alarms. If any step fails the workflow posts a `Canary
Health` check with a failure conclusion and executes `scripts/rollback.sh
--env staging` to revert to the last known-good image.

## Blue/green fallback

`reusable-bluegreen.yml` deploys the green stack, validates probes, and cuts
traffic over. Failure at any stage marks the `BlueGreen Health` check as failed
and runs `scripts/rollback.sh --env production` to push the prior task
definition.

Both reusable workflows inherit secrets from `gate-and-promote.yml`, so the same
AWS and Fly credentials drive forward promotion and emergency rollback.
