# BlackRoad Prism Console - Production Deployment Guide

**Last Updated**: 2025-11-09  
**Status**: Production Ready

## Quick Start

```bash
# Start all services with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or start manually
npm install
cd apps/agent-gateway && npm run build && npm start &
cd apps/prism-console-web && npm run build && npm start &
```

## Architecture

- **100 Production Agents** across 5 tiers
- **Agent Gateway API** (Port 3001)
- **Prism Console Web** (Port 3000)
- **PostgreSQL** for persistence
- **Redis** for caching

## Environment Setup

```env
# Agent Gateway
AGENT_GATEWAY_PORT=3001
AGENTS_PATH=/path/to/agents

# Prism Console
NEXT_PUBLIC_AGENT_GATEWAY_URL=http://localhost:3001
```

## Verification

```bash
# Health checks
curl http://localhost:3001/health
curl http://localhost:3000

# List agents
curl http://localhost:3001/v1/agents
```

See full deployment guide in repository documentation.
