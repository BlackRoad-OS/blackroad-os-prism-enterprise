# BlackRoad.io — Dependency & Ops Bundle

Date: 2025-08-22

Requires Node.js 20 or later.

This bundle is a **drop-in helper** to resolve “missing dependencies etc.” without requiring
connector access. Push it into your working copy, then run one script on the server to scan
your API, install missing npm packages, set up env defaults, and (optionally) boot a local
LLM stub on port **8000** if none is running.

> **Heads-up from the maintainer:** I'm still getting everything set up and I'm honestly not a
> strong coder yet. Thank you for your patience if anything here is rough around the edges —
> I'm doing my best and truly sorry for any bumps along the way.
## Note on GitHub Copilot agent UI

The Codespaces chat quick-actions are provided by GitHub Copilot's agent features and are
controlled by the Copilot service (not repo files). See `COPILOT_SETUP.md` and
`.github/copilot-instructions.md` for guidance to enable and tune Copilot agent behavior.

**What’s included**

- `ops/install.sh` — one-shot setup for `/srv/blackroad-api` (or detected API path)
- `tools/dep-scan.js` — scans JS/TS for `require()`/`import` usage and installs missing packages
- `tools/verify-runtime.sh` — quick health checks (API on 4000, LLM on 8000)
- `srv/blackroad-api/.env.example` — sample env for your Express API
- `srv/blackroad-api/package.json.sample` — a safe starter if your API has no package.json
- `srv/lucidia-llm/` — minimal FastAPI echo stub (only used if you don’t already run an LLM on 8000)
- `srv/lucia-llm/` — same stub (duplicate dir name for compatibility with earlier scripts)

Date: 2025-08-22

This bundle is a **drop-in helper** to resolve “missing dependencies etc.” without requiring
connector access. Push it into your working copy, then run one script on the server to scan
your API, install missing npm packages, set up env defaults, and (optionally) boot a local
LLM stub on port **8000** if none is running.

**What’s included**

- `ops/install.sh` — one-shot setup for `/srv/blackroad-api` (or detected API path)
- `tools/dep-scan.js` — scans JS/TS for `require()`/`import` usage and installs missing packages
- `tools/verify-runtime.sh` — quick health checks (API on 4000, LLM on 8000)
- `srv/blackroad-api/.env.example` — sample env for your Express API
- `srv/blackroad-api/package.json.sample` — a safe starter if your API has no package.json
- `srv/lucidia-llm/` — minimal FastAPI echo stub (only used if you don’t already run an LLM on 8000)
- `srv/lucia-llm/` — same stub (duplicate dir name for compatibility with earlier scripts)

> Nothing here overwrites your existing code. The scripts are defensive: they detect paths,
> **merge** deps, and only generate files if missing.

---

## Quick start

**On your workstation**

1. Unzip this at the **root of your working copy** (where your repo root lives).
2. Commit and push.

**On the server**

## Recovery & cleanup runbook

Need to investigate or recover from cleanup operations? Follow the consolidated triage→handoff flow in [`docs/mainline-cleanup.md`](docs/mainline-cleanup.md).

**On your workstation**

1. Unzip this at the **root of your working copy** (where your repo root lives).
2. Commit and push.

**On the server**

```bash
cd /path/to/your/working/copy
sudo bash ops/install.sh
bash tools/verify-runtime.sh
```

- The installer will:
  - Locate your API (prefers `./srv/blackroad-api`, then `/srv/blackroad-api`, else searches for `server_full.js`)
  - Create `package.json` if missing and **auto-install** any missing npm packages it finds
  - Create `.env` from the example if missing and generate strong secrets
  - Ensure your SQLite file exists (defaults to `blackroad.db` inside the API dir if `DB_PATH` is not set)
  - Check if `127.0.0.1:8000` is serving `/health`. If not, it prints a one-liner to launch the stub.

## Git workflow

When you're ready to share changes:

1. Stage your updates:
   ```bash
   git add -A
   ```
2. Commit with a clear message:
   ```bash
   git commit -m "feat: describe your change"
   ```
3. Push the branch:
   ```bash
   git push origin <branch-name>
   ```
4. Open a Pull Request and review the CI results.

## Mining progress & leaderboards

Track miner activity, crown trophy holders, and celebrate "green wins" with the
new leaderboard tooling bundled in this repo:

1. Log each mined block in [`logs/blocks.csv`](logs/blocks.csv). Keep the header
   row and append one line per block with the timestamp, block ID, miner name,
   energy usage (kWh), and fees earned (USD).
2. Refresh the leaderboard outputs by running:
   ```bash
   python3 scripts/build_leaderboards.py
   ```
   This generates `leaderboard.md` for humans and
   `leaderboard_snapshot.json` for downstream tools.
3. Tweak thresholds or rename trophies via
   [`config/leaderboard_config.json`](config/leaderboard_config.json). The
   script merges missing keys with sensible defaults, so only override what you
   need.

Every push that touches the CSV, config, or script automatically rebuilds the
leaderboard through the `leaderboard-refresh` GitHub Action to keep things
up-to-date.

## Developing with VS Code and Docker on macOS

## Developing with VS Code and Docker on macOS

1. Start [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac/).
2. Install [Visual Studio Code](https://code.visualstudio.com/) and the **Dev Containers** extension.
3. Open this repository in VS Code and select **Reopen in Container** to use `.devcontainer/devcontainer.json`.
4. Once the container is running, use the integrated terminal to run commands like `npm install`, `npm run lint`, or `npm test`.

---

## Performance

```bash
python -m cli.console bench:run --name "Treasury-BOT" --iter 30 --warmup 5
python -m cli.console slo:report
python -m cli.console slo:gate --fail-on regressions
```

---

## Notes & assumptions

- Stack recorded in memory (Aug 2025): SPA on `/var/www/blackroad/index.html`, Express API on port **4000**
  at `/srv/blackroad-api` with SQLite; LLM service on **127.0.0.1:8000**; NGINX proxies `/api` and `/ws`.
- This bundle does **not** ship `node_modules/` (native builds vary by machine). Instead, it generates
  and installs what’s actually needed by **scanning your sources**.
- If your API already has `package.json`, nothing is overwritten; missing deps are added.
- If you maintain your API directly under a different path, run the scanner manually, e.g.:
  ```bash
  node tools/dep-scan.js --dir /path/to/api --save
  ```

If anything looks off, run `bash tools/verify-runtime.sh` and share the output.

## Subscribe API

Environment variables for Stripe integration:

- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_STARTER_MONTHLY`
- `STRIPE_PRICE_PRO_MONTHLY`
- `STRIPE_PRICE_INFINITY_MONTHLY`
- `STRIPE_PRICE_STARTER_YEARLY`
- `STRIPE_PRICE_PRO_YEARLY`
- `STRIPE_PRICE_INFINITY_YEARLY`
- `STRIPE_PORTAL_RETURN_URL` (optional)

Example calls:

```bash
## Notes & assumptions

- Stack recorded in memory (Aug 2025): SPA on `/var/www/blackroad/index.html`, Express API on port **4000**
  at `/srv/blackroad-api` with SQLite; LLM service on **127.0.0.1:8000**; NGINX proxies `/api` and `/ws`.
- This bundle does **not** ship `node_modules/` (native builds vary by machine). Instead, it generates
  and installs what’s actually needed by **scanning your sources**.
- If your API already has `package.json`, nothing is overwritten; missing deps are added.
- If you maintain your API directly under a different path, run the scanner manually, e.g.:
  ```bash
  node tools/dep-scan.js --dir /path/to/api --save
  ```

If anything looks off, run `bash tools/verify-runtime.sh` and share the output.

## Testing

- `npm test` runs the smoke test harness (`tests/smoke.test.mjs`).
- `npm run test:jest` executes the Jest integration suite with `NODE_ENV` preloaded to `test` via `tests/jest.setup.js`.

## Subscribe API

Environment variables for Stripe integration:

- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_STARTER_MONTHLY`
- `STRIPE_PRICE_PRO_MONTHLY`
- `STRIPE_PRICE_INFINITY_MONTHLY`
- `STRIPE_PRICE_STARTER_YEARLY`
- `STRIPE_PRICE_PRO_YEARLY`
- `STRIPE_PRICE_INFINITY_YEARLY`
- `STRIPE_PORTAL_RETURN_URL` (optional)

Example calls:

```bash
curl http://localhost:4000/api/subscribe/config
curl -H "Cookie: brsid=..." http://localhost:4000/api/subscribe/status
curl -X POST http://localhost:4000/api/subscribe/checkout \
  -H "Content-Type: application/json" \
  -d '{"planId":"pro","interval":"month"}'
curl -H "Cookie: brsid=..." http://localhost:4000/api/subscribe/portal
# Webhooks are received at /api/stripe/webhook and must include the Stripe signature header.
# The middleware stack must expose the raw JSON payload (e.g., `express.raw({ type: 'application/json' })`)
# ahead of the route so Stripe signature verification can read `req.rawBody`.
```

## Unified Sync Pipeline

Use `scripts/blackroad_sync.sh` to drive a chat-style deployment flow.
Example:

```bash
./scripts/blackroad_sync.sh "Push latest to BlackRoad.io"
```

The script also understands:

- "Refresh working copy and redeploy"
- "Rebase branch and update site"
- "Sync Salesforce -> Airtable -> Droplet"

---

## Visual Hardware Guides

- [Pepper's Ghost Cube Calibration](docs/guides/peppers-ghost-calibration.md) — 5-minute tune-up checklist for crisp, centered holographic projections.

It pulls from GitHub, triggers connector webhooks, updates a Working Copy checkout, and
executes a remote refresh command on the droplet.

### BlackRoad Sync CLI

`codex/tools/blackroad_sync.py` scaffolds a chat-friendly pipeline that mirrors
commands like "Push latest to BlackRoad.io" or "Refresh working copy and
redeploy". Each sub-command currently logs the intended action:

```bash
python codex/tools/blackroad_sync.py push
python codex/tools/blackroad_sync.py refresh
python codex/tools/blackroad_sync.py rebase
python codex/tools/blackroad_sync.py sync
```

Extend the script with real webhooks, Slack posts, or droplet deployments as
needed. For example, `scripts/blackroad_ci.py` will post connector sync
updates to Slack when a `SLACK_WEBHOOK_URL` environment variable points to an
incoming webhook.

---

## Codex Deploy Flow

`codex/jobs/blackroad-sync-deploy.sh` provides a chat-focused pipeline tying
together git pushes, connector syncs, working-copy refreshes and server deploys.
Typical usage:

```bash
# commit local changes, push and deploy to the droplet
bash codex/jobs/blackroad-sync-deploy.sh push-latest "chore: update"

# refresh the iOS Working Copy checkout and redeploy
bash codex/jobs/blackroad-sync-deploy.sh refresh

# rebase current branch onto origin/main then deploy
bash codex/jobs/blackroad-sync-deploy.sh rebase-update

# run Salesforce → Airtable → Droplet syncs
bash codex/jobs/blackroad-sync-deploy.sh sync-connectors
```

It honours environment variables like `DROPLET_HOST`,
`WORKING_COPY_PATH`, and `SLACK_WEBHOOK` for remote access and
status notifications.

# BlackRoad Prism Console

A Python 3.11+ bot orchestration framework for enterprise operations.

## Architecture
[console] → [orchestrator] → [bots]
                ↓
         memory.jsonl

## Quick Start
```bash
# Install
pip install -r requirements.txt

# List available bots
python -m cli.console bot:list

# Create and route a task
python -m cli.console task:create --goal "Build Q3 cash forecast"
python -m cli.console task:route --id <TASK_ID> --bot "Treasury-BOT"

# View task history
cat memory.jsonl | jq
```

## Core Concepts

- **Bots**: Autonomous agents with missions, KPIs, guardrails
- **Tasks**: Work units routed to appropriate bots
- **Orchestrator**: Routes tasks, enforces policy, logs everything
- **Memory**: Append-only audit trail in JSONL format

## Modules

See [docs/MODULES.md](docs/MODULES.md) for an overview of every operational module.

## Creating Custom Bots

See [docs/BOT_DEVELOPMENT.md](docs/BOT_DEVELOPMENT.md) for guidance on extending the platform.

## Configuration

Configuration formats and examples live in [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Security

The complete security model is documented in [docs/SECURITY.md](docs/SECURITY.md).

## Development

Developer workflow, testing, and contribution expectations are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Merge Queue Primer

Learn how to keep `main` green and releasable with serialized merges in [docs/MERGE_QUEUE_PRIMER.md](docs/MERGE_QUEUE_PRIMER.md).

## Project Status

⚠️ **Alpha Stage**: This project is under active development. The core orchestration 
framework is functional, but APIs may change. Tool adapters are currently stubbed and 
make no external calls for safety during development.

We welcome feedback and contributions! See CONTRIBUTING.md for guidelines.
---

## Codex Deploy Flow

`codex/jobs/blackroad-sync-deploy.sh` provides a chat-focused pipeline tying
together git pushes, connector syncs, working-copy refreshes and server deploys.
Typical usage:

```bash
# commit local changes, push and deploy to the droplet
bash codex/jobs/blackroad-sync-deploy.sh push-latest "chore: update"

# refresh the iOS Working Copy checkout and redeploy
bash codex/jobs/blackroad-sync-deploy.sh refresh

# rebase current branch onto origin/main then deploy
bash codex/jobs/blackroad-sync-deploy.sh rebase-update

# run Salesforce → Airtable → Droplet syncs
bash codex/jobs/blackroad-sync-deploy.sh sync-connectors
```

It honours environment variables like `DROPLET_HOST`,
`WORKING_COPY_PATH`, and `SLACK_WEBHOOK` for remote access and
status notifications.

- **/geodesic**: Compute Fubini–Study distance `d_FS = arccos(|⟨ψ|φ⟩|)` and sample the **CP² geodesic** points between |ψ₀⟩ and |ψ₁⟩.

## Codex Sync Helper

Use `scripts/blackroad_sync.py` for chat-driven CI/CD tasks. It can commit and
push changes, refresh a working copy, rebase branches, or stub out connector
sync jobs.

Examples:

```bash
scripts/blackroad_sync.py push -m "feat: update site"
scripts/blackroad_sync.py refresh
scripts/blackroad_sync.py sync-connectors
```

## Backbone Equations Reference

See [docs/blackroad-equation-backbone.md](docs/blackroad-equation-backbone.md) for a curated list of one hundred foundational equations across mathematics, physics, computer science, and engineering.

_Last updated on 2025-09-11_

## Prism Developer Mode

Start the development server:

```bash
cd prism/server
npm install
npm run dev
```

Run the web console with Approvals panel:

```bash
cd apps/prismweb
npm install
npm run dev
```

## Program Board

The CLI exposes a lightweight portfolio view that persists to `program/board.json`.
Example:

```bash
python -m cli.console program:add --id P001 --title "APAC Launch" --owner "Regional-Ops" --bot "Regional-Ops-BOT" --start 2025-10-01 --due 2026-01-15
python -m cli.console program:list
python -m cli.console program:roadmap
```

Roadmap output is rendered as an ASCII Gantt chart with 13 week buckets.

## Dependencies & Scheduling

Tasks may depend on other tasks and be scheduled for a specific time.  The
polling scheduler will run tasks whose dependencies are complete:

```bash
python -m cli.console scheduler:run --every-seconds 5
```

Metrics about dependency blocks and schedule SLAs are written to
`orchestrator/metrics.jsonl`.

## CSV Import/Export

Bulk task management is supported with CSV files.  Columns:

`id, goal, context_json, depends_on_csv, scheduled_for_iso, bot`

```bash
python -m cli.console task:import --csv samples/sample_tasks.csv
python -m cli.console task:export --csv out.csv
```

Sample files live under `samples/`.

## Retail Industry Pack

The repository ships with a minimal retail example consisting of two bots:

- **Merchandising-BOT** – plans seasonal assortments from sales history.
- **Store-Ops-BOT** – generates labor plans and checklists for promotions.

Fixtures are under `fixtures/retail/` and an example workflow is available at
`examples/retail_launch.md`.
## Performance & Caching

The console includes a small pluggable cache with in-memory and file backends.
Cache usage is transparent to bots that perform deterministic computations.

## Scenario Simulator

A lightweight engine can execute multi-step scenarios and collect results.  Two
scenarios are bundled for demos.

Example:

```bash
python -m cli.console sim:list
python -m cli.console sim:run --id finance_margin_push
```

## TUI

A minimal text UI is available for demonstrations:

```bash
python -m cli.console tui:run
```

```
+--------------------+
| Bots | Tasks | Log |
+--------------------+
|        demo        |
+--------------------+
```

## Backups

Local snapshots can be created and restored using:

```bash
python -m cli.console backup:snapshot --to backups/demo
python -m cli.console backup:restore --from backups/demo
```
