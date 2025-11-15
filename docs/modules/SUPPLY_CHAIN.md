# Supply Chain Module

## Overview

The supply chain module powers sales and operations planning (S&OP), inventory
balancing, and logistics coordination.

## Bots

- **S&OP-BOT**
  - Mission: Align demand, supply, and inventory over the planning horizon.
  - Inputs: Task goal, S&OP configuration, fixture data.
  - Outputs: Allocation plans, risk alerts, suggested logistics actions.
  - KPIs: Service level, inventory turns, capacity utilisation.
  - Guardrails: Deterministic simulations only, no live system calls.
  - Handoffs: Supply chain planning team.

## Commands

```bash
python -m cli.console task:create --goal "Replan S&OP for Q3" --bot S&OP-BOT
```

## Configuration Files

- `config/supply/sop.yaml`: Planning horizons, target inventory, logistics partners.

## Workflows

1. Load fixture data via `fixtures/supply/sop_example.json`.
2. Create a routing task for S&OP.
3. Review recommended allocations and logistics notes.
4. Export artifacts from `artifacts/<task_id>/` for distribution.

## Examples

- `fixtures/supply/sop_task.json`: Example task payload for tests.
