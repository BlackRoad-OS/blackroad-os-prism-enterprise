import fetch from 'node-fetch';

const DEFAULT_POLL_MS = 15_000;
const REQUEST_TIMEOUT_MS = 5_000;

function getEnv(name, {required = true, fallback} = {}) {
  const value = process.env[name];
  if ((value === undefined || value === '') && required) {
    throw new Error(`Missing required environment variable ${name}`);
  }
  return value === undefined || value === '' ? fallback : value;
}

function redact(value) {
  if (!value) return '***';
  const str = String(value);
  if (str.length <= 8) return `${str.slice(0, 2)}***${str.slice(-2)}`;
  return `${str.slice(0, 4)}***${str.slice(-4)}`;
}

function log(message, meta = undefined) {
  const ts = new Date().toISOString();
  if (meta) {
    console.log(`[miner-bridge] ${ts} ${message}`, meta);
  } else {
    console.log(`[miner-bridge] ${ts} ${message}`);
  }
}

function buildHeaders(token) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

function normalizeHashrate(source) {
  if (!source) {
    return { minute: 0, quarterHour: 0 };
  }
  if (Array.isArray(source.total)) {
    const [oneMin, fiveMin, fifteenMin] = source.total;
    return {
      minute: Number.isFinite(oneMin) ? oneMin : 0,
      quarterHour: Number.isFinite(fifteenMin) ? fifteenMin : 0,
    };
  }
  if (typeof source.total === 'number') {
    return { minute: source.total, quarterHour: source.total };
  }
  return { minute: 0, quarterHour: 0 };
}

function normalizeResults(results) {
  if (!results) {
    return { accepted: 0, rejected: 0, total: 0 };
  }
  const accepted = Number.isFinite(results.shares_good) ? results.shares_good : 0;
  const rejected = Number.isFinite(results.shares_bad) ? results.shares_bad : 0;
  const total = Number.isFinite(results.shares_total)
    ? results.shares_total
    : accepted + rejected;
  return { accepted, rejected, total };
}

function extractPool(summary) {
  const pool = summary?.connection?.pool ?? summary?.pool ?? 'unknown';
  return typeof pool === 'string' ? pool : 'unknown';
}

function extractMiner(summary) {
  if (typeof summary?.worker_id === 'string' && summary.worker_id.trim().length > 0) {
    return summary.worker_id.trim();
  }
  if (typeof summary?.rig_id === 'string' && summary.rig_id.trim().length > 0) {
    return summary.rig_id.trim();
  }
  return 'xmrig';
}

async function fetchJson(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) {
      throw new Error(`Request failed with status ${res.status}`);
    }
    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}

function buildSample(summary) {
  const hashrate = normalizeHashrate(summary?.hashrate ?? summary?.hash ?? summary);
  const results = normalizeResults(summary?.results ?? summary?.shares);
  return {
    miner: extractMiner(summary),
    pool: extractPool(summary),
    hashrate_1m: hashrate.minute,
    hashrate_15m: hashrate.quarterHour,
    shares_accepted: results.accepted,
    shares_rejected: results.rejected,
    shares_total: results.total,
    ts: new Date().toISOString(),
  };
}

function buildEvent({ orgId, agentId, sample }) {
  const payload = {
    type: 'miner.sample',
    orgId,
    agentId,
    sample,
  };
  const event = {
    topic: 'miner.sample',
    payload,
  };
  if (agentId) {
    event.actor = `agent:${agentId}`;
  }
  return event;
}

async function postSample({ prismApi, headers, event }) {
  const url = `${prismApi.replace(/\/$/, '')}/events`;
  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(event),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to post event (${res.status}): ${body}`);
  }
  return res.json().catch(() => undefined);
}

async function run() {
  const prismApi = getEnv('PRISM_API');
  const orgId = getEnv('PRISM_ORG_ID');
  const agentId = getEnv('MINER_AGENT_ID', { required: false });
  const token = getEnv('PRISM_TOKEN', { required: false });
  const xmrigUrl = getEnv('XMRIG_URL', { required: false, fallback: 'http://xmrig:18080/2/summary' });
  const pollMs = Number.parseInt(getEnv('POLL_INTERVAL_MS', { required: false, fallback: `${DEFAULT_POLL_MS}` }), 10);

  log('Starting miner bridge', {
    prismApi,
    orgId,
    agentId: agentId ? redact(agentId) : undefined,
    xmrigUrl,
    pollMs,
    token: token ? redact(token) : undefined,
  });

  const headers = buildHeaders(token);

  async function tick() {
    try {
      const summary = await fetchJson(xmrigUrl);
      const sample = buildSample(summary);
      const event = buildEvent({ orgId, agentId, sample });
      await postSample({ prismApi, headers, event });
      log('Posted miner.sample event', {
        miner: sample.miner,
        pool: sample.pool,
        hashrate_1m: sample.hashrate_1m,
        hashrate_15m: sample.hashrate_15m,
        shares_accepted: sample.shares_accepted,
        shares_rejected: sample.shares_rejected,
        shares_total: sample.shares_total,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      log(`Error during sample tick: ${message}`);
    }
  }

  await tick();
  setInterval(tick, Number.isFinite(pollMs) && pollMs > 0 ? pollMs : DEFAULT_POLL_MS);
}

run().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  log(`Fatal error: ${message}`);
  process.exitCode = 1;
});
