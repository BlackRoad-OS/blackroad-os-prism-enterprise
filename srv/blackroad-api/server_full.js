'use strict';

const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { promisify } = require('node:util');
const { execFile } = require('node:child_process');

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const cookieSession = require('cookie-session');
const rateLimit = require('express-rate-limit');
const Stripe = require('stripe');

const execFileAsync = promisify(execFile);

const isTestEnv =
  process.env.NODE_ENV === 'test' || process.env.JEST_WORKER_ID !== undefined;

function parseAllowedOrigins() {
  return (process.env.ALLOW_ORIGINS || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
}

const allowedOrigins = parseAllowedOrigins();

function buildCorsOptions() {
  if (allowedOrigins.length === 0) {
    return { origin: true, credentials: true };
  }
  return {
    origin(origin, callback) {
      if (!origin) return callback(null, true);
      if (allowedOrigins.includes(origin)) return callback(null, true);
      return callback(new Error('Not allowed by CORS'), false);
    },
    credentials: true,
  };
}

const app = express();
app.set('trust proxy', 1);

app.use(helmet());
app.use(cors(buildCorsOptions()));
app.use(
  rateLimit({
    windowMs: 60 * 1000,
    max: 300,
    standardHeaders: true,
    legacyHeaders: false,
  })
);

let stripe = null;
if (process.env.STRIPE_SECRET) {
  try {
    stripe = new Stripe(process.env.STRIPE_SECRET, {
      apiVersion: '2023-10-16',
    });
  } catch (err) {
    console.warn('[blackroad-api] failed to init Stripe client:', err.message);
  }
}

const rawJsonParser = express.raw({ type: 'application/json' });
app.post('/api/billing/webhook', rawJsonParser, (req, res) => {
  if (!stripe || !process.env.STRIPE_WEBHOOK_SECRET) {
    return res.status(503).json({ error: 'webhook_unconfigured' });
  }
  const signature = req.get('Stripe-Signature');
  try {
    stripe.webhooks.constructEvent(
      req.body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );
    return res.json({ received: true });
  } catch (err) {
    return res
      .status(400)
      .json({ error: 'invalid_signature', detail: err.message });
  }
});

app.use(express.json({ limit: '2mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(
  cookieSession({
    name: 'brsid',
    secret: process.env.SESSION_SECRET || 'dev-session-secret',
    httpOnly: true,
    sameSite: 'lax',
    secure: !isTestEnv && process.env.NODE_ENV === 'production',
    maxAge: 7 * 24 * 60 * 60 * 1000,
  })
);

const originKey = (() => {
  if (!process.env.ORIGIN_KEY_PATH) return null;
  try {
    return fs
      .readFileSync(path.resolve(process.env.ORIGIN_KEY_PATH), 'utf8')
      .trim();
  } catch (err) {
    console.warn('[blackroad-api] unable to read origin key:', err.message);
    return null;
  }
})();

function shouldEnforceOriginKey(req) {
  if (!originKey) return false;
  const origin = req.get('Origin');
  return typeof origin === 'string' && origin.length > 0;
}

function ensureOriginKey(req, res, next) {
  if (!shouldEnforceOriginKey(req)) return next();
  if (req.get('X-BlackRoad-Key') === originKey) return next();
  return res.status(401).json({ error: 'invalid_origin_key' });
}

app.use('/api', ensureOriginKey);

function isMaintenanceMode() {
  const raw = String(process.env.AUTOPAL_GLOBAL_ENABLED || '')
    .trim()
    .toLowerCase();
  if (!raw) return false;
  return raw === 'false' || raw === '0' || raw === 'off';
}

const maintenancePayload = {
  code: 'maintenance_mode',
  message: 'AutoPal is paused by ops.',
  hint: 'Try again later or use runbooks.',
  runbook: 'https://runbooks/autopal/maintenance',
};

app.use((req, res, next) => {
  if (!isMaintenanceMode()) return next();

  res.set('x-autopal-mode', 'maintenance');

  const now = new Date().toISOString();
  if (req.path === '/health' || req.path === '/health/live') {
    res.set('cache-control', 'max-age=10');
    return res.json({ status: 'ok', ts: now });
  }
  if (req.path === '/health/ready') {
    return res.json({ status: 'ok', ts: now });
  }
  if (req.method === 'POST' && req.path === '/secrets/materialize') {
    return res.status(403).json({
      code: 'materialize_disabled',
      message: 'Token minting disabled (global switch).',
    });
  }
  if (req.method === 'POST' && req.path === '/secrets/resolve') {
    return res.status(503).json({
      code: 'maintenance_mode',
      message: 'Secret operations are disabled by the global switch.',
    });
  }
  if (req.method === 'POST' && req.path === '/fossil/override') {
    return res.status(503).json({
      code: 'maintenance_mode',
      message: 'Overrides are disabled while AutoPal is paused.',
    });
  }

  if (req.method === 'GET') {
    res.set('Retry-After', '60');
  }
  return res.status(503).json(maintenancePayload);
});

function nowIso() {
  return new Date().toISOString();
}

function requireAuth(req, res, next) {
  if (req.session && req.session.user) return next();
  return res.status(401).json({ error: 'unauthorized' });
}

app.get('/health', (_req, res) => {
  res.json({ ok: true, ts: nowIso() });
});

app.get('/health/live', (_req, res) => {
  res.json({ status: 'ok', ts: nowIso() });
});

app.get('/health/ready', (_req, res) => {
  res.json({ status: 'ok', ts: nowIso() });
});

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, uptime: process.uptime(), ts: nowIso() });
});

app.post('/api/login', (req, res) => {
  const { username, password } = req.body || {};
  if (typeof username !== 'string' || typeof password !== 'string') {
    return res.status(400).json({ error: 'missing_credentials' });
  }
  if (username !== 'root' || password !== 'Codex2025') {
    return res.status(401).json({ error: 'invalid_credentials' });
  }
  req.session.user = { id: 'root', username: 'root', roles: ['admin'] };
  return res.json({ ok: true, user: { username: 'root' } });
});

app.post('/api/logout', (req, res) => {
  req.session = null;
  res.json({ ok: true });
});

const DEFAULT_ENTITLEMENTS = {
  planName: 'Free',
  entitlements: {
    can: {
      math: { pro: false },
      llm: { pro: true },
    },
    limits: {
      chat: 500,
      storageGb: 5,
    },
  },
};

app.get('/api/billing/entitlements/me', requireAuth, (_req, res) => {
  res.json(DEFAULT_ENTITLEMENTS);
});

app.get('/api/trust/curvature', (_req, res) => {
  res.json([
    { u: 'a', v: 'b', kappa: 0.42 },
    { u: 'b', v: 'c', kappa: 0.37 },
  ]);
});

app.get('/api/truth/diff', (_req, res) => {
  res.json({
    ctd: 1,
    ops: [
      { op: 'replace', path: '/meta/title', lhs: 'Truth A', rhs: 'Truth B' },
      { op: 'add', path: '/meta/tags/-', value: 'insight' },
    ],
  });
});

app.get('/api/connectors/status', (_req, res) => {
  res.json({
    config: {
      stripe: false,
      mail: false,
      sheets: false,
      calendar: false,
      discord: false,
      webhooks: false,
    },
    live: {
      slack: false,
      airtable: false,
      linear: false,
      salesforce: false,
    },
  });
});

const QUANTUM_TOPICS = [
  {
    topic: 'reasoning',
    summary:
      'Quantum reasoning models blend symbolic search with qubit annealing.',
  },
  {
    topic: 'memory',
    summary:
      'Persistent entanglement enables long-horizon recall of agent sessions.',
  },
  {
    topic: 'symbolic',
    summary:
      'Hybrid symbolic/quantum theorem provers unlock interpretable planning.',
  },
];

app.get('/api/quantum', (_req, res) => {
  res.json({ topics: QUANTUM_TOPICS });
});

app.get('/api/quantum/:topic', (req, res) => {
  const detail = QUANTUM_TOPICS.find(
    (entry) => entry.topic === req.params.topic
  );
  if (!detail) {
    return res.status(404).json({ error: 'unknown_topic' });
  }
  return res.json({ ...detail, ts: nowIso() });
});

app.get('/api/math/health', (_req, res) => {
  const hasEngine = Boolean(process.env.MATH_ENGINE_URL);
  if (!hasEngine) {
    return res.status(503).json({ ok: false, error: 'engine_unavailable' });
  }
  return res.json({ ok: true, engine: process.env.MATH_ENGINE_URL });
});

app.post('/api/math/eval', (req, res) => {
  const hasEngine = Boolean(process.env.MATH_ENGINE_URL);
  if (!hasEngine) {
    return res.status(503).json({ error: 'engine_unavailable' });
  }
  const { expr } = req.body || {};
  if (typeof expr !== 'string') {
    return res.status(400).json({ error: 'expr_required' });
  }
  try {
    const value = eval(expr);
    return res.json({ ok: true, value });
  } catch (err) {
    return res
      .status(400)
      .json({ error: 'invalid_expression', detail: err.message });
  }
});

const PROVIDERS = [
  {
    id: 'openai',
    name: 'OpenAI',
    models: ['gpt-4o', 'o3-mini'],
    capabilities: ['chat', 'embeddings'],
  },
  {
    id: 'anthropic',
    name: 'Anthropic',
    models: ['claude-3.5-sonnet'],
    capabilities: ['chat'],
  },
];

app.get('/v1/providers', (_req, res) => {
  res.json(PROVIDERS);
});

app.get('/v1/providers/:id/health', (req, res) => {
  const provider = PROVIDERS.find((item) => item.id === req.params.id);
  if (!provider) {
    return res.status(404).json({ error: 'provider_not_found' });
  }
  return res.json({ id: provider.id, ok: true, latencyMs: 42 });
});

const gitRepoPath = process.env.GIT_REPO_PATH
  ? path.resolve(process.env.GIT_REPO_PATH)
  : process.cwd();

async function runGit(args) {
  const { stdout } = await execFileAsync('git', args, {
    cwd: gitRepoPath,
    maxBuffer: 4 * 1024 * 1024,
  });
  return stdout.toString();
}

function computeCounts(statusOutput) {
  const counts = { staged: 0, unstaged: 0, untracked: 0 };
  if (!statusOutput) return counts;
  const lines = statusOutput.split('\n').filter(Boolean);
  for (const line of lines) {
    const state = line.slice(0, 2);
    if (state === '??') {
      counts.untracked += 1;
      continue;
    }
    if (state[0] && state[0] !== ' ') counts.staged += 1;
    if (state[1] && state[1] !== ' ') counts.unstaged += 1;
  }
  return counts;
}

app.get('/api/git/health', requireAuth, async (_req, res) => {
  try {
    const inside = await runGit(['rev-parse', '--is-inside-work-tree']);
    res.json({
      ok: true,
      insideWorkTree: inside.trim() === 'true',
      repoPath: gitRepoPath,
      readOnly: true,
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

app.get('/api/git/status', requireAuth, async (_req, res) => {
  try {
    const [branchRaw, statusRaw] = await Promise.all([
      runGit(['rev-parse', '--abbrev-ref', 'HEAD']),
      runGit(['status', '--porcelain']),
    ]);
    const branch = branchRaw.trim();
    const counts = computeCounts(statusRaw);
    const isDirty = Object.values(counts).some((value) => value > 0);
    res.json({ ok: !isDirty, branch, counts, isDirty });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

app.use((req, res) => {
  res.status(404).json({ error: 'not_found', path: req.path });
});

const server = http.createServer(app);

const desiredPort = (() => {
  if (require.main === module) {
    return Number.parseInt(process.env.PORT || '4000', 10);
  }
  return 0;
})();

server.listen(desiredPort);

module.exports = { app, server };

if (require.main === module) {
  const address = server.address();
  const boundPort =
    typeof address === 'object' && address ? address.port : desiredPort;

  console.log(`[blackroad-api] listening on port ${boundPort}`);
}
