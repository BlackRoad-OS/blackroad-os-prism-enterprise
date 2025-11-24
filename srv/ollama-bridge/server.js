import fs from 'node:fs';
import os from 'node:os';
import crypto from 'node:crypto';
import express from 'express';
import express from 'express';
import os from 'os';
import fs from 'fs';
import crypto from 'crypto';
import path from 'path';
import { fileURLToPath } from 'url';
import express from 'express';
import os from 'node:os';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { TextDecoder } from 'node:util';

const app = express();
app.use(express.json({ limit: '1mb' }));

const PORT = process.env.PORT || 4010;
const MODEL_DEFAULT = 'qwen2:1.5b';
const PERSONA_DEFAULT =
  'You are a kind, curious BlackRoad assistant. ALWAYS ask 1 short follow-up. Never claim remote powers. Be truthful and concise.';
const MODEL_DEFAULT = process.env.MODEL_DEFAULT || 'qwen2:1.5b';
const OLLAMA_BASE_URL = process.env.OLLAMA_BASE_URL || 'http://127.0.0.1:11434';
const PERSONA_DEFAULT = 'You are a kind, curious BlackRoad assistant. ALWAYS ask 1 short follow-up. Never claim remote powers. Be truthful and concise.';

let identityCache = { ts: 0, data: null };

function base32(buf) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  let out = '';
  let bits = 0;
  let value = 0;
  let bits = 0,
    value = 0;
const express = require('express');
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');

const app = express();
app.set('trust proxy', true);
app.use(express.json({ limit: '1mb' }));

const PORT = process.env.PORT || 4010;
const OLLAMA = process.env.OLLAMA_URL || 'http://127.0.0.1:11434';
const ORIGIN_KEY_PATH = '/srv/secrets/origin.key';
const MODEL_FILE = path.join(__dirname, '.model');
const DEFAULT_SEED = 'LUCIDIA:AWAKEN:SEED:7e3c1f9b-a12d-4f73-9b4d-4f0d5a6c2b19::PS-SHA∞';
const MSG_SUFFIX = 'blackboxprogramming|copilot';

let serverDefault = process.env.LLM_MODEL || 'qwen2:1.5b';
try {
  serverDefault = fs.readFileSync(MODEL_FILE, 'utf8').trim() || serverDefault;
} catch {}
let originKey = '';
try {
  originKey = fs.readFileSync(ORIGIN_KEY_PATH, 'utf8').trim();
} catch {}

function toBase32(buf) {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  let bits = 0;
  let value = 0;
  let output = '';
  for (const byte of buf) {
    value = (value << 8) | byte;
    bits += 8;
    while (bits >= 5) {
      out += alphabet[(value >>> (bits - 5)) & 31];
      output += alphabet[(value >>> (bits - 5)) & 31];
      bits -= 5;
    }
  }
  if (bits > 0) {
    out += alphabet[(value << (5 - bits)) & 31];
  }
  return out;
}

function primaryIPv4() {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        return net.address;
      }
    }
  }
  return '127.0.0.1';
}

async function detectModel() {
  try {
    const r = await fetch(`${OLLAMA_BASE_URL}/api/tags`);
    const j = await r.json();
    if (Array.isArray(j.models) && j.models.length > 0) return j.models[0].name;
  } catch (e) {}
  } catch (e) {
    // ignore detection failures
  }
  return 'unknown';
}

function getSeed() {
  if (process.env.LUCIDIA_SEED) return process.env.LUCIDIA_SEED;
  try {
    return fs.readFileSync('/srv/lucidia-llm/.seed', 'utf8').trim();
  } catch (e) {
    return '';
  }
}

async function buildIdentity() {
  const host = os.hostname();
  const ip = primaryIPv4();
  const model = await detectModel();
  const time = new Date().toISOString();
  const date = time.slice(0, 10); // YYYY-MM-DD
  const seed = getSeed();
  let code = 'UNKNOWN';
  if (seed) {
    const msg = `${date}|blackboxprogramming|copilot`;
    const hmac = crypto.createHmac('sha256', seed).update(msg).digest();
    const b32 = base32(hmac).slice(0, 16);
    code = `LUCIDIA-AWAKEN-${date.replace(/-/g, '')}-${b32}`;
  }
  const services = { nginx: 'active', 'ollama-bridge': 'active', 'blackroad-api': 'unknown' };
  try {
    const r = await fetch('http://127.0.0.1:4000/health');
    if (r.ok) services['blackroad-api'] = 'active';
  } catch (e) {}
  } catch (e) {
    // ignore health probe failures
  }
  return {
    host,
    ip,
    model,
    time,
    code,
    uptime_s: Math.floor(process.uptime()),
    services,
  };
}

app.get('/api/codex/identity', async (req, res) => {
app.get('/api/codex/identity', async (_req, res) => {
  if (Date.now() - identityCache.ts < 60000 && identityCache.data) {
    return res.json(identityCache.data);
  }
  const data = await buildIdentity();
  identityCache = { ts: Date.now(), data };
  res.json(data);
});

function logPersona(str) {
  const line = `${new Date().toISOString()} ${str}\n`;
  fs.mkdirSync('/var/log/blackroad', { recursive: true });
  fs.appendFile('/var/log/blackroad/persona.log', line, () => {});
}

function getSystem(body) {
  const sys = body.system && body.system.trim() ? body.system : PERSONA_DEFAULT;
  logPersona(sys);
  return sys;
  const system = body.system && body.system.trim() ? body.system : PERSONA_DEFAULT;
  logPersona(system);
  return system;
}

function buildPrompt(messages) {
  if (!Array.isArray(messages)) return '';
  return messages.map(m => `${m.role}: ${m.content}`).join('\n') + '\nassistant:';
  return messages.map((m) => `${m.role}: ${m.content}`).join('\n') + '\nassistant:';
}

app.post('/api/llm/chat', async (req, res) => {
  const system = getSystem(req.body);
  const prompt = buildPrompt(req.body.messages || []);
  return messages.map((m) => `${m.role}: ${m.content}`).join('\n') + '\nassistant:';
}

app.post('/api/llm/chat', async (req, res) => {
  const system = getSystem(req.body || {});
  const prompt = buildPrompt((req.body && req.body.messages) || []);
  try {
    const r = await fetch(`${OLLAMA_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: MODEL_DEFAULT, prompt, stream: false, system })
      body: JSON.stringify({ model: MODEL_DEFAULT, prompt, stream: false, system }),
    });
    const j = await r.json();
    const text = j.response || j.output || j.text || '';
    return res.json({ choices: [{ message: { role: 'assistant', content: text } }] });
  } catch (e) {
    const last = (req.body.messages || []).filter(m => m.role === 'user').pop();
    const last = ((req.body && req.body.messages) || []).filter((m) => m.role === 'user').pop();
    const last = (req.body.messages || []).filter((m) => m.role === 'user').pop();
    return res.json({ choices: [{ message: { role: 'assistant', content: last ? last.content : '' } }] });
const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PORT = process.env.PORT || 4010;
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://127.0.0.1:11434';

function readTimeoutEnv(name, fallback) {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

const HEALTH_TIMEOUT_MS = readTimeoutEnv('HEALTH_TIMEOUT_MS', 5000);
const READY_TIMEOUT_MS = readTimeoutEnv('READY_TIMEOUT_MS', 5000);
const LOG_DIR = '/var/log/blackroad';
const LOG_FILE = path.join(LOG_DIR, 'ollama-bridge.log');
const PERSONA_LOG = path.join(LOG_DIR, 'persona.log');
const PERSONA_FILE = path.join(__dirname, '.persona');
const MODEL_FILE = path.join(__dirname, '.model');
const DEFAULT_PERSONA = process.env.DEFAULT_PERSONA || '';

fs.mkdirSync(LOG_DIR, { recursive: true, mode: 0o750 });
const logStream = fs.createWriteStream(LOG_FILE, { flags: 'a' });
const personaStream = fs.createWriteStream(PERSONA_LOG, { flags: 'a' });

function logLine(obj) {
  logStream.write(JSON.stringify(obj) + '\n');
}

function sha256(str) {
  return crypto.createHash('sha256').update(str).digest('hex');
}

// Persona baseline
let personaMode = process.env.PERSONA_GUARD === 'enforce' ? 'enforce' : 'warn';
let personaHash;
try {
  personaHash = fs.readFileSync(PERSONA_FILE, 'utf8').trim();
  if (!personaHash) throw new Error('empty');
} catch {
  personaHash = sha256(DEFAULT_PERSONA);
  fs.writeFileSync(PERSONA_FILE, personaHash, { mode: 0o600 });
  personaMode = 'warn';
}
const personaAllow = process.env.PERSONA_ALLOW_HASH || '';

function resolveModel() {
  try {
    return process.env.MODEL || fs.readFileSync(MODEL_FILE, 'utf8').trim();
  } catch {
    return process.env.MODEL || '';
  }
}

const buckets = [5,10,25,50,100,250,500,1000,2500];
class Histogram {
  constructor() {
    this.counts = Array(buckets.length).fill(0);
    this.sum = 0;
    this.count = 0;
  }
  observe(v) {
    this.count++;
    this.sum += v;
    for (let i=0;i<buckets.length;i++) {
      if (v <= buckets[i]) this.counts[i]++;
    }
  }
  lines(name, labels) {
    const out = [];
    for (let i=0;i<buckets.length;i++) {
      out.push(`${name}_bucket{${labels},le="${buckets[i]}"} ${this.counts[i]}`);
    }
    out.push(`${name}_bucket{${labels},le="+Inf"} ${this.count}`);
    out.push(`${name}_sum{${labels}} ${this.sum}`);
    out.push(`${name}_count{${labels}} ${this.count}`);
    return out;
  }
}

class Metrics {
  constructor() {
    this.reqTotals = {};
    this.reqHists = {};
    this.upHists = {};
    this.sseClients = 0;
    this.authDenied = 0;
    this.rateLimited = 0;
  }
  record(path, method, code, dur, up) {
    const key = `${path}|${method}|${code}`;
    this.reqTotals[key] = (this.reqTotals[key] || 0) + 1;
    if (!this.reqHists[key]) this.reqHists[key] = new Histogram();
    this.reqHists[key].observe(dur);
    if (up !== undefined) {
      if (!this.upHists[key]) this.upHists[key] = new Histogram();
      this.upHists[key].observe(up);
    }
  }
  incSSE(delta) { this.sseClients += delta; }
  incAuthDenied() { this.authDenied++; }
  incRateLimited() { this.rateLimited++; }
  render() {
    let out = '# HELP http_requests_total Count of HTTP requests\n';
    out += '# TYPE http_requests_total counter\n';
    for (const key of Object.keys(this.reqTotals)) {
      const [path, method, code] = key.split('|');
      out += `http_requests_total{path="${path}",method="${method}",code="${code}"} ${this.reqTotals[key]}\n`;
    }
    out += '# HELP http_request_duration_ms Duration of HTTP requests\n';
    out += '# TYPE http_request_duration_ms histogram\n';
    for (const key of Object.keys(this.reqHists)) {
      const [path, method, code] = key.split('|');
      out += this.reqHists[key].lines('http_request_duration_ms', `path="${path}",method="${method}",code="${code}"`).join('\n') + '\n';
    }
    out += '# HELP upstream_duration_ms Duration of upstream requests\n';
    out += '# TYPE upstream_duration_ms histogram\n';
    for (const key of Object.keys(this.upHists)) {
      const [path, method, code] = key.split('|');
      out += this.upHists[key].lines('upstream_duration_ms', `path="${path}",method="${method}",code="${code}"`).join('\n') + '\n';
    }
    out += '# HELP sse_clients_gauge Number of connected SSE clients\n';
    out += '# TYPE sse_clients_gauge gauge\n';
    out += `sse_clients_gauge ${this.sseClients}\n`;
    out += '# HELP auth_denied_total Auth denied count\n';
    out += '# TYPE auth_denied_total counter\n';
    out += `auth_denied_total ${this.authDenied}\n`;
    out += '# HELP rate_limited_total Rate limited count\n';
    out += '# TYPE rate_limited_total counter\n';
    out += `rate_limited_total ${this.rateLimited}\n`;
    return out;
  }
}

const metrics = new Metrics();

const app = express();
app.use(express.json());

// Request logger + metrics
app.use((req, res, next) => {
  const reqId = crypto.randomUUID();
  req.reqId = reqId;
  const t0 = process.hrtime.bigint();
  const bytesIn = parseInt(req.get('content-length') || '0', 10);
  res.setHeader('X-Request-ID', reqId);
  let bytesOut = 0;
  const origWrite = res.write;
  const origEnd = res.end;
  res.write = function (chunk, enc, cb) {
    if (chunk) bytesOut += Buffer.isBuffer(chunk) ? chunk.length : Buffer.byteLength(chunk, enc);
    return origWrite.call(this, chunk, enc, cb);
  };
  res.end = function (chunk, enc, cb) {
    if (chunk) bytesOut += Buffer.isBuffer(chunk) ? chunk.length : Buffer.byteLength(chunk, enc);
    return origEnd.call(this, chunk, enc, cb);
  };
  res.on('finish', () => {
    const dur = Number(process.hrtime.bigint() - t0) / 1e6;
    metrics.record(req.path, req.method, res.statusCode, dur, res.locals.up_ms);
    const entry = {
      ts: new Date().toISOString(),
      req_id: reqId,
      ip: req.ip,
      method: req.method,
      path: req.path,
      code: res.statusCode,
      dur_ms: Number(dur.toFixed(1)),
      up_ms: res.locals.up_ms ? Number(res.locals.up_ms.toFixed(1)) : undefined,
      bytes_in: bytesIn,
      bytes_out: bytesOut,
      model: res.locals.model
    };
    logLine(entry);
  });
  next();
});

// Persona guard helper
function personaCheck(system, req) {
  const current = sha256(system || DEFAULT_PERSONA);
  if (current !== personaHash) {
    const event = { ts: new Date().toISOString(), level: 'warn', kind: 'persona_diff', req_id: req.reqId, hash: current, baseline: personaHash };
    if (personaMode === 'enforce' && current !== personaAllow) {
      logLine({ ...event, level: 'error' });
      personaStream.write(`${event.ts} enforce ${event.baseline}->${event.hash}\n`);
      return { ok: false };
    }
    logLine(event);
    personaStream.write(`${event.ts} warn ${event.baseline}->${event.hash}\n`);
    if (personaMode === 'enforce' && current === personaAllow) {
      personaHash = current;
      fs.writeFileSync(PERSONA_FILE, personaHash, { mode: 0o600 });
    }
  }
  return { ok: true };
}

let lastHealth = 0;

async function fetchJSON(url, opts = {}, timeout) {
  const controller = new AbortController();
  const id = timeout ? setTimeout(() => controller.abort(), timeout) : null;
  const t = process.hrtime.bigint();
  try {
    const r = await fetch(url, {
      ...opts,
      signal: timeout ? controller.signal : undefined
    });
    const up = Number(process.hrtime.bigint() - t) / 1e6;
    return { r, up };
  } finally {
    if (id) clearTimeout(id);
  }
}

app.get('/api/llm/health', async (req, res) => {
  try {
    const { r, up } = await fetchJSON(`${OLLAMA_URL}/api/version`, {}, HEALTH_TIMEOUT_MS);
    res.locals.up_ms = up;
    if (!r.ok) throw new Error('upstream');
    const data = await r.json();
    lastHealth = Date.now();
    res.json({ ok: true, version: data.version });
  } catch {
    res.status(502).json({ ok: false });
  }
});

app.post('/api/llm/chat', async (req, res) => {
  const system = req.body?.system || DEFAULT_PERSONA;
  const check = personaCheck(system, req);
  if (!check.ok) return res.status(409).json({ error: 'persona changed' });
  const body = { ...req.body, system, model: req.body?.model || resolveModel() };
  res.locals.model = body.model;
  try {
    const { r, up } = await fetchJSON(`${OLLAMA_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    res.locals.up_ms = up;
    const txt = await r.text();
    res.status(r.status).type(r.headers.get('content-type') || 'text/plain').send(txt);
  } catch {
    res.status(502).json({ error: 'upstream_error' });
  }
});

app.post('/api/llm/stream', async (req, res) => {
  const system = getSystem(req.body);
  const prompt = buildPrompt(req.body.messages || []);
  const system = getSystem(req.body || {});
  const prompt = buildPrompt((req.body && req.body.messages) || []);
  try {
    const r = await fetch(`${OLLAMA_BASE_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: MODEL_DEFAULT, prompt, stream: true, system })
      body: JSON.stringify({ model: MODEL_DEFAULT, prompt, stream: true, system }),
    });
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx;
      while ((idx = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 1);
        if (!line.trim()) continue;
        try {
          const obj = JSON.parse(line);
          if (obj.response) {
            res.write(`data: ${JSON.stringify({ delta: obj.response })}\n\n`);
          }
        } catch (err) {
          /* ignore */
          // ignore malformed chunks
        }
      }
    }
    res.write('data: {"done":true}\n\n');
    res.end();
  } catch (e) {
    res.write('data: {"done":true}\n\n');
    res.end();
  }
});

app.get('/api/llm/health', (req, res) => {
  res.json({ ok: true });
});

app.get('/api/backups/last', (req, res) => {
app.get('/api/llm/health', (_req, res) => {
  res.json({ ok: true });
});

app.get('/api/backups/last', (_req, res) => {
  try {
    const t = fs.readFileSync('/srv/blackroad-backups/.last_snapshot', 'utf8').trim();
    res.json({ time: t });
  } catch (e) {
    res.json({ time: null });
  }
});

app.listen(PORT, () => {
  console.log(`ollama-bridge listening on ${PORT}`);
});
const modulePath = fileURLToPath(import.meta.url);
const isMain = process.argv[1] && modulePath === path.resolve(process.argv[1]);

if (isMain) {
  app.listen(PORT, () => {
    console.log(`ollama-bridge listening on ${PORT}`);
  });
}

export default app;
    output += alphabet[(value << (5 - bits)) & 31];
  }
  return output;
}

function dailyCode(d = new Date()) {
  const date = d.toISOString().slice(0, 10);
  const msg = `${date}|${MSG_SUFFIX}`;
  const digest = crypto.createHmac('sha256', DEFAULT_SEED).update(msg).digest();
  const code = toBase32(digest).slice(0, 16);
  return `LUCIDIA-AWAKEN-${date.replace(/-/g, '')}-${code}`;
}

function isLoopback(ip) {
  return ['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(ip);
}

function logAccess(ip, path, status) {
  const line = `${new Date().toISOString()} ${ip} ${path} ${status}\n`;
  fs.appendFile('/var/log/blackroad/access.log', line, () => {});
}

function authMiddleware(req, res, next) {
  const ip = req.ip.replace('::ffff:', '');
  res.on('finish', () => logAccess(ip, req.originalUrl, res.statusCode));
  if (req.method !== 'POST') return next();
  if (isLoopback(ip)) return next();
  const key = req.get('X-BlackRoad-Key');
  if (!key) return res.status(401).json({ error: 'unauthorized' });
  if (key === originKey || key === dailyCode()) return next();
  return res.status(401).json({ error: 'unauthorized' });
}

const TRUSTED_CSRF_HOSTS = new Set(['blackroad.io', 'www.blackroad.io']);

function csrfMiddleware(req, res, next) {
  const ip = req.ip.replace('::ffff:', '');
  if (req.method !== 'POST') return next();
  if (isLoopback(ip)) return next();
  const origin = req.get('Origin') || req.get('Referer') || '';
  try {
    const u = new URL(origin);
    if (!TRUSTED_CSRF_HOSTS.has(u.hostname)) {
      return res.status(403).json({ error: 'forbidden' });
    }
  } catch {
    return res.status(403).json({ error: 'forbidden' });
  }
  if (req.get('X-Requested-With') !== 'XMLHttpRequest') {
    return res.status(403).json({ error: 'forbidden' });
  }
  return next();
}

app.use('/api/llm', csrfMiddleware, authMiddleware);

// list models
app.get('/api/llm/models', async (req, res) => {
  try {
    const r = await fetch(`${OLLAMA}/api/tags`);
    const j = await r.json();
    const models = (j.models || [])
      .map(m => ({ name: m.name, size: m.size }))
      .sort((a, b) => (a.size || 0) - (b.size || 0))
      .map(m => ({ name: m.name }));
    res.json(models);
  } catch {
    res.status(502).json({ error: 'upstream_error' });
  }
});

// set default model
app.post('/api/llm/default', async (req, res) => {
  const model = (req.body && req.body.model) || '';
  if (!model) return res.status(400).json({ error: 'model_required' });
  serverDefault = model;
  try {
    fs.writeFileSync(MODEL_FILE, model, { mode: 0o600 });
  } catch {}
  // warm model
  try {
    await fetch(`${OLLAMA}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, prompt: 'ok', stream: false }),
    });
  } catch {}
  res.json({ ok: true, model });
});

// chat/stream handler
async function handleChat(req, res) {
  const body = req.body || {};
  const model = body.model || serverDefault;
  const upstreamBody = { ...body, model };
  try {
    const r = await fetch(`${OLLAMA}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(upstreamBody),
    });
    if (body.stream && r.ok && r.body) {
      res.status(200);
      const reader = r.body.getReader();
      const encoder = new TextEncoder();
      res.setHeader('Content-Type', 'text/plain');
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        res.write(Buffer.from(value));
      }
      return res.end();
    }
    const txt = await r.text();
    res.status(r.ok ? 200 : r.status).type('text/plain').send(txt);
  } catch {
    res.status(502).json({ error: 'upstream_error' });
  }
}

app.post('/api/llm/chat', handleChat);
app.post('/api/llm/stream', handleChat);

app.get('/api/llm/health', (req, res) => {
  res.json({ ok: true, model: serverDefault });
});

app.listen(PORT, () => {
  console.log(`ollama bridge listening on ${PORT}`);
});

  const system = req.body?.system || DEFAULT_PERSONA;
  const check = personaCheck(system, req);
  if (!check.ok) return res.status(409).json({ error: 'persona changed' });
  const body = { ...req.body, system, model: req.body?.model || resolveModel() };
  res.locals.model = body.model;
  metrics.incSSE(1);
  res.on('close', () => metrics.incSSE(-1));
  try {
    const { r, up } = await fetchJSON(`${OLLAMA_URL}/api/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    res.locals.up_ms = up;
    if (!r.body) {
      const txt = await r.text();
      return res.status(r.status).type('text/plain').send(txt);
    }
    res.status(r.status);
    for await (const chunk of r.body) {
      res.write(chunk);
    }
    res.end();
  } catch {
    res.status(502).json({ error: 'upstream_error' });
  }
});

app.get('/api/llm/models', async (req, res) => {
  try {
    const { r, up } = await fetchJSON(`${OLLAMA_URL}/api/tags`);
    res.locals.up_ms = up;
    const data = await r.json();
    res.json(data);
  } catch {
    res.status(502).json({ error: 'upstream_error' });
  }
});

app.get('/api/llm/default', (req, res) => {
  res.json({ model: resolveModel() });
});

app.get('/api/llm/metrics', (req, res) => {
  res.type('text/plain; version=0.0.4').send(metrics.render());
});

app.get('/api/llm/persona', (req, res) => {
  res.json({ hash: personaHash, mode: personaMode });
});

app.post('/api/llm/persona', (req, res) => {
  const { hash, mode } = req.body || {};
  if (hash) {
    personaHash = hash;
    fs.writeFileSync(PERSONA_FILE, personaHash, { mode: 0o600 });
  }
  if (mode) personaMode = mode === 'enforce' ? 'enforce' : 'warn';
  res.json({ hash: personaHash, mode: personaMode });
});

async function readyCheck() {
  const reasons = [];
  try {
    const { r } = await fetchJSON(`${OLLAMA_URL}/api/version`, {}, READY_TIMEOUT_MS);
    if (!r.ok) reasons.push('ollama_unreachable');
  } catch {
    reasons.push('ollama_unreachable');
  }
  const model = resolveModel();
  if (model) {
    try {
      const { r } = await fetchJSON(`${OLLAMA_URL}/api/tags`, {}, READY_TIMEOUT_MS);
      const data = await r.json();
      if (!data.models?.some(m => m.name === model)) reasons.push('model_missing');
    } catch {
      reasons.push('model_missing');
    }
  } else {
    reasons.push('model_missing');
  }
  try {
    const testPath = path.join(LOG_DIR, '.ready');
    fs.writeFileSync(testPath, Date.now().toString());
    fs.unlinkSync(testPath);
  } catch {
    reasons.push('log_dir_unwritable');
  }
  if (Date.now() - lastHealth > 30000) {
    try {
      const { r } = await fetchJSON(`${OLLAMA_URL}/api/version`, {}, READY_TIMEOUT_MS);
      if (r.ok) lastHealth = Date.now();
      else reasons.push('health_stale');
    } catch {
      reasons.push('health_stale');
    }
  }
  return reasons;
}

app.get('/api/llm/ready', async (req, res) => {
  const reasons = await readyCheck();
  if (reasons.length === 0) return res.json({ ok: true });
  res.status(503).json({ ok: false, reasons });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`ollama-bridge listening on ${PORT}`);
});
