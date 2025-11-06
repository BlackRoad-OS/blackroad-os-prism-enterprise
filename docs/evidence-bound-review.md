# **Evidence-Bound Review: blackroad-prism-console**

> **Goal** – Verify every README claim, script behavior, and architectural decision with **exact code references** (file + line range + SHA where applicable).
> **Instructions for responders** – Answer **each numbered item** with:
>
> 1. **File path** (e.g., `ops/install.sh`)
> 2. **Line range** (e.g., `L42-48`)
> 3. **Quoted code snippet** (indented)
> 4. **Commit SHA** (if historical) or `N/A`
> 5. **Brief explanation** (1–2 sentences)

---

## **Path & Environment Handling**

1. **Exact search command & false-positive guard**
   In `ops/install.sh`, quote the *exact* `find` (or equivalent) command and the surrounding lines (±5). Explain how it avoids false positives if multiple sub-projects contain `server_full.js` (e.g., first hit only, parent check, path allowlist).

2. **Non-overwrite guarantees**
   README claims “nothing overwrites your existing code.”
   Paste the conditional guards (`if [[ -f … ]]`, `test -e`, etc.) from both `ops/install.sh` and `tools/dep-scan.js` that enforce this, with line ranges.
   If a merge routine replaces guards, quote it and show how it avoids destructive writes.

---

## **Dependency Scanner**

3. **Import / require patterns**
   Paste the exact regex or parser logic used to detect `require()` and `import … from …`.
   Confirm whether dynamic `import()` is handled and cite the pattern / AST rule or TODO comment.

4. **`package.json` merge behavior**
   When merging into an existing `package.json`, does `dep-scan.js` preserve `scripts`, `engines`, `workspaces`?
   Paste the merge function and show a minimal before/after example proving custom keys are retained.

---

## **LLM Stubs & Naming**

5. **Duplication is intentional**
   Provide `git log --stat` output (last 3 commits) for `srv/lucidia-llm/` and `srv/lucia-llm/`.
   Include SHAs, authors, file stats, and any commit message referencing “backward compatibility.”

6. **Host / port & TLS**
   Paste lines from `srv/lucidia-llm/app.py` (or `main.py`) that set `host="127.0.0.1"` and `port=8000`.
   Include any commented-out TLS or `.env` configuration block.

---

## **Timeline & Alpha Status**

7. **Why still Alpha**
   List open GitHub issues tagged `alpha-blocker` (issue #, title, labels).
   If the label was renamed, include the rename link.

8. **Alpha badge provenance**
   Identify the commit SHA that added the Alpha badge in `README.md`, link the PR, and quote at least two review comments that approved it.

---

## **Mining & Leaderboards**

9. **CSV field validation**
   In `scripts/build_leaderboards.py`, show the `csv.DictReader` setup and validation for `energy_usage_kwh`.
   Paste the conditional(s) / type-cast logic.

10. **Missing energy values**
    Show how missing or non-numeric `energy_usage_kwh` rows are handled (default 0.0, skip, or error).
    Include any log message or exception path.

---

## **Dev Container & Cross-Platform**

11. **dockerDesktopContext fallback**
    In `.devcontainer/devcontainer.json`, show the `dockerContext` value.
    If it references `dockerDesktopContext`, explain the Linux fallback or paste the error string users see.

12. **SSH mounting**
    Does the devcontainer mount `~/.ssh` for Git? Paste the `mounts` entry and note any flags or feature guards.

---

## **Performance & Bots**

13. **Treasury-BOT stub**
    Locate `bots/treasury_bot.py` and paste the `run()` method body that returns placeholder data for `bench:run`, including return type/shape.

14. **Append safety for `memory.jsonl`**
    Show the function writing to `memory.jsonl`. Paste any file-lock (`flock`, `fcntl`, `portalocker`) or atomic-write logic. If none, quote the append call to prove no lock exists.

---

## **Security & Secrets**

15. **Stripe raw body**
    In `srv/blackroad-api/server_full.js`, paste the middleware that keeps `req.rawBody` for Stripe signatures (e.g., `express.raw({type:'application/json'})`).
    Include the package name and version from `package.json`.

16. **LLM stub binding is local**
    Confirm the `uvicorn.run(..., host="127.0.0.1", port=8000)` line (path + lines). State if it’s hard-coded or `.env`-configurable.

---

## **CI / CD & Sync Scripts**

17. **`DROPLET_HOST` SSH command**
    In `codex/jobs/blackroad-sync-deploy.sh`, paste the `ssh -o StrictHostKeyChecking=no` line and the remote “refresh” command.

18. **No hidden `git push`**
    Paste results of:

    ```bash
    grep -R "git push" codex/
    grep -R "git push" scripts/
    ```

    Confirm only the Codex job pushes and `scripts/blackroad_sync.sh` is log-only.

---

## **Program Board & Scheduling**

19. **13-week bucket math**
    In `cli/console.py`, paste the datetime math mapping ISO dates → 13-week buckets (with rounding logic and base epoch). Include an example if present.

20. **Snapshot atomicity**
    For `backup:snapshot`, show the file-write sequence (temp file → write → flush → final move). Paste calls like `NamedTemporaryFile`, `os.replace`, or `shutil.move`. If not atomic, note current behavior.

---

### ✅ **Good answers must:**

* Cite **file paths + line ranges** for every snippet
* Include **commit SHAs / PR links** for history questions
* Say “No” openly when a feature doesn’t exist, with a TODO or issue link

---

**Deployment steps**

1. Create a new GitHub issue → **“Evidence-Bound Review of blackroad-prism-console.”**
2. Paste this entire block.
3. Assign to the maintainer or open as a Q&A discussion.
4. (Optional) Add to PR template for reviews.

**Tag `@blackboxprogramming` when complete.**

---

That version will render cleanly in GitHub’s Markdown preview and keeps every technical demand intact.
