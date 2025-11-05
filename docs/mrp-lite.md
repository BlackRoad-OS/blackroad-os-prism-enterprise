# MRP Lite

The lightweight MRP planner consumes deterministic CSV inputs and writes
artifacts under `artifacts/mfg/mrp/`.

* Demand: `python -m cli.console mfg:mrp --demand demand.csv --inventory inventory.csv --pos open_pos.csv`
  nets demand against inventory and open purchase orders.
* Plan output includes the planned quantity, release lead-time offsets
  (derived from the item catalog), and a kitting list generated via the
  BOM explosion helpers.
* For every planned item a `kitting_<item>.csv` is emitted so warehouse
  teams can pick component quantities without additional systems.
