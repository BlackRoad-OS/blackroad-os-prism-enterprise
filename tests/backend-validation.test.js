process.env.JWT_SECRET = 'test-secret';
const { app } = require('../backend/server');

function getPort(server) {
  return server.address().port;
}

describe('backend validation', () => {
  it('rejects malformed json and missing fields', async () => {
    const server = app.listen(0);
    const port = getPort(server);
    try {
      const loginRes = await fetch(`http://127.0.0.1:${port}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'root', password: 'Codex2025' }),
      });
      const loginJson = await loginRes.json();
      const token = loginJson.token;

      const badRes = await fetch(`http://127.0.0.1:${port}/api/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: '{"title": "bad"',
      });
      expect(badRes.status).toBe(400);

      const missRes = await fetch(`http://127.0.0.1:${port}/api/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({}),
      });
      expect(missRes.status).toBe(400);
    } finally {
      server.close();
    }
  });

  it('returns json for not found routes', async () => {
    const server = app.listen(0);
    const port = getPort(server);
    try {
      const res = await fetch(`http://127.0.0.1:${port}/nope`);
      expect(res.status).toBe(404);
      const contentType = res.headers.get('content-type') || '';
      expect(contentType.includes('application/json')).toBe(true);
      const body = await res.json();
      expect(body.error).toBe('not found');
    } finally {
      server.close();
    }
  });
});
