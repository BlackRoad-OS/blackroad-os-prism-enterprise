# Database Architecture

**Last Updated:** 2025-11-15

## Overview

The BlackRoad Prism Console uses **two separate databases** for different services. Understanding this separation is critical for development and deployment.

---

## Database Separation

### 1. Prism Console API Database

**File:** `prism.db` (SQLite) or configured Postgres DB
**Location:** Auto-created by Prism Console API service
**Managed By:** SQLModel (auto-create tables from Python models)

**Purpose:** Stores Prism-specific observability and orchestration data

#### Tables

| Table | Schema | Purpose |
|-------|--------|---------|
| `agent` | `services/prism-console-api/src/prism/models.py` | Agent registry for console |
| `agentevent` | `services/prism-console-api/src/prism/models.py` | Agent event log |
| `runbook` | `services/prism-console-api/src/prism/models.py` | Runbook catalog |
| `metric` | `services/prism-console-api/src/prism/models.py` | Dashboard metrics |
| `minersample` | `services/prism-console-api/src/prism/models.py` | Miner telemetry timeseries |
| `setting` | `services/prism-console-api/src/prism/models.py` | Key-value config |

**Connection:**
- Default: `sqlite:///prism.db` (relative to service root)
- Production: Set `PRISM_API_DB_URL` to Postgres URL

**Table Creation:**
Tables are auto-created on startup via `SQLModel.metadata.create_all(engine)` in `services/prism-console-api/src/prism/main.py:191`.

---

### 2. Main BlackRoad API Database

**File:** Configured by main blackroad-api service (not Prism Console API)
**Location:** Managed by `os/docker/services/blackroad-api/`
**Managed By:** SQL migrations in `db/migrations/*.sql`

**Purpose:** Stores user accounts, wallets, ledger integration, and cross-service data

#### Tables (from `db/migrations/0001_init.sql`)

| Table | Purpose |
|-------|---------|
| `users` | User accounts (email, password_hash, role) |
| `agents` | Agent catalog (different schema than Prism's `agent` table) |
| `agent_logs` | Agent log entries |
| `wallets` | Wallet balances |
| `transactions` | Wallet transactions |
| `notes` | User notes |
| `tasks` | Task tracking |
| `timeline_events` | Event timeline |
| `commits` | Git commits log |

#### RoadChain Tables (from `db/migrations/202501080000_roadchain.sql`)

| Table | Purpose |
|-------|---------|
| `roadchain_accounts` | EVM address linking (user_id ↔ evm_address) |
| `roadchain_limits` | Rate limits (proofs_published per month) |
| `roadchain_receipts` | Ledger receipts (usage, manifest, badge) |
| `roadchain_merkle_roots` | Daily merkle roots for batch anchoring |
| `roadchain_webhook_log` | Webhook events from external ledger |

---

## Schema Differences: `agent` vs `agents`

**IMPORTANT:** These are **two different tables** for **two different purposes**:

### Prism Console API: `agent` Table

**File:** `services/prism-console-api/src/prism/models.py`

```python
class Agent(SQLModel, table=True):
    id: str  # Primary key
    name: str
    domain: str  # E.g., "infrastructure", "data", "security"
    status: str  # E.g., "active", "idle", "offline"
    memory_used_mb: float
    last_seen_at: datetime
    version: str
```

**Purpose:** Track agents for **observability in Prism Console**

**Used By:**
- `GET /api/agents` – List agents
- `GET /api/agents/{id}` – Get agent details
- Web UI: Agent catalog view

---

### Main API: `agents` Table

**File:** `db/migrations/0001_init.sql`

```sql
CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  status TEXT DEFAULT 'idle',
  heartbeat_at TEXT,
  memory_path TEXT,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**Purpose:** Agent **registration and lifecycle management** for main API

**Used By:**
- Main blackroad-api service (`os/docker/services/blackroad-api/`)
- Agent registration workflows
- Cross-service agent discovery

---

## Why Two Agent Tables?

**Separation of Concerns:**

1. **Prism Console** focuses on **observability and monitoring**
   - Real-time status (`memory_used_mb`, `last_seen_at`)
   - Domain classification
   - Version tracking

2. **Main API** focuses on **lifecycle and registration**
   - Slugs for routing
   - Heartbeat tracking
   - Notes and memory paths
   - Created/updated timestamps

**Benefits:**
- Prism Console API can be deployed independently
- Schema evolution doesn't break cross-service contracts
- Prism can aggregate data from multiple sources (not just main API)

---

## Migration Management

### Prism Console API

**NO MIGRATIONS NEEDED** – Tables are auto-created from models.

To change schema:
1. Edit `services/prism-console-api/src/prism/models.py`
2. Restart service
3. SQLModel will recreate tables (for new DBs) or require manual migration (for existing DBs)

**Production Recommendation:** Use Alembic for migrations:
```bash
cd services/prism-console-api
poetry add alembic
alembic init alembic
# Configure alembic/env.py to use SQLModel metadata
# Generate migrations: alembic revision --autogenerate -m "description"
# Apply migrations: alembic upgrade head
```

---

### Main API

**USES SQL MIGRATIONS** in `db/migrations/`

Migration files are applied in order:
1. `0001_init.sql` – Base schema
2. `202501080000_roadchain.sql` – RoadChain tables
3. `20250824_lucidia_brain.sql` – Lucidia tables
4. etc.

**To add a migration:**
1. Create `db/migrations/YYYYMMDDHHMM_description.sql`
2. Use timestamp prefix to ensure ordering
3. Test migration on dev DB before production

---

## Connection Strings

### Prism Console API

**Environment Variable:** `PRISM_API_DB_URL`

**Examples:**
```bash
# SQLite (default for local dev)
PRISM_API_DB_URL=sqlite:///prism.db

# PostgreSQL (production)
PRISM_API_DB_URL=postgresql://user:pass@localhost:5432/prism

# PostgreSQL with connection pooling
PRISM_API_DB_URL=postgresql+asyncpg://user:pass@localhost:5432/prism
```

---

### Main API

**Environment Variable:** `DATABASE_URL`

**Example:**
```bash
DATABASE_URL=postgresql://blackroad:password@localhost:5432/blackroad
```

---

## Querying the Database

### Prism Console API (SQLite)

```bash
# Connect to SQLite DB
cd services/prism-console-api
sqlite3 prism.db

# List tables
.tables

# Describe agent table
.schema agent

# Query agents
SELECT * FROM agent LIMIT 10;

# Exit
.quit
```

### Main API (Postgres)

```bash
# Connect to Postgres
psql postgresql://blackroad:password@localhost:5432/blackroad

# List tables
\dt

# Describe agents table
\d agents

# Query agents
SELECT * FROM agents LIMIT 10;

# Exit
\q
```

---

## Production Recommendations

### 1. Use PostgreSQL for Both Databases

SQLite is fine for local dev, but production should use Postgres:

```bash
# Prism Console API
PRISM_API_DB_URL=postgresql://prism_user:password@postgres:5432/prism_console

# Main API
DATABASE_URL=postgresql://blackroad_user:password@postgres:5432/blackroad_main
```

### 2. Separate Postgres Instances

For high availability, run separate Postgres instances:
- Prism Console DB on instance 1
- Main API DB on instance 2

This allows independent scaling and backup schedules.

### 3. Enable Connection Pooling

Use PgBouncer or built-in pooling:

```bash
PRISM_API_DB_URL=postgresql+psycopg2://user:pass@pgbouncer:6432/prism?pool_size=20&max_overflow=10
```

### 4. Backup Strategy

**Prism Console DB:**
- Frequent backups (hourly) – contains real-time telemetry
- Retention: 7 days (telemetry is time-sensitive)

**Main API DB:**
- Daily backups – contains user accounts and wallets
- Retention: 30 days + monthly archives

---

## Troubleshooting

### "Table already exists" Error

**Problem:** SQLModel trying to create tables that already exist

**Solution:** Drop and recreate:
```bash
cd services/prism-console-api
rm prism.db
poetry run uvicorn prism.main:app --reload
```

### Schema Mismatch After Model Change

**Problem:** Changed `models.py` but table schema didn't update

**Solution:** SQLModel doesn't auto-migrate. Options:
1. Delete DB and recreate (dev only)
2. Manually alter table via SQL
3. Use Alembic for migrations (recommended for production)

### "No such table: agent_event" (with underscore)

**Problem:** SQLModel creates table names as lowercase class name (no underscore)

**Expected:** `agentevent` (no underscore)
**If you see:** `agent_event` (with underscore)

**Fix:** Check `models.py` – table name should be set explicitly:
```python
class AgentEvent(SQLModel, table=True):
    __tablename__ = "agentevent"  # Explicit table name
```

---

## Summary

| Database | Service | Tables | Migration Strategy |
|----------|---------|--------|-------------------|
| `prism.db` | Prism Console API | `agent`, `agentevent`, `runbook`, `metric`, `minersample`, `setting` | Auto-create from SQLModel |
| `blackroad` | Main API | `users`, `agents`, `wallets`, `roadchain_*`, etc. | SQL migrations in `db/migrations/` |

**Key Takeaway:** These are **separate databases** for **separate services**. Don't mix them!

---

**Last Updated:** 2025-11-15
**Maintainer:** Cecilia (Cece) - Systems Architect
