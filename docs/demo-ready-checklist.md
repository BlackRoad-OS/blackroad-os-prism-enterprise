# Demo-Ready Checklist (blackroad-prism-console)

**Scope:** make the repo demo-ready in one day: Memory API → Agent runtime/CLI → Console UI → Lineage/Consent → CI → Docs.
**Suggested file path:** `docs/demo-ready-checklist.md`
**Snapshot date:** 2025-11-06 (America/Chicago)

---

## 0) Ground rules

* [ ] **Single entrypoint for demo** (one command): either `docker compose up demo` or `make demo`.
* [ ] **App boots in < 60s** on a clean machine.
* [ ] **No secrets committed.** `.env.example` provided for every service, with required keys documented.

---

## 1) Environment & Runbook

* [ ] Confirm **Node ≥ 20** for API services.
* [ ] Confirm **Python ≥ 3.11** for the console/SDK.
* [ ] Provide **`.env.example`** files for each service with comments.
* [ ] Add **RUNBOOK.md** (root) with: prerequisites, one-liner start, smoke tests, and common failures.

---

## 2) Memory API (Cecilia)

**Paths (expected):** `srv/blackroad-api/memory/`
**Goal:** a minimal, test-covered, documented memory service with healthchecks.

* [ ] `npm ci` works cleanly in service dir.
* [ ] `npm run memory:server` boots; **`/health` returns 200**.
* [ ] Database init and persistence verified (SQLite or configured DB).
* [ ] **Tests green**: `npm test` (Jest or equivalent) with one integration test hitting `/health` and one CRUD happy path.
* [ ] **README.md** in service folder: setup, env vars, curl examples, error codes.
* [ ] **Dockerfile** + optional `docker compose` service. Healthcheck added.
* [ ] Add **OpenAPI (YAML or JSON)** stub describing `/health`, `/api/memory/index`, `/api/memory/search`.

**Smoke commands:**

```bash
curl -sS localhost:PORT/health | jq .
node scripts/seed-memory.js  # optional: seeds a few docs
curl -sS -X POST localhost:PORT/api/memory/index -d @sample.json -H 'Content-Type: application/json'
```

---

## 3) Agent Registry & CLI

**Paths (expected):** `prism/prismsh.js`, `bots/`
**Goal:** discover agents, import without side-effects, run a basic ask/spawn.

* [ ] **Imports fixed** in `bots/` (no missing modules/typos).
* [ ] `node prism/prismsh.js --help` prints usage.
* [ ] **Smoke test:** programmatically import every agent and construct once without network calls.
* [ ] Provide `scripts/smoke-agents.js` that logs agent names and init status.
* [ ] Add `npm run agents:smoke` (or `make agents:smoke`).

**Minimal test (example):**

```js
// tests/agents.import.test.js
const fs = require('fs');
const path = require('path');

test('every agent imports without side effects', () => {
  const agentsDir = path.join(__dirname, '..', 'bots');
  for (const file of fs.readdirSync(agentsDir)) {
    if (!file.endsWith('.js')) continue;
    const mod = require(path.join(agentsDir, file));
    expect(mod).toBeDefined();
  }
});
```

---

## 4) Console UI (Streamlit or Web App)

**Paths (expected):** `console/` or repo root with `main.py`
**Goal:** modular app structure with a boot test and one page wired to the Memory API.

* [ ] Refactor into **pages / components / services** (per open refactor idea).
* [ ] `streamlit run main.py` boots without exceptions.
* [ ] **Page:** *Memory Browser* — search box → calls Memory API → renders results.
* [ ] **Page:** *Lineage & Consent* — renders consent JSON + lineage summary (read-only).
* [ ] Add **pytest boot test** that imports app factory and asserts it builds.

**Minimal boot test (example):**

```python
# tests/test_app_boot.py
import importlib

def test_app_imports():
    importlib.import_module('main')
```

---

## 5) Lineage, Consent & Policy Surfacing

**Paths (expected):** `prism/README.md`, `consent.json`, lineage summaries

* [ ] Store **`consent.json`** and **lineage summary** in a stable location under `prism/`.
* [ ] Expose read-only **“Consent & Lineage”** panel in console with download buttons.
* [ ] Add a **Make target** (or script) to regenerate lineage summaries after runs.
* [ ] Document **what is logged** (who/what/when/why) and opt-out behavior.

---

## 6) CI: build, test, lint

**Goal:** Red/Green feedback on PRs.

* [ ] GitHub Actions workflow `ci.yml` with matrix jobs:

  * [ ] **Memory API:** `npm ci`, `npm test`, eslint/format check.
  * [ ] **Console/SDK:** `pytest -q`, `ruff`/`flake8` or `black --check`.
* [ ] Status badges in README.

**CI scaffold (example):**

```yaml
name: ci
on: [push, pull_request]
jobs:
  node:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci --workspace srv/blackroad-api/memory
      - run: npm test --workspace srv/blackroad-api/memory
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest -q
```

---

## 7) Docs: README & Demo Script

* [ ] **Root README** gains a 90-second Quickstart:

  1. Clone → `make demo` (or `docker compose up demo`).
  2. Open Console at `http://localhost:8501`.
  3. Run `agents:smoke` and search memory.
* [ ] **`DEMO_SCRIPT.md`** (root): step-by-step storyboard with copy-pasta commands and screenshots checklist.
* [ ] Link to **API README** and **Console README** from root.

---

## 8) Release & Tagging

* [ ] Tag **`v0.1.0-prealpha`** after CI is green.
* [ ] Create **GitHub Release**: notes include what works, known limitations, and how to file issues.

---

## 9) Risk fixes (must-do before demo)

* [ ] Fix any known **import/indentation** errors in `bots/` and `main.py`.
* [ ] Ensure at least **one happy-path E2E**: index → search → display in console.
* [ ] Add **fallbacks** for missing env vars (clear error messages, no hard crashes).

---

## 10) Optional niceties

* [ ] **OpenAPI UI** (Redoc/Swagger) for the Memory API.
* [ ] **Telemetry opt-in** with a simple metrics counter and privacy note.
* [ ] **Sample dataset** (`samples/`) to showcase search and lineage.

---

## Appendix A: Suggested Make targets

```Makefile
.PHONY: demo dev ci test lint

demo: ## one-shot demo run
	@echo "Starting memory + console"
	# e.g., docker compose up memory console

agents\:smoke:
	node scripts/smoke-agents.js

ci:
	npm --prefix srv/blackroad-api/memory ci && npm --prefix srv/blackroad-api/memory test
	pytest -q

lint:
	npx eslint srv/blackroad-api/memory || true
	black --check . || true
```

## Appendix B: Commit & PR ritual

```bash
git checkout -b chore/demo-checklist
mkdir -p docs
cp THIS_FILE docs/demo-ready-checklist.md
git add docs/demo-ready-checklist.md
git commit -m "docs: add demo-ready checklist"
git push -u origin chore/demo-checklist
# Open PR titled: "docs: demo-ready checklist (v0.1.0-prealpha)"
```

---

### Definition of Done (Demo)

* [ ] One command boots the stack.
* [ ] Memory API responds and indexes at least one document.
* [ ] Console loads, can search, and shows lineage/consent.
* [ ] CI green; release tagged `v0.1.0-prealpha`.
