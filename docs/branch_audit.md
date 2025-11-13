# Branch Audit Utility

The repository already carries a historical **Branch Audit Report** but until
now required humans to cross-reference multiple git commands to regenerate the
numbers.  Run `tools/branch_audit.py` to get an up-to-date snapshot of remote
branch hygiene:

```bash
python tools/branch_audit.py --remote origin --base main
```

The script reports:

- Total number of remote branches under the chosen remote
- Counts (and percentages) of branches already merged into the base branch
- Counts of unmerged branches plus a table with the most recent unmerged work
  so the release team can prioritize reviews

Need structured data for reporting or dashboards? Use the JSON switch:

```bash
python tools/branch_audit.py --json > branch_report.json
```

The JSON payload mirrors the on-screen summary and includes timestamps,
authors, and commit subjects for the sampled unmerged heads.

Working from a detached mirror or sandbox without remote refs? Switch the
scope to local branches and point the base flag at your active branch:

```bash
python tools/branch_audit.py --scope local --base work
```

This is particularly handy in air-gapped development environments where only
local refs are available but you still want a quick hygiene report.
