# Finance Module

## Overview

Finance bots support treasury operations, cash management, and close automation.

## Bots

- **Treasury-BOT**
  - Mission: Deliver short- and mid-term cash visibility.
  - Inputs: Task goal, treasury configuration, historical cash positions.
  - Outputs: Forecast summaries, hedging recommendations, liquidity KPIs.
  - KPIs: Cash floor adherence, forecast accuracy, hedge coverage.
  - Guardrails: Offline calculations only, policy-bound hedging limits.
  - Handoffs: Treasury operations team for execution.

- **Close-BOT**
  - Mission: Coordinate monthly close workflows.
  - Inputs: Close calendar, variance thresholds, reconciliation checklists.
  - Outputs: Status updates, risk assessments, outstanding task list.
  - KPIs: Close duration, reconciliation completeness, flux anomalies.
  - Guardrails: Requires approvals for policy exceptions.
  - Handoffs: Controller organization.

## Commands

```bash
python -m cli.console task:create --goal "Generate 13-week cash view" --bot Treasury-BOT
python -m cli.console task:create --goal "Close status update" --bot Close-BOT
```

## Configuration Files

- `config/finance/treasury.yaml`: Treasury guardrails and thresholds.
- `config/close/calendar.yaml`: Close cadence and milestone definitions.

## Workflows

1. Create a treasury planning task.
2. Route to Treasury-BOT for analysis.
3. Review generated KPIs and hedging suggestions.
4. Capture approvals if required before execution.

## Examples

See `fixtures/finance/treasury_task.json` for a sample task payload used in tests.
