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

      if (body.username === VALID_USER.username && body.password === VALID_USER.password) {
        const sessionId = randomUUID();
        sessions.set(sessionId, { username: VALID_USER.username });
        return sendJson(res, 200, { ok: true }, {
          'Set-Cookie': `session=${sessionId}; HttpOnly; Path=/; SameSite=Lax`,
        });
      }
      return sendJson(res, 401, { error: 'invalid credentials' });
    }

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
