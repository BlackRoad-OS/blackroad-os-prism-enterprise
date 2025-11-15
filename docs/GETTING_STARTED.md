# Getting Started with Prism Console

Welcome to the BlackRoad Prism Console! This guide will help you get up and running quickly.

## Prerequisites

- **Node.js** 20+ (for web apps)
- **Python** 3.10+ (for API services)
- **pnpm** 8+ (for monorepo package management)
- **Poetry** 1.5+ (for Python dependencies)
- **Docker** (optional, for containerized services)

### Check Your Environment

```bash
node --version   # Should be 20+
python --version # Should be 3.10+
pnpm --version   # Should be 8+
poetry --version # Should be 1.5+
docker --version # Optional
```

---

## Quick Start (5 Minutes)

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/blackboxprogramming/blackroad-prism-console.git
cd blackroad-prism-console

# Install root dependencies
npm install

# Install Prism Console API dependencies
cd services/prism-console-api
poetry install
cd ../..

# Install Prism Console Web dependencies
cd apps/prism-console-web
pnpm install --ignore-workspace
cd ../..
```

### 2. Start Prism Console API

```bash
cd services/prism-console-api
poetry run uvicorn prism.main:app --reload --port 4000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:4000
INFO:     Application startup complete.
```

Test the API:
```bash
curl http://localhost:4000/health
# Expected: {"status":"ok","uptime":"mock","version":"0.1.0","db":"connected","mocks":false}
```

### 3. Start Prism Console Web (New Terminal)

```bash
cd apps/prism-console-web
pnpm dev
```

You should see:
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
```

### 4. Open the Console

Visit **http://localhost:3000** in your browser.

You should see the Prism Console dashboard with:
- Metrics overview
- Agent catalog (seeded with sample data)
- Runbook list
- Miners panel (showing sample telemetry)

🎉 **You're running Prism Console!**

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:
- `PRISM_API_PORT` – API server port (default: 4000)
- `PRISM_API_MOCK_MODE` – Enable mock auth for local dev (default: false)
- `BLACKROAD_API_URL` – API URL for web UI (default: http://localhost:4000)
- `QISKIT_API_TOKEN` – IBM Quantum API token (optional, for quantum features)

See [`.env.example`](../.env.example) for all available variables.

---

## Understanding the Architecture

Prism Console has two main components:

```
┌─────────────────────┐      ┌─────────────────────────────────┐
│ Prism Console Web   │─────▶│  Prism Console API              │
│ (Next.js 14)        │ HTTP │  (FastAPI)                      │
│ Port: 3000          │ SSE  │  Port: 4000                     │
└─────────────────────┘      └─────────────────────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │ SQLite Database  │
                              │ (prism.db)       │
                              └──────────────────┘
```

- **Prism Console API** – FastAPI backend that stores agents, metrics, runbooks, and miner telemetry
- **Prism Console Web** – Next.js frontend that displays dashboards and real-time telemetry
- **Database** – SQLite for local dev (auto-created), Postgres for production

For deeper understanding, see [PRISM_CONSOLE_ARCHITECTURE.md](./PRISM_CONSOLE_ARCHITECTURE.md).

---

## Common Development Tasks

### Run Tests

```bash
# API tests
cd services/prism-console-api
poetry run pytest

# Web tests
cd apps/prism-console-web
pnpm test
pnpm test:e2e  # Playwright E2E tests
```

### Lint & Format

```bash
# API
cd services/prism-console-api
poetry run ruff check src/
poetry run black src/

# Web
cd apps/prism-console-web
pnpm lint
pnpm format
```

### View API Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:4000/docs
- **ReDoc:** http://localhost:4000/redoc
- **OpenAPI JSON:** http://localhost:4000/openapi.json

### View Storybook (UI Components)

```bash
cd apps/prism-console-web
pnpm storybook
```

Visit http://localhost:6006 to browse component library.

---

## Sending Miner Telemetry

The Prism Console API accepts miner telemetry via `POST /api/miners/sample`.

### Example with curl

```bash
curl -X POST http://localhost:4000/api/miners/sample \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "miner_id": "xmrig-001",
    "hashrate_1m": 50000.0,
    "hashrate_15m": 48000.0,
    "shares_accepted": 1234,
    "shares_rejected": 12,
    "temperature_c": 72.5,
    "pool": "pool.example.com:3333",
    "profile": "high-performance"
  }'
```

**Note:** Set `PRISM_API_MOCK_MODE=true` in `.env` to bypass authentication during development.

### Watch Live Updates

Open http://localhost:3000 and navigate to the **Miners** panel. Your sample will appear in real-time via Server-Sent Events (SSE).

---

## Working with Agents

### View Agent Catalog

```bash
curl http://localhost:4000/api/agents \
  -H "Authorization: Bearer test-token"
```

### View Agent Details

```bash
curl http://localhost:4000/api/agents/cecilia-001 \
  -H "Authorization: Bearer test-token"
```

---

## Working with Runbooks

### List Runbooks

```bash
curl http://localhost:4000/api/runbooks \
  -H "Authorization: Bearer test-token"
```

### Execute a Runbook

```bash
curl -X POST http://localhost:4000/api/runbooks/restart-service/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "input": {
      "service_name": "prism-console-api",
      "graceful": true
    },
    "idempotencyKey": "unique-key-123"
  }'
```

---

## Docker Deployment (Optional)

### Using Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Build Individual Services

```bash
# Build Prism Console API
docker build -t prism-console-api:latest -f services/prism-console-api/Dockerfile .

# Build Prism Console Web
docker build -t prism-console-web:latest -f apps/prism-console-web/Dockerfile .
```

---

## Troubleshooting

### API Won't Start

**Problem:** `ModuleNotFoundError: No module named 'prism'`

**Solution:**
```bash
cd services/prism-console-api
poetry install
poetry run uvicorn prism.main:app --reload
```

### Web UI Shows "Failed to load"

**Problem:** Web UI can't connect to API

**Solutions:**
1. Verify API is running: `curl http://localhost:4000/health`
2. Check `BLACKROAD_API_URL` in `.env.local` (should be `http://localhost:4000`)
3. Check browser console for CORS errors

### Authentication Errors

**Problem:** `401 Unauthorized` when calling API

**Solutions:**
1. For local dev, set `PRISM_API_MOCK_MODE=true` in `services/prism-console-api/.env`
2. Or include a valid JWT token in `Authorization: Bearer <token>` header

### Database Issues

**Problem:** `sqlite3.OperationalError: no such table`

**Solution:** Delete `prism.db` and restart the API. Tables will be auto-created:
```bash
cd services/prism-console-api
rm -f prism.db
poetry run uvicorn prism.main:app --reload
```

---

## Next Steps

Now that you're running Prism Console:

1. **Explore the API** – Visit http://localhost:4000/docs for interactive API documentation
2. **Read the Architecture** – See [PRISM_CONSOLE_ARCHITECTURE.md](./PRISM_CONSOLE_ARCHITECTURE.md)
3. **Send Real Telemetry** – Integrate miner or agent telemetry
4. **Create Custom Runbooks** – Add operational procedures to the runbook catalog
5. **Deploy to Production** – See [DEPLOYMENT.md](../DEPLOYMENT.md)

---

## Getting Help

- **Documentation:** Browse the [`docs/`](../docs/) directory
- **Issues:** Report bugs at https://github.com/blackboxprogramming/blackroad-prism-console/issues
- **Security:** See [SECURITY.md](../SECURITY.md) for security policies

---

**Welcome to the Prism Console!** 🚀

Last Updated: 2025-11-15
