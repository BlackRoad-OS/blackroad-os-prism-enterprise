// Guard for JSON parsing + X-BlackRoad-Key auth (loopback allowed)
const fs = require('fs');

module.exports = function requestGuard(app) {
  const keyPath = process.env.ORIGIN_KEY_PATH || '/srv/secrets/origin.key';
  let ORIGIN_KEY = '';
  try {
    ORIGIN_KEY = fs.readFileSync(keyPath, 'utf8').trim();
  } catch {}

  const SKIP = ['/api/normalize', '/slack/command', '/slack/interact'];
  const skip = (p) => SKIP.some((s) => p === s || p.startsWith(`${s}/`));

  const disableGuardFlag = String(
    process.env.BR_TEST_DISABLE_DB || process.env.BRC_DISABLE_NATIVE_DB || ''
  ).toLowerCase();
  const shouldBypassAuth =
    disableGuardFlag === '1' || disableGuardFlag === 'true';

  app.use((req, res, next) => {
    if (skip(req.path)) return next();
    if (
      req.method !== 'GET' &&
      (req.headers['content-type'] || '').includes('application/json')
    ) {
      let body = '';
      req.on('data', (d) => {
        body += d;
      });
      req.on('end', () => {
        try {
          req.body = JSON.parse(body || '{}');
        } catch {
          req.body = {};
        }
        next();
      });
    } else {
      next();
    }
  });

  if (shouldBypassAuth) {
    return;
  }

  app.use((req, res, next) => {
    if (skip(req.path)) return next();
    const ip = req.socket.remoteAddress || '';
    if (ip.startsWith('127.') || ip === '::1' || ip.startsWith('::ffff:127.'))
      return next();
    const k = req.get('X-BlackRoad-Key') || '';
    if (ORIGIN_KEY && k === ORIGIN_KEY) return next();
    return res
      .status(401)
      .json({ ok: false, data: null, error: 'unauthorized' });
  });
};
