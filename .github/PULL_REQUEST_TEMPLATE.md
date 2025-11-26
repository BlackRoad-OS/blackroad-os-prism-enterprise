<!-- Short, copyable PR template for contributors and automated agents -->

# Pull Request
## Summary
-

## Summary

Provide a short (1-2 line) summary of the change.
## Balance Note
- Impact across speed, safety, creativity, and care
# {EMOJI} {SHORT TITLE}

@Copilot @BlackRoadTeam @Codex @Cadillac @Lucidia @Cecilia @blackboxprogramming

### Quick pulse before we move
- **Context:** {1 line on what this PR handles}
- **Security sanity:** double-check creds/tokens/secrets are not in logs or configs.
- **Tests:** (re)run suites; focus on auth/permissions edges.
- **Merge plan:** if green, merge to `main` after review + sign-off.

## Checklist
- [ ] Tests added/updated (if applicable)
- [ ] No secrets/keys in diff (Gitleaks will run)
- [ ] CI green
- [ ] API /api/health returns 200
- [ ] Updated docs/tests as needed
- [ ] Does this change alter power distribution?

## Changes

- Files changed (bullet list):
- Why these changes were made:

## Checklist (required for PRs created by automation)

- [ ] Lint: `npm run lint` (document any auto-fixes)
- [ ] Tests: `npm test` (list failing tests if any)
- [ ] Dependency hygiene: if you added new imports, run `node tools/dep-scan.js --dir <package> --save` (commit only the tool output)
- [ ] Env vars: added/changed? If yes, update `srv/blackroad-api/.env.example` and document defaults
- [ ] Ports/compose changes? If yes, update `ops/install.sh` and `docker-compose*.yml`
- [ ] Secrets: no secrets in the diff

## Commands I ran locally

```
# Bootstrapped repo
bash ops/install.sh

# If touching server package (example):
node tools/dep-scan.js --dir srv/blackroad-api --save

# Tests & lint
npm test
npm run lint

# Quick runtime/health check
npm run health
bash tools/verify-runtime.sh
```

## Notes for reviewers

- Any non-obvious decisions or trade-offs
- If the change touches webhooks or payments (Stripe), validate signature handling and replay payloads in staging
<!--
PULL REQUEST TEMPLATE — BlackRoad Prism Console
Copy this checklist into your PR description and fill it out before requesting review.
-->

Short summary (1-2 lines):

Files changed and why (1-3 bullets):

---

Local commands I ran (copyable):

```bash
# Install / verify deps (run from repo root)
bash ops/install.sh

# In API: run tests and lint
cd srv/blackroad-api && npm test && npm run lint

# Start API (dev)
cd srv/blackroad-api && npm run dev

# Start frontend (dev)
npm run dev:site

# Optional: quick runtime verify
npm run health && bash tools/verify-runtime.sh
```

Env vars added? (yes/no):

If yes, update `srv/blackroad-api/.env.example` with names and defaults (brief description):

Ports/compose changes? (yes/no):

If yes, list changed files:

Security & secrets checklist:

- Did you avoid committing secrets? (yes/no)
- If credentials were required for local testing, were they set via env only? (yes/no)

Notes for reviewers / special instructions:

# Summary

## Quick pulse
- [ ] Impact assessed (customer, ops, or security)
- [ ] Risk call-out (low / medium / high)
- [ ] Rollback or feature flag noted

## Optional Ops
- [ ] Added or updated dashboards / alerts
- [ ] Announced in release notes or status channel
- [ ] Coordinated with on-call / runbook owners

## Next steps
- [ ] Follow-up issue linked (if needed)
- [ ] Docs updated or slated for update
- [ ] Tests or benchmarks captured

### Context
- Context: <!-- auto-filled by pr-automation -->
- What changed and why?
- Anything reviewers should focus on?
---

### Optional Ops/Infra Add-On
- **Security sweep:** confirm no creds/keys in configs.
- **Dependency freeze:** verify no surprise upgrades.
- **CI/CD check:** confirm pathing + env parity (test/stage/prod).
- **Telemetry watch:** monitor first deploy window for anomalies/drift.

# Testing

- Local build passes
- `npm run build` (site) / API boots
- E2E (Playwright) green

# Checklist

- Docs/README updated if needed
- No secrets committed
- Labels added (area/site, area/api, etc.)
**What**
- 

**Why**
- 

**Tests**
- 

**Screenshots**
- 

**Breaking Changes**
- [] Yes
- [] No

**Checklist**
- [ ] Tests added or updated
- [ ] Docs updated
- [ ] API `/api/health` returns 200 (if relevant)
- [ ] If touching workflows/scripts/infra: security reviewer added

> Comment `@codex fix comments` to trigger bot autofix.

---

### Next steps
- [ ] Confirm agent configs use least-privilege.
- [ ] Validate pipeline runs clean with expected outputs.
- [ ] Review deps + build logs for anything unexpected.
- [ ] Deploy to staging or target branch once cleared.

---

If anyone spots drift, lag, or something off — flag here before merge. Silence = go.
## User impact (1–2 sentences)
-

## Type
- [ ] feat
- [ ] fix
- [ ] chore
- [ ] docs
- [ ] refactor

## Area (pick one)
- [ ] API
- [ ] UI
- [ ] Ingest
- [ ] Infra
- [ ] Data/dbt

## Release note (short, public-facing)
- <!-- Keep to one bullet; plain English. Used verbatim in release notes -->

## Checklist
- [ ] Tests pass (CI ≤ 10 min)
- [ ] Docs/CHANGELOG updated if user-visible
- [ ] Feature flag default checked
## Summary
-

## Type
- [ ] feat
- [ ] fix
- [ ] chore
- [ ] docs
- [ ] refactor

## Screens / Evidence
-

## Checklist
- [ ] Tests pass (CI ≤ 10 min)
- [ ] Docs/CHANGELOG updated (if user-visible)
- [ ] Linked issues
