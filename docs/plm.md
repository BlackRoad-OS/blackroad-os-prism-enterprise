# PLM Operations

The offline Product Lifecycle Management tooling ships deterministic
catalog and change-control workflows that run without external
dependencies.  Key entry points live in `plm/bom.py` and `plm/eco.py` and
are surfaced through the Typer console (`python -m cli.console`).

## Item and BOM catalog

* `python -m cli.console plm:items:load --dir fixtures/plm/items` loads
  CSV records into `artifacts/plm/items.json`.  Supplier strings may be
  delimited with `|` or `;`; they are normalised into arrays.
* `python -m cli.console plm:bom:load --dir fixtures/plm/boms` persists
  structured BOMs to `artifacts/plm/boms.json` and materialises a
  `where_used` lookup for downstream analytics.
* `python -m cli.console plm:bom:explode --item PROD-100 --rev A
  --level 2` emits a deterministic multi-level explosion that honours
  scrap percentages and writes the results to disk for contract
  validation.

## Engineering change control

* `python -m cli.console plm:eco:new --item PROD-100 --from A --to B
  --reason "Connector change"` creates a JSON + Markdown record under
  `artifacts/plm/changes`.
* `python -m cli.console plm:eco:impact --id ECO-00001` summarises cost
  deltas, newly introduced components, supplier risk and the downstream
  work centres that must absorb the change.  The analysis is persisted to
  `<change>_impact.json` for reporting pipelines.
* Releases (`plm:eco:release`) enforce dual approval for high-risk
  changes and honour SPC duty-of-care flags.  The Markdown summary is
  updated with the release timestamp for audit trails.
