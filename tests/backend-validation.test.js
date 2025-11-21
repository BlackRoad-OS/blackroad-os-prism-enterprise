const test = require('node:test');
const assert = require('node:assert/strict');

const { createServer } = require('../srv/blackroad-api/server_full.js');
const { getAuthCookie } = require('./helpers/auth.js');

async function withServer(options, callback) {
  const { server } = createServer(options);
  await new Promise((resolve) => server.listen(0, resolve));
  const address = server.address();
  const baseUrl = `http://127.0.0.1:${address.port}`;

function closeServer(server) {
  return new Promise((resolve, reject) => {
    server.close((err) => {
      if (err) {
        reject(err);
        return;
      }
      resolve();
    });
  });
}

async function getToken(port) {
  const loginRes = await fetch(`http://127.0.0.1:${port}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'root', password: 'Codex2025' })
  });
  assert.equal(loginRes.status, 200);
  assert.match(loginRes.headers.get('content-type'), /^application\/json/);

  const loginJson = await loginRes.json();
  assert.ok(loginJson.token, 'expected login token');
  return loginJson.token;
}

test('rejects malformed json and missing fields', async () => {
  const server = app.listen(0);
  const port = getPort(server);
  try {
    const token = await getToken(port);
  try {
    await callback({ baseUrl });
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test('rejects malformed json payloads', async () => {
  await withServer({ sessionSecret: 'validation-secret' }, async ({ baseUrl }) => {
    const cookie = await getAuthCookie(baseUrl);

    const response = await fetch(`${baseUrl}/api/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: cookie.join('; '),
      },
      body: '{"title": "missing brace"',
    });
    assert.equal(badRes.status, 400);
    assert.match(badRes.headers.get('content-type'), /^application\/json/);
    const badJson = await badRes.json();
    assert.equal(badJson.error, 'invalid json');

    assert.equal(response.status, 400);
    const body = await response.json();
    assert.equal(body.error, 'invalid json');
  });
});

test('requires a non-empty title field', async () => {
  await withServer({ sessionSecret: 'validation-secret' }, async ({ baseUrl }) => {
    const cookie = await getAuthCookie(baseUrl);

    const response = await fetch(`${baseUrl}/api/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Cookie: cookie.join('; '),
      },
      body: JSON.stringify({ title: '' }),
    });
    assert.equal(missRes.status, 400);
    assert.match(missRes.headers.get('content-type'), /^application\/json/);
    const missJson = await missRes.json();
    assert.equal(missJson.error, 'invalid task');
  } finally {
    await closeServer(server);
  }
});

test('returns json for not found routes', async () => {
  const server = app.listen(0);
  const port = getPort(server);
  try {
    const res = await fetch(`http://127.0.0.1:${port}/nope`);
    assert.equal(res.status, 404);
    assert.match(res.headers.get('content-type'), /^application\/json/);
    const body = await res.json();
    assert.equal(body.error, 'not found');
  } finally {
    await closeServer(server);
  }
});


    assert.equal(response.status, 400);
    const body = await response.json();
    assert.equal(body.error, 'invalid task');
  });
});

test('returns json for unknown routes', async () => {
  await withServer({ sessionSecret: 'validation-secret' }, async ({ baseUrl }) => {
    const response = await fetch(`${baseUrl}/nope`);

    assert.equal(response.status, 404);
    assert.equal(response.headers.get('content-type'), 'application/json; charset=utf-8');
    const body = await response.json();
    assert.equal(body.error, 'not found');
  });
});
