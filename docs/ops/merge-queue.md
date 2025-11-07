# Merge queue primer

The merge queue keeps `main` deployable by serialising merges behind a
`queue:ready` label. This doc captures the human steps that pair with the
automation.

## Enablement checklist
1. Navigate to **Settings → General → Merge queue** and flip the toggle to
   enable it for `main`.
2. Add a branch rule that requires the `queue:ready` label before entry.
3. In **Settings → Actions → General**, allow GitHub Actions to create and
   approve pull requests so bots can manage rebases.

## Label flow
- **Added automatically** — `.github/workflows/auto-queue-ready.yml` adds the
  `queue:ready` label when all required status checks are green.
- **Removed automatically** — The same workflow removes the label if any check
  regresses to `failure`, `cancelled`, or `timed_out`.
- **Manual override** — Maintainers can add or remove `queue:ready` manually,
  but only do so when the PR is demonstrably safe to ship.

## Operational tips
- Watch the queue status after large batches. Retry flaky checks or drop the
  PR from the queue to avoid blocking `main`.
- Keep branch protection checks in sync with
  [`docs/ops/required-checks.md`](required-checks.md).
- If a required workflow produces matrix jobs, expose a final gate job that
  reports one of the canonical names (`build`, `test`, `lint`, `security`,
  `sbom`, `policy`, `eval`).
- When temporarily disabling a flaky check, remove it from branch protection and
  update [`docs/ops/required-checks.md`](required-checks.md) in the same PR.
