# Manufacturing Routing

The manufacturing toolkit models deterministic routings and capacity
checks without external systems.

## Work centre catalog

* `python -m cli.console mfg:wc:load --file fixtures/mfg/work_centers.csv`
  normalises CSV data into `artifacts/mfg/routing/work_centers.json` with
  consistent skill lists and rate metadata.

## Routing definitions

* `python -m cli.console mfg:routing:load --dir fixtures/mfg/routings`
  parses YAML routings into an in-memory registry and persists
  `routings.json` for contract validation.
* `python -m cli.console mfg:routing:capcheck --item PROD-100 --rev B
  --qty 1000` emits capacity and labour-cost calculations per work
  centre and writes the result to
  `artifacts/mfg/routing/capcheck_<item>_<rev>.json`.
