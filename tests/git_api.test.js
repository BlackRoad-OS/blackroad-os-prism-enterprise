process.env.SESSION_SECRET = 'test-secret'; // pragma: allowlist secret
process.env.INTERNAL_TOKEN = 'x';
process.env.ALLOW_ORIGINS = 'https://example.com';
process.env.GIT_REPO_PATH = process.cwd();
process.env.MINT_PK = '0x' + '1'.repeat(64);
process.env.CLAIMREG_ADDR = '0x' + '2'.repeat(40);

const request = require('supertest');
const { app, server } = require('../srv/blackroad-api/server_full.js');
// Shared helper that logs in and returns authentication cookies for requests.
// Helper to log in and retrieve the auth cookie for authenticated requests
const { getAuthCookie } = require('./helpers/auth');
process.env.MINT_PK =
  '0x1111111111111111111111111111111111111111111111111111111111111111';
process.env.CLAIMREG_ADDR = '0x2222222222222222222222222222222222222222';
process.env.ETH_RPC_URL = 'http://127.0.0.1:8545';

const request = require('supertest');
const { app, shutdown } = require('../srv/blackroad-api/server_full.js');

// Logs in to the API and returns the authentication cookie
async function getAuthCookie() {
  const login = await request(app)
    .post('/api/login')
    .send({ username: 'root', password: 'Codex2025' });
  return login.headers['set-cookie'];
}

describe('Git API', () => {
  afterAll((done) => {
    shutdown(done);
process.env.SESSION_SECRET = 'test-secret';
process.env.INTERNAL_TOKEN = 'x';
process.env.ALLOW_ORIGINS = 'https://example.com';
process.env.GIT_REPO_PATH = process.cwd();
process.env.BR_TEST_DISABLE_DB = '1';
process.env.MINT_PK = '0x' + '11'.repeat(32);

const request = require('supertest');
const { app, server } = require('../srv/blackroad-api/server_full.js');

describe('Git API', () => {
  afterAll((done) => {
    server.close(done);
  });

  it('returns git health info', async () => {
    const login = await request(app)
      .post('/api/login')
      .send({ username: 'root', password: 'Codex2025' }); // pragma: allowlist secret
    const cookie = login.headers['set-cookie'];
    const cookie = await getAuthCookie(app);
    const res = await request(app)
      .get('/api/git/health')
      .set('Cookie', cookie);
    const cookie = await getAuthCookie();
    const res = await request(app).get('/api/git/health').set('Cookie', cookie);
      .send({ username: 'root', password: 'Codex2025' });
    const cookie = login.headers['set-cookie'];
    const res = await request(app)
      .get('/api/git/health')
      .set('Cookie', cookie);
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
    expect(typeof res.body.repoPath).toBe('string');
    expect(res.body.readOnly).toBe(true);
  });

  it('returns git status info', async () => {
    const login = await request(app)
      .post('/api/login')
      .send({ username: 'root', password: 'Codex2025' }); // pragma: allowlist secret
    const cookie = login.headers['set-cookie'];
    const cookie = await getAuthCookie(app);
    const res = await request(app)
      .get('/api/git/status')
      .set('Cookie', cookie);
    const cookie = await getAuthCookie();
    const res = await request(app).get('/api/git/status').set('Cookie', cookie);
    expect(res.status).toBe(200);
    expect(typeof res.body.ok).toBe('boolean');
    expect(res.body.ok).toBe(!res.body.isDirty);
    expect(res.body.ok).toBe(true);
    expect(typeof res.body.branch).toBe('string');
    expect(typeof res.body.shortHash).toBe('string');
    expect(typeof res.body.ahead).toBe('number');
    expect(typeof res.body.behind).toBe('number');
      .send({ username: 'root', password: 'Codex2025' });
    const cookie = login.headers['set-cookie'];
    const res = await request(app).get('/api/git/status').set('Cookie', cookie);
    expect(res.status).toBe(200);
    expect(typeof res.body.branch).toBe('string');
    expect(res.body.counts).toBeDefined();
    expect(res.body.counts).toHaveProperty('staged');
    expect(res.body.counts).toHaveProperty('unstaged');
    expect(res.body.counts).toHaveProperty('untracked');
    expect(typeof res.body.isDirty).toBe('boolean');
  });
});
