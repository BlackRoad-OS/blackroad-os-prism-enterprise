'use strict';

const express = require('express');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const router = express.Router();

const CONNECTOR_KEY = process.env.CONNECTOR_KEY || '';
const LOG_FILE = process.env.CONNECTOR_LOG || '/tmp/prism-connectors.log';
const ALLOWED_ROOTS = ['/srv', '/var/www/blackroad'];

function log(event, details = {}) {
  const payload = {
    at: new Date().toISOString(),
    event,
    ...details,
  };
  try {
    fs.appendFileSync(LOG_FILE, JSON.stringify(payload) + '\n', 'utf8');
  } catch (_error) {
    // logging must never break the request pipeline
  }
}

function resolveSafe(targetPath) {
  if (!targetPath) {
    throw new Error('path_required');
  }
  const resolved = path.resolve(targetPath);
  const isAllowed = ALLOWED_ROOTS.some((root) =>
    resolved === root || resolved.startsWith(root + path.sep)
  );
  if (!isAllowed) {
    throw new Error('path_not_allowed');
  }
  return resolved;
}

function requireAuth(req, res, next) {
  const header = req.get('Authorization') || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : '';
  if (!CONNECTOR_KEY) {
    log('auth_skipped', { reason: 'missing_key' });
    return next();
  }
  if (token === CONNECTOR_KEY) {
    return next();
  }
  log('auth_failed', { ip: req.ip, path: req.path });
  return res.status(401).json({ error: 'unauthorized' });
}

router.use(express.json({ limit: '1mb' }));
router.use(requireAuth);

router.post('/paste', (req, res) => {
  try {
    const resolved = resolveSafe(req.body?.path);
    const content = req.body?.content ?? '';
    fs.mkdirSync(path.dirname(resolved), { recursive: true });
    fs.writeFileSync(resolved, content, 'utf8');
    log('paste', { path: resolved, bytes: Buffer.byteLength(content) });
    return res.json({ ok: true, path: resolved });
  } catch (error) {
    log('paste_error', { message: error.message });
    return res.status(400).json({ error: error.message });
  }
});

router.post('/append', (req, res) => {
  try {
    const resolved = resolveSafe(req.body?.path);
    const content = req.body?.content ?? '';
    fs.mkdirSync(path.dirname(resolved), { recursive: true });
    fs.appendFileSync(resolved, content, 'utf8');
    log('append', { path: resolved, bytes: Buffer.byteLength(content) });
    return res.json({ ok: true, path: resolved });
  } catch (error) {
    log('append_error', { message: error.message });
    return res.status(400).json({ error: error.message });
  }
});

router.post('/replace', (req, res) => {
  const body = req.body || {};
  if (!body.path || typeof body.pattern !== 'string' || body.replacement === undefined) {
    return res.status(400).json({ error: 'invalid_body' });
  }
  try {
    const resolved = resolveSafe(body.path);
    const input = fs.readFileSync(resolved, 'utf8');
    const regex = new RegExp(body.pattern, 'g');
    const output = input.replace(regex, body.replacement);
    fs.writeFileSync(resolved, output, 'utf8');
    log('replace', { path: resolved, pattern: body.pattern });
    return res.json({ ok: true, path: resolved });
  } catch (error) {
    log('replace_error', { message: error.message });
    return res.status(400).json({ error: error.message });
  }
});

router.post('/restart', (req, res) => {
  const service = req.body?.service;
  if (!service) {
    return res.status(400).json({ error: 'service_required' });
  }
  exec(`systemctl restart ${service}`, (error) => {
    if (error) {
      log('restart_error', { service, message: error.message });
      return res.status(500).json({ error: error.message });
    }
    log('restart', { service });
    return res.json({ ok: true, service });
  });
});

router.post('/build', (req, res) => {
  const target = req.body?.target;
  if (!target) {
    return res.status(400).json({ error: 'target_required' });
  }

  const commands = {
    frontend: 'cd /srv/blackroad-frontend && npm run build',
    api: 'cd /srv/blackroad-api && npm install',
    llm: 'cd /srv/lucidia-llm && pip install -r requirements.txt',
    math: 'cd /srv/lucidia-math && pip install -r requirements.txt',
  };

  const command = commands[target];
  if (!command) {
    return res.status(400).json({ error: 'unknown_target' });
  }

  exec(command, (error, stdout, stderr) => {
    if (error) {
      log('build_error', { target, message: error.message });
      return res.status(500).json({ error: error.message, stderr });
    }
    log('build', { target });
    return res.json({ ok: true, target, stdout, stderr });
  });
});

module.exports = router;
