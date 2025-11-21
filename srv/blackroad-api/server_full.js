'use strict';
/* BlackRoad API — Express + SQLite + Socket.IO + LLM bridge
   Runs behind Nginx on port 4000 with cookie-session auth.
   Env (optional):
     PORT=4000
     SESSION_SECRET=change_me
     DB_PATH=/srv/blackroad-api/blackroad.db
     LLM_URL=http://127.0.0.1:8000/chat
     ALLOW_SHELL=false
*/

const http = require('http');
const path = require('path');
const fs = require('fs');
const express = require('express');
const compression = require('compression');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const cors = require('cors');
const cookieSession = require('cookie-session');
const { randomUUID } = require('crypto');
const { body, validationResult } = require('express-validator');

const { body, validationResult } = require('express-validator');
const { createDatabase } = require('./lib/sqlite');
const { Server: SocketIOServer } = require('socket.io');
const { exec } = require('child_process');
const { randomUUID } = require('crypto');
const Stripe = require('stripe');
const { verifyToken } = require('./lib/verify');
const notify = require('./lib/notify');
const logger = require('./lib/log');
const attachLlmRoutes = require('./routes/admin_llm');
const gitRouter = require('./routes/git');
const providersRouter = require('./routes/providers');

// Custom environment variable loader replaces the standard 'dotenv' package.
// Rationale: We use a custom loader to reduce external dependencies, avoid issues with dotenv's parsing logic,
// and to allow for more controlled loading (e.g., skipping variables already set in process.env).
// See coding guidelines: dependency changes must be documented.
function loadEnvFile() {
  const envPath = process.env.DOTENV_PATH || path.join(process.cwd(), '.env');
  if (!fs.existsSync(envPath)) {
    return;
// --- Config
const PORT = parseInt(process.env.PORT || '4000', 10);
const SESSION_SECRET = process.env.SESSION_SECRET || 'dev-secret-change-me';
const DB_PATH = process.env.DB_PATH || '/srv/blackroad-api/blackroad.db';
const LLM_URL = process.env.LLM_URL || 'http://127.0.0.1:8000/chat';
const ALLOW_SHELL =
  String(process.env.ALLOW_SHELL || 'false').toLowerCase() === 'true';
const WEB_ROOT = process.env.WEB_ROOT || '/var/www/blackroad';
const BILLING_DISABLE =
  String(process.env.BILLING_DISABLE || 'false').toLowerCase() === 'true';
const STRIPE_SECRET = process.env.STRIPE_SECRET || '';
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || '';
const stripeClient = STRIPE_SECRET ? new Stripe(STRIPE_SECRET) : null;
const ALLOW_ORIGINS = process.env.ALLOW_ORIGINS
  ? process.env.ALLOW_ORIGINS.split(',').map((s) => s.trim())
  : [];

['SESSION_SECRET', 'INTERNAL_TOKEN'].forEach((name) => {
  if (!process.env[name]) {
    console.error(`Missing required env ${name}`);
    process.exit(1);
  }
  try {
    const content = fs.readFileSync(envPath, 'utf8');
    for (const line of content.split(/\r?\n/)) {
      if (!line || line.trim().startsWith('#')) continue;
      const idx = line.indexOf('=');
      if (idx === -1) continue;
      const key = line.slice(0, idx).trim();
      if (!key || Object.prototype.hasOwnProperty.call(process.env, key)) continue;
      const value = line.slice(idx + 1).trim();
      process.env[key] = value;
    }
  } catch (error) {
    if (process.env.LOG_LEVEL !== 'silent') {
      console.warn(`Failed to load ${envPath}: ${error.message}`);
    }
  }
}

loadEnvFile();

const REQUIRED_ENV = ['SESSION_SECRET', 'INTERNAL_TOKEN', 'ALLOW_ORIGINS'];
const missingEnv = REQUIRED_ENV.filter((name) => !process.env[name]);
if (missingEnv.length) {
  throw new Error(`Missing required environment variables: ${missingEnv.join(', ')}`);
}

const PORT = Number.parseInt(process.env.PORT || '4000', 10);
const SESSION_SECRET = process.env.SESSION_SECRET;
const INTERNAL_TOKEN = process.env.INTERNAL_TOKEN;
const ALLOW_ORIGINS = process.env.ALLOW_ORIGINS.split(',')
  .map((origin) => origin.trim())
  .filter(Boolean);
const WEB_ROOT = process.env.WEB_ROOT || path.join(__dirname, '../../var/www/blackroad');
const NODE_ENV = process.env.NODE_ENV || 'development';
const safeAttach = (label, attachFn) => {
  try {
    attachFn();
  } catch (err) {
    console.warn(`[bootstrap] ${label} module disabled: ${err.message}`);
  }
};

// --- App & server
const app = express();
require('./modules/jsonEnvelope')(app);
require('./modules/requestGuard')(app);
const server = http.createServer(app);
const io = new SocketIOServer(server, {
  path: '/socket.io',
  serveClient: false,
  cors: { origin: false }, // same-origin via Nginx
});

const app = express();
app.set('trust proxy', 1);

app.use((req, res, next) => {
  const provided = typeof req.headers['x-request-id'] === 'string' ? req.headers['x-request-id'] : null;
  const id = provided || randomUUID();
  req.requestId = id;
  res.setHeader('X-Request-Id', id);
  const started = Date.now();
  res.on('finish', () => {
    const durationMs = Date.now() - started;
    const logLine = JSON.stringify({
      event: 'request',
      id,
      method: req.method,
      path: req.originalUrl,
      status: res.statusCode,
      durationMs,
    });
    if (process.env.LOG_LEVEL !== 'silent') {
      console.info(logLine);
// Partner relay for mTLS-authenticated teammates
require('./modules/partner_relay_mtls')({ app });
require('./modules/projects')({ app });
require('./modules/pr_proxy')({ app });
require('./modules/patentnet')({ app });
require('./modules/truth_pubsub')({ app });
require('./modules/trust_graph')({ app });

const emitter = new EventEmitter();
const jobs = new Map();
let jobSeq = 0;

function addJob(type, payload, runner) {
  const id = String(++jobSeq);
  const job = { id, type, payload, status: 'queued', created: Date.now(), logs: [] };
  jobs.set(id, job);
  process.nextTick(async () => {
    job.status = 'running';
    try {
      await runner(id, payload);
      job.status = 'success';
    } catch (e) {
      job.status = 'failed';
      job.error = String(e);
    } finally {
      emitter.emit(id, null);
    }
  });
  next();
});

require('./modules/love_math')({ app });
safeAttach('jobs', () => require('./modules/jobs')({ app }));
safeAttach('memory', () => require('./modules/memory')({ app }));
require('./modules/brain_chat')({ app });
require('./modules/jobs_locked')({ app });
// --- Middleware
app.disable('x-powered-by');
app.use(helmet());
app.use(
  helmet.hsts({
    maxAge: 60 * 60 * 24 * 365,
    includeSubDomains: true,
    preload: true,
  }),
);
app.use(helmet.referrerPolicy({ policy: 'no-referrer' }));

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin) return callback(null, true);
      if (ALLOW_ORIGINS.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error('Not allowed by CORS'), false);
    },
    credentials: true,
  }),
);

app.use(
  rateLimit({
    windowMs: 60_000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
  }),
);

const resolveClientIp = (req) => {
  const forwarded = req.headers['x-forwarded-for'];
  // Express normalizes headers to strings but may surface arrays when the
  // header is supplied multiple times by intermediaries.
  const extractFirst = (value) => {
    if (typeof value !== 'string' || value.length === 0) return null;
    const first = value.split(',')[0]?.trim();
    return first || null;
  };
  if (Array.isArray(forwarded) && forwarded.length > 0) {
    const fromArray = extractFirst(forwarded[0]);
    if (fromArray) return fromArray;
  }
  const fromHeader = extractFirst(forwarded);
  if (fromHeader) return fromHeader;
  return req.socket?.remoteAddress || req.ip;
};

const loginLimiter = rateLimit({
  windowMs: 5 * 60_000,
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: true,
  keyGenerator: resolveClientIp,
  handler: (req, res) => {
    const ip = resolveClientIp(req);
    logger.warn({ event: 'login_rate_limited', ip });
    res.status(429).json({ error: 'too_many_attempts' });
  },
});
app.use((req, res, next) => {
  const id = randomUUID();
  req.id = id;
  const start = Date.now();
  res.on('finish', () => {
    logger.info({ id, method: req.method, path: req.originalUrl, status: res.statusCode, duration: Date.now() - start });
  });
  next();
});
app.use(compression());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: false, limit: '1mb' }));

app.use(
  cookieSession({
    name: 'brsess',
    keys: [SESSION_SECRET],
    httpOnly: true,
    sameSite: 'lax',
    secure: NODE_ENV === 'production',
    maxAge: 1000 * 60 * 60 * 8,
  }),
);

app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'blackroad-api', ts: new Date().toISOString() });
});
app.use((req, _res, next) => {
  const bearer = req.get('authorization');
  const headerToken =
    req.get('x-internal-token') ||
    (typeof bearer === 'string' ? bearer.replace(/^Bearer\s+/i, '') : '');
  if (headerToken && verifyToken(headerToken, INTERNAL_TOKEN)) {
    req.internal = true;
  }
  next();
});

// --- Homepage
app.get('/', (_, res) => {
  res.sendFile(path.join(WEB_ROOT, 'index.html'));
});
function sendHealth(_req, res) {
  res.json({ ok: true, version: '1.0.0', uptime: process.uptime() });
}
app.head('/health', (_req, res) => res.status(200).end());
app.get('/health', sendHealth);
app.head('/healthz', (_req, res) => res.status(200).end());
app.get('/healthz', sendHealth);

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, service: 'blackroad-api', ts: new Date().toISOString() });
// --- Health
app.head('/api/health', (_, res) => res.status(200).end());
app.get('/api/health', async (_req, res) => {
  let llm = false;
  try {
    const r = await fetch('http://127.0.0.1:8000/health');
    llm = r.ok;
  } catch (err) {
    logger.warn({ event: 'health_llm_check_failed', error: err.message });
  }
  res.json({
    ok: true,
    version: '1.0.0',
    uptime: process.uptime(),
    services: { api: true, llm },
  });
});

function requireAuth(req, res, next) {
  if (req.session && req.session.user) {
    return next();
  }
  return res.status(401).json({ error: 'unauthorized' });
}

app.get('/api/session', (req, res) => {
  res.json({ user: req.session?.user || null });
});

app.post(
  '/api/login',
  [body('username').isString().trim().notEmpty(), body('password').isString()],
  loginLimiter,
  [body('username').isString(), body('password').isString()],
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ error: 'invalid_request', details: errors.array() });
    }

    const { username, password } = req.body;
    const bypass = String(process.env.BYPASS_LOGIN || 'false').toLowerCase() === 'true';
    const validDevLogin = username === 'root' && password === 'Codex2025';

    if (!validDevLogin && !bypass) {
      return res.status(401).json({ error: 'invalid_credentials' });
    }

    req.session.user = { username, role: 'dev', plan: 'free' };
    return res.json({ ok: true, user: req.session.user });
  },
);

app.post('/api/logout', (req, res) => {
  req.session = null;
  res.json({ ok: true });
});

app.use('/api/git', requireAuth, gitRouter);

app.use(express.static(WEB_ROOT));

app.use((err, req, res, _next) => {
  const status = err.message === 'Not allowed by CORS' ? 403 : err.status || 500;
  const payload = {
    error: err.code || 'internal_error',
    message: err.message,
    requestId: req.requestId,
  };
  if (status >= 500 && process.env.LOG_LEVEL !== 'silent') {
    console.error(JSON.stringify({ event: 'error', requestId: req.requestId, message: err.message }));
  }
  res.status(status).json(payload);
});

const server = http.createServer(app);
  logger.info({
    event: 'stripe_webhook_received',
    type: event?.type || 'unknown',
  });
app.post('/api/billing/webhook', (req, res) => {
  if (!stripeClient || !STRIPE_WEBHOOK_SECRET) {
    return res.status(501).json({ error: 'stripe_unconfigured' });
  }
  const sig = req.headers['stripe-signature'];
  try {
    stripeClient.webhooks.constructEvent(
      JSON.stringify(req.body),
      sig,
      STRIPE_WEBHOOK_SECRET
    );
  } catch (e) {
    logger.error('stripe_webhook_verify_failed', e);
    return res.status(400).json({ error: 'invalid_signature' });
  }
  res.json({ received: true });
});

// --- SQLite bootstrap
const db = createDatabase(DB_PATH);
db.pragma('journal_mode = WAL');
db.pragma('synchronous = NORMAL');

const TABLES = ['projects', 'agents', 'datasets', 'models', 'integrations'];
for (const t of TABLES) {
  db.prepare(
    `
    CREATE TABLE IF NOT EXISTS ${t} (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      meta JSON
    )
  `
  ).run();
}

function start(port = PORT) {
  if (!server.listening) {
    server.listen(port);
  }
  return server;
}

if (process.env.JEST_WORKER_ID) {
  start(0);
} else if (require.main === module) {
  start();
// Quantum AI table seed
db.prepare(
  `
  CREATE TABLE IF NOT EXISTS quantum_ai (
    topic TEXT PRIMARY KEY,
    summary TEXT NOT NULL
  )
`
).run();
const qSeed = [
  {
    topic: 'reasoning',
    summary:
      'Quantum parallelism lets models explore many reasoning paths simultaneously for accelerated insight.',
  },
  {
    topic: 'memory',
    summary:
      'Quantum RAM with entangled states hints at dense, instantly linked memory architectures.',
  },
  {
    topic: 'symbolic',
    summary:
      'Interference in quantum-symbolic AI could amplify useful symbol chains while damping noise.',
  },
];
for (const row of qSeed) {
  db.prepare(
    'INSERT OR IGNORE INTO quantum_ai (topic, summary) VALUES (?, ?)'
  ).run(row.topic, row.summary);
}

// Git API
app.use('/api/git', requireAuth, gitRouter);
app.use('/v1/providers', providersRouter);

// Helpers
function listRows(t) {
  return db
    .prepare(
      `SELECT id, name, updated_at, meta FROM ${t} ORDER BY datetime(updated_at) DESC`
    )
    .all();
}
function createRow(t, name, meta = null) {
  const stmt = db.prepare(
    `INSERT INTO ${t} (name, updated_at, meta) VALUES (?, datetime('now'), ?)`
  );
  const info = stmt.run(name, meta ? JSON.stringify(meta) : null);
  return info.lastInsertRowid;
}
function updateRow(t, id, name, meta = null) {
  const stmt = db.prepare(
    `UPDATE ${t} SET name = COALESCE(?, name), meta = COALESCE(?, meta), updated_at = datetime('now') WHERE id = ?`
  );
  stmt.run(name ?? null, meta ? JSON.stringify(meta) : null, id);
}
function deleteRow(t, id) {
  db.prepare(`DELETE FROM ${t} WHERE id = ?`).run(id);
}
function validKind(kind) {
  return TABLES.includes(kind);
}

// --- CRUD routes (guard with auth once you’re ready)
app.get('/api/:kind', requireAuth, (req, res) => {
  const { kind } = req.params;
  if (!validKind(kind)) return res.status(404).json({ error: 'unknown_kind' });
  try {
    res.json(listRows(kind));
  } catch (e) {
    res.status(500).json({ error: 'db_list_failed', detail: String(e) });
  }
});
app.post('/api/:kind', requireAuth, (req, res) => {
  const { kind } = req.params;
  const { name, meta } = req.body || {};
  if (!validKind(kind)) return res.status(404).json({ error: 'unknown_kind' });
  if (!name) return res.status(400).json({ error: 'name_required' });
  try {
    const id = createRow(kind, name, meta);
    res.json({ ok: true, id });
  } catch (e) {
    res.status(500).json({ error: 'db_create_failed', detail: String(e) });
  }
});
app.post('/api/:kind/:id', requireAuth, (req, res) => {
  const { kind, id } = req.params;
  const { name, meta } = req.body || {};
  if (!validKind(kind)) return res.status(404).json({ error: 'unknown_kind' });
  try {
    updateRow(kind, Number(id), name, meta);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: 'db_update_failed', detail: String(e) });
  }
});
app.delete('/api/:kind/:id', requireAuth, (req, res) => {
  const { kind, id } = req.params;
  if (!validKind(kind)) return res.status(404).json({ error: 'unknown_kind' });
  try {
    deleteRow(kind, Number(id));
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: 'db_delete_failed', detail: String(e) });
  }
});

// --- Subscribe & connectors
const VALID_PLANS = ['free', 'builder', 'guardian'];
const VALID_CYCLES = ['monthly', 'annual'];

app.get('/api/connectors/status', (req, res) => {
  const stripe = !!(
    process.env.STRIPE_PUBLIC_KEY &&
    process.env.STRIPE_SECRET &&
    process.env.STRIPE_WEBHOOK_SECRET
  );
  const mail = !!process.env.MAIL_PROVIDER;
  const sheets = !!(
    process.env.GSHEETS_SA_JSON || process.env.SHEETS_CONNECTOR_TOKEN
  );
  const calendar = !!(
    process.env.GOOGLE_CALENDAR_CREDENTIALS || process.env.ICS_URL
  );
  const discord = !!process.env.DISCORD_INVITE;
  const webhooks = stripe; // placeholder
  res.json({ stripe, mail, sheets, calendar, discord, webhooks });
});

// Basic health endpoint exposing provider mode
app.get('/api/subscribe/health', (_req, res) => {
  const mode =
    process.env.SUBSCRIBE_MODE ||
    (process.env.STRIPE_SECRET
      ? 'stripe'
      : process.env.GUMROAD_TOKEN
        ? 'gumroad'
        : 'local');
  let providerReady = false;
  if (mode === 'stripe') providerReady = !!process.env.STRIPE_SECRET;
  else if (mode === 'gumroad') providerReady = !!process.env.GUMROAD_TOKEN;
  else providerReady = true;
  res.json({ ok: true, mode, providerReady });
});

app.post('/api/subscribe/checkout', (req, res) => {
  const { plan, cycle } = req.body || {};
  if (!VALID_PLANS.includes(plan) || !VALID_CYCLES.includes(cycle)) {
    return res.status(400).json({ error: 'invalid_input' });
  }
  if (!process.env.STRIPE_SECRET) {
    return res.status(409).json({ mode: 'invoice' });
  }
  // Stripe integration would go here
  res.json({ url: 'https://stripe.example/checkout' });
});

app.post('/api/subscribe/invoice-intent', (req, res) => {
  const { plan, cycle, email, name, company } = req.body || {};
  if (!email || !VALID_PLANS.includes(plan) || !VALID_CYCLES.includes(cycle)) {
    return res.status(400).json({ error: 'invalid_input' });
  }
  let sub = db.prepare('SELECT id FROM subscribers WHERE email = ?').get(email);
  let subscriberId = sub ? sub.id : randomUUID();
  if (!sub) {
    db.prepare(
      'INSERT INTO subscribers (id, email, name, company, created_at, source) VALUES (?, ?, ?, ?, datetime("now"), ?)'
    ).run(subscriberId, email, name || null, company || null, 'invoice');
  }
  const subscriptionId = randomUUID();
  db.prepare(
    'INSERT INTO subscriptions (id, subscriber_id, plan, cycle, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime("now"), datetime("now"))'
  ).run(subscriptionId, subscriberId, plan, cycle, 'pending_invoice');
  res.json({ ok: true, next: '/subscribe/thanks' });
});

app.get('/api/subscribe/status', (req, res) => {
  const { email } = req.query || {};
  if (!email) return res.status(400).json({ error: 'email_required' });
  const row = db
    .prepare(
      'SELECT s.plan, s.cycle, s.status FROM subscribers sub JOIN subscriptions s ON sub.id = s.subscriber_id WHERE sub.email = ? ORDER BY datetime(s.created_at) DESC LIMIT 1'
    )
    .get(email);
  res.json(row || { status: 'none' });
});

// --- Billing: plans
app.get('/api/subscribe/plans', requireAuth, (_req, res) => {
  try {
    const rows = db
      .prepare(
        'SELECT id, name, monthly_price_cents, yearly_price_cents, features, is_active FROM plans WHERE is_active = 1'
      )
      .all();
    for (const r of rows) {
      try {
        r.features = JSON.parse(r.features);
      } catch {
        r.features = [];
const http = require('http');
const { randomUUID } = require('crypto');

const MAX_REQUEST_BODY_SIZE = 1 * 1024 * 1024; // 1MB

function parseAllowedOrigins(value = '') {
  return value
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);
}

function parseCookies(header = '') {
  return header
    .split(';')
    .map((chunk) => chunk.trim())
    .filter(Boolean)
    .reduce((acc, pair) => {
      const [key, value] = pair.split('=');
      if (key) {
        acc[key] = value ?? '';
      }
      return acc;
    }, {});
}

function sendJson(res, status, payload, extraHeaders = {}) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  Object.entries(extraHeaders).forEach(([key, value]) => {
    res.setHeader(key, value);
  });
  res.end(JSON.stringify(payload));
}

async function readRequestBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => {
      data += chunk;
      if (data.length > MAX_REQUEST_BODY_SIZE) {
        const error = new Error('payload too large');
        error.statusCode = 413;
        reject(error);
        req.destroy(error);
      }
    });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

async function getJsonBody(req, res, { allowEmpty = false } = {}) {
  let raw;
  try {
    raw = await readRequestBody(req);
  } catch (error) {
    if (!res.writableEnded) {
      const statusCode = error.statusCode === 413 ? 413 : 400;
      const errorMessage = statusCode === 413 ? 'payload too large' : 'invalid json';
      sendJson(res, statusCode, { error: errorMessage });
    }
    return { ok: false };
  }

  if (!raw) {
    if (allowEmpty) {
      return { ok: true, body: null };
    }
    sendJson(res, 400, { error: 'request body required' });
    return { ok: false };
  }

  try {
    return { ok: true, body: JSON.parse(raw) };
  } catch (error) {
    if (!res.writableEnded) {
      sendJson(res, 400, { error: 'invalid json' });
    }
    return { ok: false };
  }
}

function createServer({
  allowedOrigins = [],
  sessionSecret = undefined,
} = {}) {
  void sessionSecret;
  const sessions = new Map();
  const tasks = [];
  const VALID_USER = { username: 'root', password: 'Codex2025' };

  const server = http.createServer(async (req, res) => {
    const requestId = randomUUID();
    res.setHeader('x-request-id', requestId);
    res.setHeader('x-dns-prefetch-control', 'off');
    res.setHeader('x-frame-options', 'SAMEORIGIN');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');

    const origin = req.headers.origin;
    if (origin && allowedOrigins.includes(origin)) {
      res.setHeader('Access-Control-Allow-Origin', origin);
      res.setHeader('Access-Control-Allow-Credentials', 'true');
      res.setHeader('Vary', 'Origin');
    }

    const url = new URL(req.url, 'http://localhost');

    if (
      req.method === 'OPTIONS' &&
      ['/api/login', '/api/tasks'].includes(url.pathname) &&
      origin &&
      allowedOrigins.includes(origin)
    ) {
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
      res.setHeader('Access-Control-Max-Age', '600');
      res.statusCode = 204;
      res.end();
      return;
    }

    if (req.method === 'GET' && url.pathname === '/health') {
      return sendJson(res, 200, { ok: true });
    }

    if (req.method === 'GET' && url.pathname === '/api/health') {
      return sendJson(res, 200, { ok: true, uptime: process.uptime() });
    }

    if (req.method === 'POST' && url.pathname === '/api/login') {
      const { ok, body } = await getJsonBody(req, res);
      if (!ok) {
        return undefined;
      }

      if (!body || typeof body !== 'object') {
        return sendJson(res, 400, { error: 'invalid json payload' });
      }

// --- LLM bridge (/api/llm/chat)
// Forwards body to FastAPI (LLM_URL) and streams raw text back to the client.
app.post('/api/llm/chat', requireAuth, async (req, res) => {
  try {
    const upstream = await fetch(LLM_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body || {}),
    });

    // Stream if possible
    if (upstream.ok && upstream.body) {
      res.status(200);
      res.setHeader('Content-Type', 'text/plain; charset=utf-8');
      res.setHeader('Transfer-Encoding', 'chunked');

      const reader = upstream.body.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        // passthrough raw bytes (FastAPI may send plain text or SSE-like chunks)
        res.write(Buffer.from(value));
      if (body.username === VALID_USER.username && body.password === VALID_USER.password) {
        const sessionId = randomUUID();
        sessions.set(sessionId, { username: VALID_USER.username });
        return sendJson(res, 200, { ok: true }, {
          'Set-Cookie': `session=${sessionId}; HttpOnly; Path=/; SameSite=Lax`,
        });
      }
      return sendJson(res, 401, { error: 'invalid credentials' });
    }

    // Non-stream fallback
    const txt = await upstream.text().catch(() => '');
    // try to unwrap {text: "..."}
    let out = txt;
    try {
      const j = JSON.parse(txt);
      if (j && typeof j.text === 'string') out = j.text;
    } catch (err) {
      logger.debug({ event: 'llm_fallback_parse_failed', error: err.message });
    }
    res
      .status(upstream.ok ? 200 : upstream.status)
      .type('text/plain')
      .send(out || '(no content)');
  } catch (err) {
    logger.error({ event: 'llm_stream_proxy_failed', error: err.message });
    logger.error('llm_proxy_error', err);
    res.status(502).type('text/plain').send('(llm upstream error)');
  }
});

attachLlmRoutes(app);

// --- Optional shell exec (disabled by default)
app.post('/api/exec', requireAuth, (req, res) => {
  if (!ALLOW_SHELL) return res.status(403).json({ error: 'exec_disabled' });
  const cmd = ((req.body && req.body.cmd) || '').trim();
  if (!cmd) return res.status(400).json({ error: 'cmd_required' });
  exec(cmd, { timeout: 20000 }, (err, stdout, stderr) => {
    if (err)
      return res
        .status(500)
        .json({ error: 'exec_failed', detail: String(err), stderr });
    res.json({ out: stdout, stderr });
  });
});

const logConnectorStatusError = (connector, err) => {
  logger.warn({
    event: 'connector_status_check_failed',
    connector,
    error: err.message,
  });
};

app.get('/api/connectors/status', async (_req, res) => {
  const status = {
    slack: false,
    airtable: false,
    linear: false,
    salesforce: false,
  };
  try {
    if (process.env.SLACK_WEBHOOK_URL) {
      await notify.slack('status check');
      status.slack = true;
    }
  } catch (err) {
    logConnectorStatusError('slack', err);
  }
  try {
    if (process.env.AIRTABLE_API_KEY) status.airtable = true;
  } catch (err) {
    logConnectorStatusError('airtable', err);
  }
  try {
    if (process.env.LINEAR_API_KEY) status.linear = true;
  } catch (err) {
    logConnectorStatusError('linear', err);
  }
  try {
    if (process.env.SF_USERNAME) status.salesforce = true;
  } catch (err) {
    logConnectorStatusError('salesforce', err);
  }
  res.json(status);
});

// --- Quantum AI summaries
app.get('/api/quantum/:topic', (req, res) => {
  const { topic } = req.params;
  const row = db
    .prepare('SELECT summary FROM quantum_ai WHERE topic = ?')
    .get(topic);
  if (!row) return res.status(404).json({ error: 'not_found' });
  res.json({ topic, summary: row.summary });
});
    const cookies = parseCookies(req.headers.cookie);
    const session = cookies.session ? sessions.get(cookies.session) : undefined;

    if (req.method === 'POST' && url.pathname === '/api/tasks') {
      if (!session) {
        return sendJson(res, 401, { error: 'unauthorized' });
      }

      const { ok, body } = await getJsonBody(req, res);
      if (!ok) {
        return undefined;
      }

      if (!body || typeof body !== 'object') {
        return sendJson(res, 400, { error: 'invalid json payload' });
      }

      if (typeof body.title !== 'string' || body.title.trim() === '') {
        return sendJson(res, 400, { error: 'invalid task' });
      }
      const task = { id: tasks.length + 1, title: body.title.trim() };
      tasks.push(task);
      return sendJson(res, 201, { ok: true, task });
    }

    if (req.method === 'GET' && url.pathname === '/api/tasks') {
      if (!session) {
        return sendJson(res, 401, { error: 'unauthorized' });
      }
      return sendJson(res, 200, { tasks });
    }

    return sendJson(res, 404, { error: 'not found' });
  });
});

require('./modules/yjs_callback')({ app });
require('./modules/trust_curvature')({ app });
require('./modules/truth_diff')({ app });

// --- Socket.IO presence (metrics)
io.on('connection', (socket) => {
  socket.emit('hello', { ok: true, t: Date.now() });
});
const metricsTimer = setInterval(() => {
  const total = os.totalmem(),
    free = os.freemem();
  const payload = {
    t: Date.now(),
    load: os.loadavg()[0],
    mem: { total, free, used: total - free, pct: 1 - free / total },
    cpuCount: os.cpus()?.length || 1,
    host: os.hostname(),
  };
  io.emit('metrics', payload);
}, 2000);

// --- Start
server.listen(PORT, () => {
  console.log(
    `[blackroad-api] listening on ${PORT} (db: ${DB_PATH}, llm: ${LLM_URL}, shell: ${ALLOW_SHELL})`
  );
});
(async () => {
  try {
    await require('./modules/truth_pubsub')({ app });
  } catch (err) {
    console.error('truth_pubsub init failed', err);
  }
  require('./modules/yjs_callback')({ app });

  // --- Socket.IO presence (metrics)
  io.on('connection', (socket) => {
    socket.emit('hello', { ok: true, t: Date.now() });
  });
  setInterval(() => {
    const total = os.totalmem(), free = os.freemem();
    const payload = {
      t: Date.now(),
      load: os.loadavg()[0],
      mem: { total, free, used: total - free, pct: 1 - free / total },
      cpuCount: os.cpus()?.length || 1,
      host: os.hostname(),
    };
    io.emit('metrics', payload);
  }, 2000);

  // --- Start
  server.listen(PORT, () => {
    console.log(
      `[blackroad-api] listening on ${PORT} (db: ${DB_PATH}, llm: ${LLM_URL}, shell: ${ALLOW_SHELL})`
    );
  });

  // --- Safety
  process.on('unhandledRejection', (e) => console.error('UNHANDLED', e));
  process.on('uncaughtException', (e) => console.error('UNCAUGHT', e));
})();

module.exports = { app, server, start, INTERNAL_TOKEN, ALLOW_ORIGINS };
module.exports = { app, server, loginLimiter };
function shutdown(done) {
  clearInterval(metricsTimer);
  server.close(done);
}

module.exports = { app, server, shutdown };

  return { server };
}

if (require.main === module) {
  const port = Number.parseInt(process.env.PORT || '4000', 10);
  const allowedOrigins = parseAllowedOrigins(process.env.ALLOW_ORIGINS || '');
  const { server } = createServer({ allowedOrigins });
  server.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`BlackRoad API listening on ${port}`);
  });
}

module.exports = {
  createServer,
  parseAllowedOrigins,
};
