# Consent Protocol

The BlackRoad Prism Console requires explicit, revocable, and auditable consent
before any sensitive orchestration step can execute. The protocol is enforced by
the `orchestrator.consent` module and consumed by bots, routers, and the CLI.

## Core Concepts

- **ConsentRequest** – represents a negotiation between two agents. Each
  request records the initiating agent, the receiving agent, the consent type,
  scope restrictions, intended purpose, and optional duration. Requests are
  signed using the PS-SHA∞ scheme (SHA3-512 → SHA-512 → BLAKE2b) to guarantee
  tamper detection.
- **ConsentGrant** – encapsulates the approval of a request. Grants inherit the
  request scope, can be time-bounded, and may be flagged as revocable. Each
  grant stores its PS-SHA∞ signature and revocation metadata for audit trails.
- **ConsentRegistry** – manages lifecycle operations, persists every event to
  `orchestrator/consent.jsonl`, and performs validation checks before sensitive
  actions such as task assignment, memory writes, and bot hand-offs.

## Enforcement Points

1. **Task assignment** – `BaseBot.run` verifies that the task owner has granted
   a `task_assignment` consent covering the specific task ID before execution.
2. **Memory access** – `MemoryLog.append` and the router demand an active
   `data_access` consent prior to persisting any response.
3. **Collaboration / hand-off** – both the router and lineage tracker confirm a
   `collaboration` consent before lineage is recorded or artefacts are shared.

If any validation fails a `ConsentError` is raised and the operation aborts.

## CLI Commands

The Typer-based console exposes dedicated consent commands:

```bash
python -m cli.console consent:request --from TreasuryBOT --to ComplianceBOT \
    --type task_assignment --purpose "delegate regulatory review" --duration 4h \
    --scope task:Q4-FILING

python -m cli.console consent:grant --request req_ab12cd34 --expires-in 8h

python -m cli.console consent:revoke --grant grant_ef56gh78 --reason "completed"

python -m cli.console consent:audit --agent TreasuryBOT --limit 10
```

Every CLI action verifies the persisted log signatures and returns clear
identifiers for downstream automation.

## Example Scenarios

### 1. Treasury requests collaboration with Compliance

1. TreasuryBOT issues a `collaboration` request scoped to `task:SOX-2025` with a
   24-hour duration.
2. ComplianceBOT grants the request, adding the condition "share redacted
   forecasts only".
3. The registry logs the signed request and grant. Subsequent lineage writes are
   permitted until the 24-hour window expires.

### 2. S&OP revokes data access immediately after export

1. S&OP leadership requests `data_access` consent for SupplyChainBOT to export
   SKU inventory.
2. SupplyChainBOT grants a revocable consent with scope `inventory:*`.
3. After the export finishes, S&OP revokes the grant. Any further attempts to
   write into shared memory raise a `ConsentError`.

### 3. Finance grants standing task assignment to Treasury

1. Finance Operations issues a long-running `task_assignment` request covering
   all treasury tasks (`scope="*"`).
2. The consent is granted with a one-week expiry, allowing Treasury-BOT to
   accept assignments automatically.
3. An audit review a week later shows the request, grant, and auto-expiry in the
   JSONL log, satisfying compliance requirements.

## Auditing and Integrity

- Each log entry in `orchestrator/consent.jsonl` includes an entry signature that
  is recomputed when the registry loads. Any mismatch raises a `ConsentError`.
- `ConsentRegistry.audit(agent)` returns a chronological slice of the log for a
  specific agent, enabling real-time compliance dashboards.
- Revocations are logged with timestamps and optional reasons, providing a full
  narrative for governance teams.

## Developer Workflow

1. Use `ConsentRegistry.request_consent()` and `.grant_consent()` to bootstrap
   test fixtures.
2. Always call `ConsentRegistry.reset_default()` in tests when overriding the
   log path to prevent cross-test contamination.
3. Rely on the CLI commands for manual inspection or when integrating with CI
   pipelines.

By making consent a first-class requirement, the Prism Console enforces a clear
contract between agents and maintains an immutable audit trail for every
decision.

