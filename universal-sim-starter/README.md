# Universal Simulation Starter Pipeline

This module scaffolds a lightweight, automation-friendly pipeline that can orchestrate
PySPH and Taichi-MPM style simulations. The included stages generate deterministic stub
metrics when the heavy simulation engines are unavailable so the downstream comparison
and reporting steps remain functional inside CI environments.

## Layout

```
10_genesis/        # Generates per-variant outputs and a manifest
40_compare/        # Aggregates metrics for quick inspection
90_reports/        # Produces a Markdown summary of all runs
tools/             # Helper utilities and orchestration wrappers
Makefile           # Wiring for running the full pipeline locally
```

`10_genesis/variants.yaml` enumerates the default simulation scenarios. Each entry can
be extended with additional parameters or engines as the real simulations evolve.

## Quickstart

To execute the complete pipeline you can either use the Makefile:

```bash
make -C universal-sim-starter all
```

or run the convenience wrapper that chains every stage and performs validation:

```bash
python3 universal-sim-starter/tools/generate_outputs.py --force-stub
```

Use the `--force-stub` switch to ensure deterministic stub metrics even when PySPH or
Taichi-MPM are installed locally.

## Validation & Cleanup

After running the pipeline you can verify the artifacts (the target will rerun any
missing stages automatically) with:

```bash
make -C universal-sim-starter check
```

Temporary outputs live under `universal-sim-starter/outputs` and can be removed with:

```bash
make -C universal-sim-starter clean
```

This keeps local working trees tidy while allowing the generated reports to be reviewed
on demand.
