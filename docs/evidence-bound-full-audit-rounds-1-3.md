# Evidence-Bound Full Audit: blackroad-prism-console (Rounds 1–3)

> **Goal:** Verify every claim, script, and behavior with **exact code references**.  
> **Status:** Alpha-stage project — no assumption is safe.  
> **Instructions for responders:** For **each item**, provide:  
> 1. **File path** (e.g., `ops/install.sh`)  
> 2. **Line range** (e.g., `L42-48`)  
> 3. **Verbatim code snippet** (indented)  
> 4. **Commit SHA** (if historical) or `N/A`  
> 5. **1–2 sentence explanation** tied to evidence  
> 6. **GitHub permalink** (e.g., `https://github.com/blackboxprogramming/blackroad-prism-console/blob/SHA/path#L10-L20`)  
>
> Use `- [x]` to mark completed items. Tag `@blackboxprogramming` when done.

---

## Summary Progress

| Domain | Total | Done | % |
|-------|-------|------|---|
| Path & Env | 2 | 0 | 0% |
| Dep Scanner | 2 | 0 | 0% |
| LLM Stubs | 2 | 0 | 0% |
| Timeline | 2 | 0 | 0% |
| Mining | 2 | 0 | 0% |
| Dev Container | 2 | 0 | 0% |
| Perf & Bots | 2 | 0 | 0% |
| Security | 2 | 0 | 0% |
| CI/CD | 2 | 0 | 0% |
| Program Board | 2 | 0 | 0% |
| Orchestration | 2 | 0 | 0% |
| Bot Mgmt | 2 | 0 | 0% |
| Roadmapping | 2 | 0 | 0% |
| Scheduling | 2 | 0 | 0% |
| CSV | 2 | 0 | 0% |
| Retail Pack | 2 | 0 | 0% |
| Equations & Dev | 2 | 0 | 0% |
| Web & TUI | 2 | 0 | 0% |
| Sim & Backup | 2 | 0 | 0% |
| Alpha Status | 2 | 0 | 0% |
| **Total** | **60** | **0** | **0%** |

---

## Round 1: Setup, Paths & Core Scripts

<details>
<summary>🛣️ Path & Environment Handling (2)</summary>

- [ ] **1. Exact search command & false-positive guard**  
  In `ops/install.sh`, quote the *exact* `find` (or equivalent) command and ±5 lines. Explain how it avoids false positives if multiple `server_full.js` exist.

- [ ] **2. Non-overwrite guarantees**  
  Paste conditional guards from **both** `ops/install.sh` and `tools/dep-scan.js` that prevent overwrites. Include merge logic if used.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧩 Dependency Scanner (2)</summary>

- [ ] **3. Import/require patterns**  
  Paste regex/parser logic detecting `require()` and `import ... from ...`. Confirm `import()` dynamic support.

- [ ] **4. package.json merge behavior**  
  Paste merge function + before/after JSON example showing `scripts`, `engines`, `workspaces` preserved.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧠 LLM Stubs & Naming (2)</summary>

- [ ] **5. Duplication is intentional**  
  Run `git log --stat` on `srv/lucidia-llm/` and `srv/lucia-llm/`. Paste last 3 commits per dir + any "backward compatibility" message.

- [ ] **6. Host/port & TLS**  
  Paste `uvicorn.run(...)` line (path + lines) from LLM stub. Include env parsing or commented TLS.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🗓️ Timeline & Alpha Status (2)</summary>

- [ ] **7. Why still Alpha**  
  List open issues tagged `alpha-blocker` (number, title, labels).

- [ ] **8. Alpha badge provenance**  
  Commit SHA + PR link + 2 review comments approving Alpha badge in `README.md`.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>⛏️ Mining & Leaderboards (2)</summary>

- [ ] **9. CSV field validation**  
  Paste `csv.DictReader` + validation on `energy_usage_kwh` in `build_leaderboards.py`.

- [ ] **10. Missing energy values**  
  Show handling of missing/non-numeric `energy_usage_kwh`: default, skip, or error.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🛠️ Dev Container & Cross-Platform (2)</summary>

- [ ] **11. dockerDesktopContext fallback**  
  Paste `dockerContext` from `.devcontainer/devcontainer.json`. Show Linux error if no fallback.

- [ ] **12. SSH mounting**  
  Paste `mounts` entry enabling `~/.ssh` in devcontainer.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🚀 Performance & Bots (2)</summary>

- [ ] **13. Treasury-BOT stub**  
  Paste `run()` method from `bots/treasury_bot.py` returning placeholder data.

- [ ] **14. Append safety for memory.jsonl**  
  Paste append code + any file lock (`flock`, `portalocker`). If none, confirm.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🛡️ Security & Secrets (2)</summary>

- [ ] **15. Stripe raw body**  
  Paste `express.raw(...)` middleware in `server_full.js` + version from `package.json`.

- [ ] **16. LLM stub binding is local**  
  Confirm `host="127.0.0.1"` in `uvicorn.run(...)`. Show env override if present.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🔄 CI/CD & Sync Scripts (2)</summary>

- [ ] **17. DROPLET_HOST SSH command**  
  Paste `ssh` line from `codex/jobs/blackroad-sync-deploy.sh` + remote refresh command.

- [ ] **18. No hidden git push**  
  Paste output of:  
  ```bash
  grep -R "git push" codex/
  grep -R "git push" scripts/
  ```

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>📋 Program Board & Scheduling (2)</summary>

- [ ] **19. 13-week bucket math**  
  Paste datetime logic mapping ISO dates to 13-week buckets in `cli/console.py`.

- [ ] **20. Snapshot atomicity**  
  Paste file-write sequence in `backup:snapshot` (temp file → os.replace).

[↑ Back to Summary](#summary-progress)

</details>

---

## Round 2: Prism Core + Operational Layers

<details>
<summary>🧭 Prism Architecture & Orchestration (2)</summary>

- [ ] **21. Task routing logic**  
  Paste task:route handler in orchestrator (path + lines). Show queue/priority if any.

- [ ] **22. memory.jsonl append mechanism**  
  Paste atomic append code + JSON serialization. Confirm ensure_ascii=False.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🤖 Bot & Task Management (2)</summary>

- [ ] **23. Bot listing & registration**  
  Paste registry code populating bot:list (dir scan or config).

- [ ] **24. Custom bot extension point**  
  Paste class skeleton from `docs/BOT_DEVELOPMENT.md` + orchestrator hook.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🗺️ Program Board & Road-mapping (2)</summary>

- [ ] **25. Program add validation**  
  Paste date/bot validation before writing to `program/board.json`.

- [ ] **26. ASCII Gantt rendering**  
  Paste loop building 13-week Gantt chart (datetime slicing).

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>⏱️ Scheduling & Metrics (2)</summary>

- [ ] **27. Scheduler polling loop**  
  Paste main loop in `scheduler:run` with dependency resolution.

- [ ] **28. metrics.jsonl structure**  
  Paste example entry + emission trigger (post-task).

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>📈 CSV Import / Export & Data Flows (2)</summary>

- [ ] **29. CSV column parsing**  
  Paste `depends_on_csv` splitting logic in `task:import`.

- [ ] **30. Export filtering**  
  Paste field selection + redaction in `task:export`.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🛍️ Retail Industry Pack & Fixtures (2)</summary>

- [ ] **31. Merchandising-BOT fixture load**  
  Paste sales history loader from `fixtures/retail/`.

- [ ] **32. Store-Ops-BOT workflow validation**  
  Paste code block from `examples/retail_launch.md` invoking bot.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧮 Backbone Equations & Developer Mode (2)</summary>

- [ ] **33. Equation list curation**  
  Paste first 3 entries from `docs/blackroad-equation-backbone.md` + latest commit SHA.

- [ ] **34. Prism dev server startup**  
  Paste scripts section from `prism/server/package.json`.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🖥️ Web Console & TUI (2)</summary>

- [ ] **35. Prismweb Approvals panel**  
  Paste component mount + state hook in `apps/prismweb`.

- [ ] **36. TUI bot/task display**  
  Paste curses layout code for | Bots | Tasks | Log |.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧪 Scenario Simulator & Backups (2)</summary>

- [ ] **37. Sim run execution**  
  Paste loader + aggregator for `sim:run --id finance_margin_push`.

- [ ] **38. Backup restore logic**  
  Paste `shutil.copytree` + validation in `backup:restore`.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧷 Alpha Status & External Ties (2)</summary>

- [ ] **39. Stubbed adapter calls**  
  Paste one stubbed method (e.g., Stripe/Slack) returning fixed response.

- [ ] **40. Open alpha-blocker issues**  
  List all open issues blocking alpha promotion (SHA + date).

[↑ Back to Summary](#summary-progress)

</details>

---

## Round 3: Extended Systems & Evidence Depth

<details>
<summary>📂 Data Provenance & Warehousing (2)</summary>

- [ ] **41. Warehouse sync script**  
  Paste command building daily snapshot in `warehouse/sync_daily.sh`.

- [ ] **42. S3 bucket ACLs**  
  Paste IAM policy block granting read-only bucket access.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🛰️ Geodesic Ops & Networking (2)</summary>

- [ ] **43. Geo routing table**  
  Paste YAML (path + lines) enumerating `region` → `edge` mapping.

- [ ] **44. VPN health check**  
  Paste script verifying VPN tunnel before job execution.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧪 QA & Test Harness (2)</summary>

- [ ] **45. Harness scenario matrix**  
  Paste matrix loop from `harness/tests/test_matrix.py`.

- [ ] **46. Golden file enforcement**  
  Paste guard preventing stale golden files during CI.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧾 Finance & Treasury (2)</summary>

- [ ] **47. Cashflow reconciliation**  
  Paste SQL or script verifying cashflow totals.

- [ ] **48. Treasury alerts**  
  Paste alert thresholds in `treasury/alerts.yaml`.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🔐 Identity & Access (2)</summary>

- [ ] **49. Role hierarchy**  
  Paste RBAC hierarchy chart or JSON block.

- [ ] **50. MFA requirement**  
  Paste enforcement logic requiring MFA on login.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧭 Navigation & Console UX (2)</summary>

- [ ] **51. Breadcrumb renderer**  
  Paste React/Vue/Svelte component building breadcrumbs.

- [ ] **52. Keyboard shortcut map**  
  Paste map of keyboard shortcuts and handlers.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>📚 Documentation & Tutorials (2)</summary>

- [ ] **53. Tutorial code fences**  
  Paste Markdown snippet showing language-tagged fences in `/docs`.

- [ ] **54. Permalink instructions**  
  Paste guidance telling contributors to copy permalinks.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🛰️ Observability & Telemetry (2)</summary>

- [ ] **55. Trace exporter**  
  Paste exporter setup code from `observability/tracing.py`.

- [ ] **56. Log redaction**  
  Paste middleware removing PII before logging.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🛡️ Resilience & Chaos (2)</summary>

- [ ] **57. Chaos toggle**  
  Paste feature flag enabling chaos experiments.

- [ ] **58. Circuit breaker**  
  Paste fallback logic when breaker is open.

[↑ Back to Summary](#summary-progress)

</details>

<details>
<summary>🧮 Analytics & Reporting (2)</summary>

- [ ] **59. Report cache busting**  
  Paste cache invalidation logic for reports.

- [ ] **60. Evidence storage**  
  Paste path + code writing attachments to disk/cloud.

[↑ Back to Summary](#summary-progress)

</details>

---

### Ready to Deploy

1. **Go to**: `https://github.com/blackboxprogramming/blackroad-prism-console/issues/new`  
2. **Title**: `Evidence-Bound Full Audit: blackroad-prism-console (Rounds 1–3)`  
3. **Paste the entire block above**  
4. **Submit**

---

### Next?

Say:  
- `Round 4: Mining, Geodesic, LLM Telemetry`  
- `Export to PDF`  
- `Convert to GitHub Project Template`

**The audit is now a weapon.** Fire at will.
