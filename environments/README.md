# Environment Manifests

This directory contains declarative manifests describing each externally accessible footprint.

| Name        | URL Pattern                           | Notes |
|-------------|----------------------------------------|-------|
| production  | https://blackroad.io                  | Primary customer-facing footprint with `www` alias. |
| staging     | https://dev.blackroadinc.us           | Release-candidate surface routed through the hub domain. |
| preview     | https://pr-<number>.dev.blackroad.io | Ephemeral per-PR previews served via the ECS/Fargate module. |

Each manifest is structured consistently so automation can discover and route deployments without manual configuration. Update these files when environments are added or modified.
