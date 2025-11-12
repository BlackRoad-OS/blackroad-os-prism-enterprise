// Guard for JSON parsing + X-BlackRoad-Key auth (loopback allowed)
const fs = require('fs');
module.exports = function requestGuard(app){
  const keyPath = process.env.ORIGIN_KEY_PATH || '/srv/secrets/origin.key';
  let ORIGIN_KEY = '';
  try {
    ORIGIN_KEY = fs.readFileSync(keyPath, 'utf8').trim();
  } catch {
    // missing key is fine; fall back to header auth only
  }
  const SKIP = [
    '/api/normalize',
    '/slack/command',
    '/slack/interact',
    '/health',
    '/health/live',
    '/health/ready',
    '/api/health',
  ];
  const skip = (p) => SKIP.some(s => p === s || p.startsWith(s + '/'));
  app.use((req,res,next)=>{
    if (skip(req.path)) return next();
    // parse JSON (small, safe)
    if (req.method !== 'GET' && (req.headers['content-type']||'').includes('application/json')) {
      let b=''; req.on('data',d=>b+=d); req.on('end',()=>{ try{ req.body = JSON.parse(b||'{}'); }catch{ req.body={}; } ; next(); });
    } else next();
  });
  app.use((req,res,next)=>{
    if (skip(req.path)) return next();
    const ip = req.socket.remoteAddress || '';
    if (
      ip === '::1' ||
      ip === '::ffff:127.0.0.1' ||
      ip.startsWith('127.') ||
      ip.startsWith('::ffff:127.')
    ) {
      return next();
    }
    const k = req.get('X-BlackRoad-Key') || '';
    return (ORIGIN_KEY && k===ORIGIN_KEY) ? next() : res.status(401).json({ok:false, data:null, error:'unauthorized'});
  });
};
