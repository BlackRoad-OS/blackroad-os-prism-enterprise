# Architecture Decisions

This document records key architecture decisions made during Prism Console development and refactoring.

**Format:** Each decision includes context, decision, rationale, and consequences.

---

## ADR-001: Separate Databases for Prism Console API and Main API

**Date:** 2025-11-15
**Status:** ✅ ACCEPTED
**Context:** The codebase has two database schemas that appeared to conflict.

**Decision:**
- Prism Console API uses its own database (`prism.db`) with tables auto-created from SQLModel
- Main API uses separate database with SQL migrations in `db/migrations/`
- The two databases serve different purposes and should remain separate

**Rationale:**
- Separation of concerns: Prism focuses on observability, Main API focuses on user/wallet/ledger management
- Independent deployment: Prism Console API can be deployed without Main API
- Schema evolution: Changes to one don't break the other

**Consequences:**
- ✅ Clear boundaries between services
- ✅ Independent scaling and backup strategies
- ⚠️ Potential data duplication (e.g., agent registry exists in both)
- ⚠️ Cross-database queries require application-level joins

**See:** [docs/DATABASE.md](./DATABASE.md)

---

## ADR-002: Deprecate In-Repo RoadChain Service

**Date:** 2025-11-15
**Status:** 🔶 PROPOSED
**Context:** `services/roadchain/` is a prototype blockchain node with ephemeral in-memory state.

**Decision:**
- Deprecate `services/roadchain/` service in this repo
- Keep DB tables (`roadchain_*`) for integration with external RoadChain node
- Create thin client in Prism Console API to call external RoadChain API

**Rationale:**
- Current impl is prototype quality (no persistence, no tests, simplified consensus)
- RoadChain logic belongs in dedicated `roadchain` repo
- Prism should be a **client** of blockchain, not a blockchain node itself
- DB tables in `db/migrations/202501080000_roadchain.sql` are for **receipts/webhooks** from external ledger, not for running a node

**Consequences:**
- ✅ Clear separation: Prism = control plane, RoadChain = ledger
- ✅ Reduced codebase complexity in Prism repo
- ✅ External RoadChain can evolve independently
- ⚠️ Requires external RoadChain service to be deployed
- ⚠️ Migration path needed for any existing users

**Implementation Plan:**
1. Move `services/roadchain/` to `_trash/roadchain-deprecated/`
2. Add `DEPRECATED.md` explaining the decision
3. Create thin client in `services/prism-console-api/src/prism/integrations/roadchain_client.py`
4. Update docs

**Status:** Awaiting implementation

---

## ADR-003: Consolidate AutoPal Implementations

**Date:** 2025-11-15
**Status:** 🔶 PROPOSED
**Context:** Four AutoPal implementations exist across the codebase:
- `services/autopal/`
- `autopal/`
- `autopal-express/`
- `autopal_fastapi/`

**Decision:**
- Pick single canonical implementation (likely `autopal_fastapi/` or `services/autopal/`)
- Deprecate and move others to `_trash/`

**Rationale:**
- Maintenance burden: Four implementations means 4x the bugs and technical debt
- Confusion: Developers don't know which to use
- Likely cause: Iterative prototyping without cleanup

**Consequences:**
- ✅ Single source of truth
- ✅ Reduced maintenance burden
- ⚠️ Need to verify which impl is most complete before choosing

**Implementation Plan:**
1. Audit each implementation:
   - Check git history (`git log --oneline -- services/autopal/ autopal/ autopal-express/ autopal_fastapi/`)
   - Compare features
   - Check which is referenced in docs/configs
2. Pick canonical version
3. Move others to `_trash/autopal-{name}-deprecated/`
4. Update references in docker-compose, configs, docs

**Status:** Awaiting audit

---

## ADR-004: Consolidate Lucidia Services

**Date:** 2025-11-15
**Status:** 🔶 PROPOSED
**Context:** Lucidia logic is spread across 10+ directories:
- `services/lucidia_api/`
- `services/lucidia-cognitive-system/`
- `modules/lucidia/`
- `opt/blackroad/lucidia/`
- `alice_lucidia/`
- `lucidia/`
- `lucidia-llm/`
- `lucidia-monitor/`
- `lucidia_infinity/`
- `lucidia_math_forge/`
- `lucidia_math_lab/`
- etc.

**Decision:**
- Consolidate into:
  - `services/lucidia_api/` – Main FastAPI service
  - `modules/lucidia/` – Shared Python modules
  - External repo `lucidia` – Heavy inference/training workloads (if it exists)

**Rationale:**
- Current fragmentation makes it impossible to understand what Lucidia actually does
- Likely cause: Incremental development without consolidation
- Clear boundaries: Service (API) vs Library (modules) vs External (repo)

**Consequences:**
- ✅ Clear structure
- ✅ Easier to navigate
- ⚠️ Significant refactoring required
- ⚠️ Risk of breaking imports

**Implementation Plan:**
1. Map all Lucidia directories and their purposes
2. Categorize:
   - Active services → `services/lucidia_api/`
   - Reusable modules → `modules/lucidia/`
   - Standalone apps (monitor, lab) → `apps/lucidia-*/` or separate repos
   - Dead code → `_trash/`
3. Update imports across codebase
4. Test thoroughly

**Status:** Awaiting implementation

---

## ADR-005: Agent Event Ingestion API

**Date:** 2025-11-15
**Status:** 🔶 PROPOSED
**Context:** Agents have no clear endpoint to publish events to Prism Console API.

**Decision:**
- Implement `POST /api/agents/{id}/events` endpoint
- Accept standardized event schema (type, timestamp, message, meta)
- Store in `agentevent` table
- Optionally broadcast via SSE (like miner telemetry)

**Rationale:**
- Current gap: Miner telemetry works end-to-end, but agent events don't
- Agents need a way to report progress, errors, completions
- Web UI needs to display agent event history

**Consequences:**
- ✅ Complete observability for agents
- ✅ Consistent with miner telemetry pattern
- ⚠️ Requires agents to be updated to call this endpoint

**Implementation Plan:**
1. Add route in `services/prism-console-api/src/prism/main.py`
2. Define Pydantic schema for event payload
3. Write to `agentevent` table via `AgentRepository`
4. Optional: Broadcast via SSE for real-time updates
5. Update agent frameworks to call this endpoint

**Status:** Awaiting implementation

---

## ADR-006: Standardized Event Schema

**Date:** 2025-11-15
**Status:** 🔶 PROPOSED
**Context:** Different services emit events in different formats.

**Decision:**
- Define unified event schema:
  ```json
  {
    "id": "uuid",
    "type": "miner.sample | agent.event | roadchain.block_mined | ...",
    "source": "service_name",
    "timestamp": "ISO8601",
    "payload": { /* type-specific data */ }
  }
  ```
- Create JSON Schema + Pydantic models in `modules/events/`
- Enforce schema in SSE broadcaster

**Rationale:**
- Current: Each service has its own event format
- Goal: Unified event bus for cross-service observability
- Enables future MQTT/Kafka event streaming

**Consequences:**
- ✅ Consistent event format across services
- ✅ Easier to build event aggregation/analysis tools
- ⚠️ Breaking change for existing event consumers
- ⚠️ Requires migration plan

**Implementation Plan:**
1. Define schema in `schemas/events.json`
2. Create Pydantic models in `modules/events/events.py`
3. Update miner telemetry to use standardized format
4. Update agent events (once implemented) to use standardized format
5. Update SSE broadcaster to enforce schema

**Status:** Awaiting implementation

---

## Decision Template

```markdown
## ADR-XXX: Title

**Date:** YYYY-MM-DD
**Status:** 🔶 PROPOSED | ✅ ACCEPTED | ❌ REJECTED | ⚠️ DEPRECATED
**Context:** What is the issue that motivates this decision?

**Decision:** What is the change that we're proposing or have agreed to?

**Rationale:** Why did we choose this option over alternatives?

**Consequences:** What are the positive and negative outcomes?

**Implementation Plan:** (if applicable)
1. Step one
2. Step two

**Status:** Current implementation status
```

---

**Legend:**
- 🔶 PROPOSED – Under consideration
- ✅ ACCEPTED – Decision made and implemented
- ❌ REJECTED – Decision not pursued
- ⚠️ DEPRECATED – Decision superseded by newer decision

---

**Last Updated:** 2025-11-15
**Maintainer:** Cecilia (Cece) - Systems Architect
