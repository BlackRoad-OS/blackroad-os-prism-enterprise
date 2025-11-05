# Configuration Guide

## Directory Layout

```
config/
├── users.json
├── approvals.yaml
├── finance/
│   └── treasury.yaml
├── close/
│   └── calendar.yaml
└── supply/
    └── sop.yaml
```

## Users (`config/users.json`)

Defines operator roles and access levels.

```json
{
  "users": [
    {"id": "alice", "role": "finance", "permissions": ["task:create", "task:route"]},
    {"id": "sam", "role": "security", "permissions": ["policy:approve"]}
  ]
}
```

## Approvals (`config/approvals.yaml`)

```yaml
policies:
  treasury:
    requires_approval: true
    approvers:
      - cfo
    sla_hours: 8
  close:
    requires_approval: false
    approvers: []
```

## Finance (`config/finance/treasury.yaml`)

```yaml
cash_floor: 2500000
hedge_policies:
  - currency: EUR
    max_notional: 500000
  - currency: JPY
    max_notional: 750000
```

## Close (`config/close/calendar.yaml`)

```yaml
deadlines:
  - name: Pre-close reconciliation
    due_days_from_period_end: -5
  - name: Flux analysis
    due_days_from_period_end: 3
```

## Supply (`config/supply/sop.yaml`)

```yaml
planning_horizon_weeks: 12
inventory_targets:
  - sku: WIDGET-001
    min: 400
    max: 900
logistics_partners:
  - carrier: Acme Freight
    lanes: ["NA-EU", "NA-APAC"]
```

## Environment Variables

| Variable                 | Description                             |
|--------------------------|-----------------------------------------|
| `PRISM_SIGNING_KEY`      | Base64 encoded signing key for memory log |
| `PRISM_DATABASE_URL`     | Optional database URL for external store |
| `PRISM_DEPLOY_TOKEN`     | Credential for deployment automation     |

## Validation

Run `python -m cli.console config:validate` to ensure all files conform to the
Pydantic models defined in `config/models.py`.
