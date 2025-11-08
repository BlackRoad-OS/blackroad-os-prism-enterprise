# Release Approvals

The Gatekeeper approvals manifest (`config/approvals.json`) defines which roles
must sign off before an environment can promote:

- **staging** — `qa-signoff`
- **production** — `platform-lead`, `security`, `change-advisory`

Gate status queries (`GET /api/gate/status`) read the manifest and the recorded
approvals for the target commit (`data/approvals/<sha>.json`) to determine who is
pending. The `Approvals Gate` job in `gate-and-promote.yml` echoes the required
reviewers and surfaces a GitHub Check so PR authors can see what is blocking.

To add a new approver, update `config/approvals.json` and ensure a corresponding
reviewer or GitHub environment requirement exists. Gatekeeper will include the
new entry in its pending list until a deployment automation (or a manual update
of the approvals record) grants it.
