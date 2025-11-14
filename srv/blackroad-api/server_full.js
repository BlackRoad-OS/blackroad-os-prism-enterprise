'use strict';

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

const gitRouter = require('./routes/git');

// Custom environment variable loader replaces the standard 'dotenv' package.
// Rationale: We use a custom loader to reduce external dependencies, avoid issues with dotenv's parsing logic,
// and to allow for more controlled loading (e.g., skipping variables already set in process.env).
// See coding guidelines: dependency changes must be documented.
function loadEnvFile() {
  const envPath = process.env.DOTENV_PATH || path.join(process.cwd(), '.env');
  if (!fs.existsSync(envPath)) {
    return;
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
    }
  });
  next();
});

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

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, service: 'blackroad-api', ts: new Date().toISOString() });
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
}

module.exports = { app, server, start, INTERNAL_TOKEN, ALLOW_ORIGINS };
