# Merge Queue Primer

This guide explains what merge queues are, why teams adopt them, and how to roll one out so that the `main` branch stays healthy and releasable.

---

## What a Merge Queue Does

- **Serializes merges to main**: Pull requests enter a queue and land one at a time instead of all at once.
- **Re-tests against the exact tip**: Each candidate merge creates a temporary branch that combines `main` with the PR. Continuous integration runs on that branch before landing.
- **Prevents green-then-red**: Because every PR is validated against the real merge target, `main` stays green instead of regressing after apparently green PRs.
- **Keeps main always releasable**: With a consistently green branch, you can cut releases at any time with confidence.

---

## When to Use a Merge Queue

Consider a merge queue when any of the following apply:

- Multiple PRs are in flight (even 5–10 per day can introduce races).
- CI runtime exceeds 5–10 minutes and you frequently see flakiness.
- You must keep `main` at release quality because deployments or compliance artifacts depend on it.

---

## Core Pieces

- **Queue**: A FIFO (or sometimes priority-aware) list of PRs that are ready to merge.
- **Eligibility gate**: Required checks, reviews, and labels must be satisfied before entering the queue.
- **Temporary merge branch**: Created per PR (or batch) to run CI on the exact merge candidate.
- **Auto-merge**: Successful CI results land automatically; failures bounce the PR without affecting `main`.

---

## Minimal, Battle-Tested Policy

- **Required checks**: Run the full test suite, linting, build, and security scans.
- **Required reviews**: At least one or two code owners must approve.
- **Protection**: Direct pushes to `main` are disallowed; only the queue merges.
- **No skipping CI**: Never bypass CI for a queued merge.
- **Flake strategy**: Auto-retry once; if the retry fails, eject the PR so the author can investigate.

---

## Example GitHub Setup

1. **Branch protection** (Settings → Branches → `main`):
   - Require status checks to pass.
   - Require PR reviews (including code owners if applicable).
   - Disable direct pushes.
2. **Enable auto-merge** in repository settings and choose "Squash" or "Rebase".
3. **Label & rule**:
   - Create a `queue:ready` label.
   - Use an automation (e.g., a merge queue action) that:
     - Adds PRs with `queue:ready` to the queue.
     - Creates a temporary merge branch such as `mq/<PR#>`.
     - Runs the full CI suite.
     - Merges on success and removes the label on failure.
4. **CI tips**:
   - Cache dependencies and parallelize end-to-end tests.
   - Keep fast gates (lint, type checks, unit tests) separate from longer suites, but require both for merge.

---

## House Rules That Keep Velocity High

- Keep PRs small (≤400 lines of code) for faster reviews and fewer conflicts.
- Only label PRs as ready when they are genuinely green and approved.
- Optionally define priority lanes (e.g., `priority:hotfix`) for urgent fixes.
- Eject failing PRs from the queue so authors can fix issues offline.

---

## Metrics to Watch

- **Lead time to merge**: Track queue wait plus CI runtime; aim for less than 2× the CI duration.
- **Queue length**: A long queue suggests adding CI capacity or splitting test shards.
- **Red rate on temporary branches**: High rates signal flaky tests that need attention.

---

## Why BlackRoad Teams Benefit

BlackRoad teams frequently ship AI-assisted PR bursts. A merge queue:

- Converts bursts of 60–100 PRs per week into a predictable merge stream.
- Protects compliance artifacts (OPA/Rego, IaC, templates) from regressions.
- Keeps `main` deployable so you can ship from trunk whenever you need.

---

## Next Steps

If you want hands-on help, draft:

- A branch protection checklist for copy/paste into repository settings.
- A GitHub Actions workflow that implements the queue with temporary branches.
- Labels and simple bot logic to gate on `queue:ready` and auto-retry once.

