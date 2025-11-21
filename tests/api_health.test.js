// <!-- FILE: tests/api_health.test.js -->
process.env.SESSION_SECRET = 'test-secret';
process.env.INTERNAL_TOKEN = 'x';
process.env.ALLOW_ORIGINS = 'https://example.com';
process.env.MINT_PK = '0x' + '1'.repeat(64);
process.env.CLAIMREG_ADDR = '0x' + '2'.repeat(40);
const request = require('supertest');
const { app, server, loginLimiter } = require('../srv/blackroad-api/server_full.js');
const { app, server } = require('../srv/blackroad-api/server_full.js');
// Login helper reused across tests to obtain authenticated cookies.
// Helper to obtain an auth cookie for requests requiring authentication
const { getAuthCookie } = require('./helpers/auth');

describe('API security and health', () => {
  afterAll((done) => {
    loginLimiter.resetKey('::ffff:127.0.0.1');
    loginLimiter.resetKey('127.0.0.1');
    server.close(done);
process.env.MINT_PK =
  '0x1111111111111111111111111111111111111111111111111111111111111111';
process.env.CLAIMREG_ADDR = '0x2222222222222222222222222222222222222222';
process.env.ETH_RPC_URL = 'http://127.0.0.1:8545';
const request = require('supertest');
const { app, shutdown } = require('../srv/blackroad-api/server_full.js');

describe('API security and health', () => {
  afterAll((done) => {
    shutdown(done);
  });

  it('responds to /health', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
  });

  it('returns security headers on /api/health', async () => {
  it('responds to /healthz', async () => {
    const res = await request(app).get('/healthz');
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
  });

  it('responds to /api/health with security headers', async () => {
    const res = await request(app)
      .get('/api/health')
      .set('Origin', 'https://example.com');
    expect(res.status).toBe(200);
    expect(res.headers['x-dns-prefetch-control']).toBe('off');
    expect(res.headers['access-control-allow-origin']).toBe(
      'https://example.com'
    );
  });

  it('validates login payload', async () => {
    const res = await request(app).post('/api/login').send({});
    expect(res.status).toBe(400);
  });

  it('returns default entitlements for logged-in user', async () => {
    const cookie = await getAuthCookie(app);
    const res = await request(app)
      .get('/api/billing/entitlements/me')
      .set('Cookie', cookie);
    expect(res.status).toBe(200);
    expect(res.body.planName).toBe('Free');
    expect(res.body.entitlements.can.math.pro).toBe(false);
  });

  it('rate limits repeated failed login attempts', async () => {
    loginLimiter.resetKey('::ffff:127.0.0.1');
    loginLimiter.resetKey('127.0.0.1');

    for (let i = 0; i < 5; i += 1) {
      const res = await request(app)
        .post('/api/login')
        .send({ username: 'root', password: 'wrong' });
      expect([400, 401]).toContain(res.status);
    }

    const final = await request(app)
      .post('/api/login')
      .send({ username: 'root', password: 'wrong' });
    expect(final.status).toBe(429);
    expect(final.body.error).toBe('too_many_attempts');
const test = require('node:test');
const assert = require('node:assert/strict');

const { createServer } = require('../srv/blackroad-api/server_full.js');
const { getAuthCookie } = require('./helpers/auth.js');

const allowedOrigin = 'https://example.com';

async function withServer(options, callback) {
  const { server } = createServer(options);
  await new Promise((resolve) => server.listen(0, resolve));
  const address = server.address();
  const baseUrl = `http://127.0.0.1:${address.port}`;

  try {
    await callback({ baseUrl });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test('GET /health responds with ok', async () => {
  await withServer(
    { sessionSecret: 'test-session-secret', allowedOrigins: [allowedOrigin] },
    async ({ baseUrl }) => {
      const response = await fetch(`${baseUrl}/health`, {
        headers: { Origin: allowedOrigin },
      });

      assert.equal(response.status, 200);
      const body = await response.json();
      assert.equal(body.ok, true);
      assert.equal(response.headers.get('access-control-allow-origin'), allowedOrigin);
      assert.ok(response.headers.get('x-request-id'));
    }
  );
});

test('GET /api/health applies security headers', async () => {
  await withServer(
    { sessionSecret: 'test-session-secret', allowedOrigins: [allowedOrigin] },
    async ({ baseUrl }) => {
      const response = await fetch(`${baseUrl}/api/health`, {
        headers: { Origin: allowedOrigin },
      });

      assert.equal(response.status, 200);
      const body = await response.json();
      assert.equal(body.ok, true);
      assert.equal(response.headers.get('x-dns-prefetch-control'), 'off');
      assert.equal(response.headers.get('x-frame-options'), 'SAMEORIGIN');
      assert.equal(response.headers.get('access-control-allow-origin'), allowedOrigin);
    }
  );
});

test('authenticated task creation succeeds', async () => {
  await withServer({ sessionSecret: 'test-session-secret' }, async ({ baseUrl }) => {
    const cookie = await getAuthCookie(baseUrl);

    const response = await fetch(`${baseUrl}/api/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: cookie.join('; '),
      },
      body: JSON.stringify({ title: 'Ship secure endpoint' }),
    });

    assert.equal(response.status, 201);
    const body = await response.json();
    assert.equal(body.ok, true);
    assert.equal(body.task.title, 'Ship secure endpoint');
  });
});
