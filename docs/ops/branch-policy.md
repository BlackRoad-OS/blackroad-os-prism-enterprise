# Branch policy guardrails

This repository locks `main` behind strict branch protection and automation.
Keep this reference close when tuning GitHub settings so changes can be audited
in code review.

## Protection settings
- Require linear history.
- Enforce for administrators.
- Block force pushes and branch deletions.
- Require at least one approving review and code owners.
- Dismiss stale reviews when new commits land.
- Require the status checks listed in [`required-checks.md`](required-checks.md).

The script in the pull request description applies these settings via `gh api`.
Rerun it after rotating workflows or adjusting approval rules.

## Merge strategies
Only squash or rebase merges are allowed. Merge commits are disabled to keep
history clean for audit exports.

## Continuous verification
`.github/workflows/protect-branch-config.yml` fails if a pull request loosens
any of the guardrails above. If the workflow blocks your change, update this
reference and the workflow logic together so the protection stays intentional.
