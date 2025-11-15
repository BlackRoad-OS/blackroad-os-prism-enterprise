# SPC and Yield

## Statistical process control

`python -m cli.console mfg:spc:analyze --op OP-200 --window 50` consumes
fixture CSV samples, calculates classical X-bar/R style thresholds and
persists artefacts under `artifacts/mfg/spc/`:

* `report.json` with the deterministic summary (mean, sigma, rule hits).
* `charts.csv` and `charts.md` for ASCII-friendly visualisation.
* `findings.json` for contract validation and automation gates.
* `blocking.flag` whenever a 3σ violation is detected; ECO releases read
  this flag to enforce duty-of-care.

## Yield and cost of quality

`python -m cli.console mfg:yield --period 2025-09` materialises a yield
summary with FPY/RTY metrics, Markdown output, and a Pareto of defects.

`python -m cli.console mfg:coq --period 2025-Q3` aggregates ledger-like
fixtures into prevention/appraisal/failure buckets for operations
reporting.
