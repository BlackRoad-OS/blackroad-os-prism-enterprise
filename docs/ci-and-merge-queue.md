# CI & Merge Queue

This repository hosts the BlackRoad Prism Console frontend. The automation below prepares it for strict CI checks and a label-driven merge queue.

## Stack summary

- Frontend: React + Vite workspace under `frontend/` using Node.js 20 and npm workspaces.
- Tests: `npm run test` currently executes the Vite build output; expand with unit/integration coverage as they become available.

## Workflows

### CI (`.github/workflows/ci.yml`)

- Triggers on pull requests targeting `main` and pushes to `main`.
- Runs the **Frontend (Node 20)** job, which:
  - Checks out the repository.
  - Sets up Node.js 20 with npm caching for `package-lock.json` and `frontend/package-lock.json`.
  - Installs workspace dependencies via `npm ci`.
  - Builds the application with `npm run build`.
  - Executes `npm run test` (currently a build surrogate until dedicated tests are defined).
- The resulting check name is `CI / Frontend (Node 20)`. Protect `main` by requiring this check to pass.

### Deploy (`.github/workflows/deploy.yml`)

- Triggers only on pushes to `main`.
- Repeats a fresh checkout, Node.js setup, dependency install, and build before any release logic runs.
- Targets the `production` environment so that approvals can be required in the GitHub UI.
- Replace the TODO step with the actual deployment (container publish, infrastructure apply, etc.) once the release path is finalized.
- Keep this workflow gated behind the same branch protections and merge queue so production deploys only happen from vetted, green builds.

## Pull request expectations & merge queue

Apply this instruction block to pull requests so all automation stays aligned:

```
@copilot @dependabot @blackroad @cadillac @codex @lucidia @cecilia @gitguardian @blackboxprogramming @slackbot @blackroadagents

I can’t merge right now. Please: 
1) set up tests, 2) run full CI, 3) fix failing checks and review comments, 4) re-run CI, 5) add/keep `queue:ready` when green. 
Block prod deploys until protections are strict and all checks pass. Thanks.
```

### Merge queue flow

1. Create a feature branch, push commits, and open a pull request against `main`.
2. The `CI / Frontend (Node 20)` check must finish green. Address any lint/test/build failures before proceeding.
3. Obtain the necessary code review approvals (if required by branch protection rules).
4. When CI is green and feedback is resolved, apply the `queue:ready` label.
5. GitHub’s merge queue or auto-merge (configured in repository settings) will merge the PR when it reaches the front of the queue and passes final checks.

### Repository settings checklist

- Require pull requests before merging into `main`; disable direct pushes for non-admins.
- Require the `CI / Frontend (Node 20)` check (and any future checks) to pass before merge.
- Optionally require at least one approving review.
- Configure the merge queue to react to the `queue:ready` label so that only reviewed, green PRs merge.
- Associate the `production` environment with deployment approvals to guard the release workflow.

Keeping these protections in place ensures production deploys only happen from code that has passed the full CI pipeline and entered the queue intentionally.
