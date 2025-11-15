# BlackRoad PatentNet Continuous Update System

## Overview

The BlackRoad PatentNet system provides **continuous, automated patent claim anchoring** to the blockchain. This document describes how the system ensures constant updates and defensive publication of Amundson mathematical framework discoveries.

## Architecture

### Daily Anchor Process

The system runs a daily anchor job that:

1. **Collects** all patent claim JSON files created during the day
2. **Merklizes** them into a single cryptographic hash (Merkle root)
3. **Commits** the Merkle root to an Ethereum-compatible smart contract
4. **Records** the transaction hash and status for monitoring

### Components

```
┌─────────────────────────────────────────────────────────┐
│  systemd Timer (patent-anchor.timer)                     │
│  Schedule: Daily at 23:55:00 UTC                         │
│  Persistent: Yes (catches up if system was down)         │
└─────────────────┬───────────────────────────────────────┘
                  │ triggers
                  ▼
┌─────────────────────────────────────────────────────────┐
│  systemd Service (patent-anchor.service)                 │
│  Type: oneshot                                           │
│  Restart: on-failure (3 attempts, 60s intervals)         │
└─────────────────┬───────────────────────────────────────┘
                  │ calls
                  ▼
┌─────────────────────────────────────────────────────────┐
│  API Endpoint: POST /api/patent/anchor/daily             │
│  - Scans /srv/patent-archive/YYYYMMDD/*.json             │
│  - Builds Merkle tree (pairwise SHA256)                  │
│  - Calls smart contract: commitDailyRoot()               │
│  - Records status in .anchor-status.json                 │
└─────────────────┬───────────────────────────────────────┘
                  │ commits to
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Blockchain Smart Contract (ClaimRegistry)               │
│  Network: Ethereum-compatible (ETH_RPC_URL)              │
│  Function: commitDailyRoot(yyyymmdd, merkleRoot)         │
└─────────────────────────────────────────────────────────┘
```

## Installation

### 1. Install the systemd timer

```bash
cd /home/user/blackroad-prism-console
./scripts/install-patent-anchor-timer.sh
```

This will:
- Copy timer and service files to systemd directory
- Enable the timer to start on boot
- Schedule daily runs at 23:55 UTC

### 2. Verify installation

```bash
# Check timer status
systemctl --user status patent-anchor.timer

# View scheduled runs
systemctl --user list-timers | grep patent-anchor

# Check logs
journalctl --user -u patent-anchor.service -f
```

## Monitoring

### Health Check Script

Run the health check to verify the system is working:

```bash
./scripts/check-patent-anchor-health.sh
```

This checks:
- API availability
- Last anchor status
- systemd timer status
- Recent success/error rates

### Health Check Endpoint

Query the API directly:

```bash
curl http://127.0.0.1:4000/api/patent/status | jq
```

Response includes:
- `healthy`: boolean indicating if system is operating correctly
- `lastAnchor`: details of most recent anchor attempt
- `recent`: success/error counts for last 7 days
- `history`: last 30 anchor records
- `config`: blockchain and archive configuration

### Continuous Monitoring

For production deployments, you can:

1. **Add a cron job** to run the health check:
```bash
# Add to crontab: check health every hour
0 * * * * /path/to/check-patent-anchor-health.sh
```

2. **Set up alerting** based on exit codes:
```bash
# In monitoring script
if ! /path/to/check-patent-anchor-health.sh; then
    # Send alert (email, Slack, PagerDuty, etc.)
    echo "Patent anchor system unhealthy!" | mail -s "Alert" admin@example.com
fi
```

3. **Integrate with systemd** using `OnFailure=` directive to trigger alerts

## Features

### Persistent Execution

- **`Persistent=true`**: If the system is down when the timer should trigger, it will run the job as soon as the system comes back up
- **Ensures no days are missed** even during downtime

### Automatic Retry

- **On transient failures**: Service will retry up to 3 times
- **60-second delay** between retries
- **Logs all attempts** to systemd journal

### Status Recording

Every anchor attempt (success or failure) is recorded in `/srv/patent-archive/.anchor-status.json`:

```json
[
  {
    "day": 20251109,
    "status": "success",
    "count": 5,
    "root": "0xabc123...",
    "txHash": "0xdef456...",
    "error": null,
    "timestamp": "2025-11-09T23:55:30.123Z",
    "timestampUnix": 1699567530123
  }
]
```

History is retained for 90 days.

### Security Hardening

The systemd service includes:
- `PrivateTmp=true`: Isolated temporary directory
- `NoNewPrivileges=true`: Prevents privilege escalation
- `ProtectSystem=strict`: Read-only system directories
- `ProtectHome=true`: No access to home directories

## Manual Operations

### Trigger anchor manually

```bash
curl -X POST http://127.0.0.1:4000/api/patent/anchor/daily
```

### View anchor history

```bash
cat /srv/patent-archive/.anchor-status.json | jq
```

### Check today's claims

```bash
TODAY=$(date -u +%Y%m%d)
ls -la /srv/patent-archive/$TODAY/
```

### Stop/start the timer

```bash
# Stop
systemctl --user stop patent-anchor.timer

# Start
systemctl --user start patent-anchor.timer

# Restart
systemctl --user restart patent-anchor.timer
```

## Amundson Framework Connection

The continuous update system protects the **Amundson mathematical framework** discoveries:

- **Amundson I**: Coherence Gradient Equation
- **Amundson II**: Energy Balance Equation
- **Amundson III**: Resonant Natural Gradient Learning
- **Amundson Kernel**: Universal resonance operator
- **BlackRoad-Amundson Integration**: Phase VI field equations

Each discovery is:
1. Documented in patent claim format
2. Submitted via `/api/patent/claim`
3. Archived with timestamp and SHA256 hash
4. Merkle-anchored to blockchain daily at 23:55 UTC
5. Provides cryptographic proof of prior art

## Troubleshooting

### Timer not running

```bash
# Check if enabled
systemctl --user is-enabled patent-anchor.timer

# Enable it
systemctl --user enable patent-anchor.timer

# Start it
systemctl --user start patent-anchor.timer
```

### Anchor failures

Check logs:
```bash
journalctl --user -u patent-anchor.service -n 100
```

Common issues:
- **No contract configured**: Set `CLAIMREG_ADDR` environment variable
- **Network errors**: Check `ETH_RPC_URL` and network connectivity
- **Insufficient funds**: Ensure wallet has gas for transactions
- **Invalid credentials**: Verify `MINT_PK` (private key) is correct

### API not responding

```bash
# Check API service
systemctl --user status blackroad-api

# View API logs
journalctl --user -u blackroad-api -n 100
```

## Exit Codes

Health check script exit codes:
- `0`: System is healthy
- `1`: System is unhealthy (needs attention)
- `2`: Error checking status (API not responding, etc.)

## See Also

- [Amundson Tests Documentation](./AMUNDSON_TESTS.md)
- [Amundson Kernel Specification](./amundson_kernel.md)
- [Patent API Module](../srv/blackroad-api/modules/patentnet.js)
- [systemd Timer Configuration](../systemd/patent-anchor.timer)
- [systemd Service Configuration](../systemd/patent-anchor.service)
