// Guard for JSON parsing + X-BlackRoad-Key auth (loopback allowed)
const fs = require('fs');
function isLocal(ip) {
  if (!ip) return false;
  if (ip === '::1' || ip.startsWith('127.')) return true;
  if (ip.startsWith('::ffff:')) {
    const mapped = ip.slice('::ffff:'.length);
    if (mapped === '127.0.0.1' || mapped.startsWith('127.')) {
      return true;
    }
  }
  return false;
}

module.exports = function requestGuard(app) {
  const keyPath = process.env.ORIGIN_KEY_PATH || '/srv/secrets/origin.key';
  let ORIGIN_KEY = '';
  try {
    ORIGIN_KEY = fs.readFileSync(keyPath, 'utf8').trim();
  } catch {}
  app.use((req, res, next) => {
    // parse JSON (small, safe)
    if (
      req.method !== 'GET' &&
      (req.headers['content-type'] || '').includes('application/json')
    ) {
      let b = '';
      req.on('data', (d) => (b += d));
      req.on('end', () => {
        try {
          req.body = JSON.parse(b || '{}');
        } catch {
          req.body = {};
        }
        next();
      });
    } else next();
  });
  app.use((req, res, next) => {
    const ip = req.socket.remoteAddress || '';
    if (isLocal(ip)) return next();
    const k = req.get('X-BlackRoad-Key') || '';
    return ORIGIN_KEY && k === ORIGIN_KEY
      ? next()
      : res.status(401).json({ ok: false, data: null, error: 'unauthorized' });
  });
};
