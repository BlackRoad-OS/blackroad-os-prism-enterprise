# Prism Merge Queue

This repository ships with a lightweight, provider-agnostic merge queue that relies on GitHub for persistence and Slack for ChatOps.

## Components

| File | Purpose |
| --- | --- |
| `.github/workflows/merge-queue.yml` | Dispatches enqueue/dequeue events when labels change and provides a manual `tick` entry point. |
| `workers/queue-endpoint.ts` | Cloudflare Worker (or any `fetch` compatible runtime) that manages the queue, merges PRs, handles Slack slash commands, and appends to the audit trail. |
| `ops/queue.json` | Canonical queue state (`queue` array + `paused` flag). |
| `ops/audit.log.jsonl` | Append-only audit log; each line is JSON describing an action. |

## Required secrets / env vars

| Location | Key | Description |
| --- | --- | --- |
| GitHub Actions | `MQ_ENDPOINT` | HTTPS endpoint hosting the worker. |
| GitHub Actions | `MQ_TOKEN` | Shared secret for the worker (same value used by Slack). |
| Worker env | `MQ_TOKEN` | Shared secret used to authenticate requests from Actions and Slack. |
| Worker env | `GITHUB_TOKEN` | GitHub App token or PAT with `repo` scope that can read/write contents, comment on PRs, and use the GraphQL API. |
| Worker env | `REPO` | `<owner>/<repo>` of this repository. |
| Worker env (optional) | `DEFAULT_BRANCH` | Default branch name; falls back to `main`. |
| Worker env (optional) | `MERGE_METHOD` | GitHub merge method (`merge`, `squash`, or `rebase`). Defaults to `squash`. |

## Slack slash command

Point a slash command such as `/mergeq` at the worker URL. The worker accepts standard Slack form payloads and recognises the shared token.

Supported commands:

```
/mergeq pause
/mergeq resume
/mergeq status
/mergeq unqueue 123
/mergeq revert last
/mergeq revert 456
```

## Operations flow

1. A PR labelled `ready-to-merge` triggers the GitHub Action, which POSTs `/enqueue`.
2. The worker updates `ops/queue.json`, appends an audit entry, and comments on the PR.
3. A manual or scheduled `workflow_dispatch` hits `/tick`, which merges the head of the queue when checks are green and the PR still has the label.
4. Slack commands can pause/resume the queue, remove PRs, or open revert PRs using the GitHub GraphQL `revertPullRequest` mutation.
5. All state changes are recorded in `ops/audit.log.jsonl` and mirrored on the affected PRs for traceability.

## Rollout checklist

1. Deploy `workers/queue-endpoint.ts` to Cloudflare Workers (or a similar runtime) with the required env vars.
2. Create the Slack slash command, forwarding to the same endpoint and including the shared token.
3. Add the GitHub secrets `MQ_ENDPOINT` and `MQ_TOKEN`.
4. Ensure required checks are configured on the default branch so `mergeable_state` becomes `clean` only when it is safe to merge.
5. (Optional) Schedule the `merge-queue` workflow to `workflow_dispatch` regularly or trigger manually after queue changes.
6. Label PRs `ready-to-merge` to enqueue them.

## Audit schema reference

Each line in `ops/audit.log.jsonl` is a JSON object shaped like:

```json
{
  "ts": "2024-03-30T18:25:43.511Z",
  "actor": "automation",
  "type": "enqueue",
  "pr": 123,
  "details": { "message": "optional free-form data" }
}
```

Common `type` values:

- `enqueue`, `unqueue`
- `merge`, `merge-error`
- `pause`, `resume`
- `missing-label`, `pr-closed`
- `revert`
- `error`

This structure makes it easy to stream the audit log to any downstream analytics system if needed.
