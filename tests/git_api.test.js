process.env.SESSION_SECRET = 'test-secret';
process.env.INTERNAL_TOKEN = 'x';
process.env.ALLOW_ORIGINS = 'https://example.com';
process.env.GIT_REPO_PATH = process.cwd();
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
  });

  it('returns git health info', async () => {
    const cookie = await getAuthCookie();
    const res = await request(app).get('/api/git/health').set('Cookie', cookie);
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
    expect(typeof res.body.repoPath).toBe('string');
    expect(res.body.readOnly).toBe(true);
  });

  it('returns git status info', async () => {
    const cookie = await getAuthCookie();
    const res = await request(app).get('/api/git/status').set('Cookie', cookie);
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
    expect(typeof res.body.branch).toBe('string');
    expect(res.body.counts).toBeDefined();
    expect(res.body.counts).toHaveProperty('staged');
    expect(res.body.counts).toHaveProperty('unstaged');
    expect(res.body.counts).toHaveProperty('untracked');
    expect(typeof res.body.isDirty).toBe('boolean');
    expect(typeof res.body.shortHash).toBe('string');
    expect(typeof res.body.lastCommitMsg).toBe('string');
  });
});
