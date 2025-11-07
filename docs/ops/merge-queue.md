# Merge queue runbook

This document converts the high-level guidance from `docs/MERGE_QUEUE_PRIMER.md`
into concrete commands and repository automation. Follow the steps below to roll
out branch protection, enable the merge queue, and keep the `queue:ready` label in
sync with passing checks.

## 1. Apply branch protection from the CLI

1. Authenticate `gh` with the repository (`gh auth status`).
2. Adjust the required contexts in `REQ_CHECKS` if needed (see
   `docs/ops/required-checks.md` for the canonical names).
3. Run the helper script from the repo root:

   ```bash
   REQ_CHECKS='["build","test","lint","security","sbom","policy","eval"]' \
     repo-ops/enforce-branch-protection.sh
   ```

   The script enforces:

   - Required status checks with strict mode enabled.
   - Required reviews with code-owner coverage and stale-review dismissal.
   - Linear history with squash or rebase merges only.
   - Automatic creation of the `queue:ready` label if it does not already exist.

   Re-run the script whenever check names change so branch protection stays in
   sync with the documentation.

## 2. Enable merge queue in the GitHub UI

1. Navigate to **Settings → General → Merge queue**.
2. Enable the merge queue and add a rule for the `main` branch that requires the
   `queue:ready` label before enqueueing.
3. Confirm that “Allow auto-merge” is on for squash or rebase merges only.

## 3. Keep the `queue:ready` label synchronized automatically

The workflow `.github/workflows/auto-queue-ready.yml` monitors pull requests and
check suites. It adds the `queue:ready` label when all required contexts succeed
and removes it when a check is missing, failing, or the pull request is marked as
Draft. No manual action is required besides ensuring the required checks list in
the workflow matches your policy.

## 4. Maintain required check documentation

The table in `docs/ops/required-checks.md` maps each alias (build, test, lint,
etc.) to the actual commit-status contexts emitted by CI. Update the document
whenever a workflow or job name changes so future automation stays aligned.

## 5. Operational tips

- **Watch the queue**: keep an eye on the merge queue badge in GitHub after each
  batch lands to make sure the tip of `main` stays green.
- **Debugging failures**: removing `queue:ready` ejects a PR from the queue.
  Re-apply after addressing flakiness or legitimate failures.
- **Expanding coverage**: when new surfaces require gating (for example, a new
  service or security scanner), add the check to the table and rerun
  `enforce-branch-protection.sh` with the updated `REQ_CHECKS`.
