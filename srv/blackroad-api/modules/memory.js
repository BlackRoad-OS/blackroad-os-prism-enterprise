// Local memory index/search using SQLite + FTS5 + Ollama embeddings.
// Falls back to an in-memory stub when better-sqlite3 is unavailable.
const fs = require('fs');
const path = require('path');

const disableDbFlag = String(
  process.env.BR_TEST_DISABLE_DB || process.env.BRC_DISABLE_NATIVE_DB || ''
).toLowerCase();
const SHOULD_DISABLE_DB = disableDbFlag === '1' || disableDbFlag === 'true';

let Database;
if (!SHOULD_DISABLE_DB) {
  try {
    Database = require('better-sqlite3');
  } catch (err) {
    console.warn(
      '[memory] better-sqlite3 unavailable, using in-memory stub:',
      err
    );
  }
} else {
  console.warn(
    '[memory] native database disabled via env flag; using in-memory stub'
  );
}

function attachStub({ app }) {
  const docs = new Map();
  app.post('/api/memory/index', async (req, res) => {
    let raw = '';
    req.on('data', (d) => {
      raw += d;
    });
    await new Promise((resolve) => req.on('end', resolve));
    let body = {};
    try {
      body = raw ? JSON.parse(raw) : {};
    } catch {
      return res.status(400).json({ error: 'invalid json' });
    }
    const id =
      body.id || `doc:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
    const text = String(body.text || '').slice(0, 200000);
    if (!text) return res.status(400).json({ error: 'missing text' });
    const meta = { source: body.source || null, tags: body.tags || [] };
    docs.set(id, { text, meta, ts: Date.now() });
    return res.json({ ok: true, id });
  });

  app.post('/api/memory/search', async (req, res) => {
    let raw = '';
    req.on('data', (d) => {
      raw += d;
    });
    await new Promise((resolve) => req.on('end', resolve));
    let body = {};
    try {
      body = raw ? JSON.parse(raw) : {};
    } catch {
      return res.status(400).json({ error: 'invalid json' });
    }
    const q = String(body.q || '').trim();
    const k = Math.max(1, Math.min(20, body.top_k || 5));
    if (!q) return res.status(400).json({ error: 'empty query' });
    const lc = q.toLowerCase();
    const results = [];
    for (const [id, entry] of docs.entries()) {
      if (!entry?.text) continue;
      if (entry.text.toLowerCase().includes(lc)) {
        results.push({
          id,
          score: 1,
          text: entry.text.slice(0, 2000),
          meta: entry.meta,
        });
      }
    }
    return res.json({ results: results.slice(0, k) });
  });

  console.log('[memory] in-memory stub online');
}

module.exports = function attachMemory({ app }) {
  if (!app) return;

  if (!Database) {
    attachStub({ app });
    return;
  }

  const DBP = process.env.MEMORY_DB || '/srv/blackroad-api/memory.db';
  fs.mkdirSync(path.dirname(DBP), { recursive: true });
  const db = new Database(DBP);
  db.exec(`CREATE TABLE IF NOT EXISTS docs (id TEXT PRIMARY KEY, text TEXT, meta TEXT, ts INTEGER);
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text, content='docs', content_rowid='rowid');
CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN INSERT INTO fts(rowid,text) VALUES (new.rowid, new.text); END;
CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN INSERT INTO fts(fts, rowid, text) VALUES('delete', old.rowid, old.text); END;
CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs BEGIN INSERT INTO fts(fts, rowid, text) VALUES('delete', old.rowid, old.text); INSERT INTO fts(rowid,text) VALUES (new.rowid, new.text); END;
CREATE TABLE IF NOT EXISTS vecs (id TEXT PRIMARY KEY, v TEXT);`);

  async function embed(text) {
    const r = await fetch('http://127.0.0.1:11434/api/embeddings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: process.env.EMBED_MODEL || 'nomic-embed-text',
        prompt: text,
      }),
    });
    const j = await r.json();
    return j.embedding || j.data?.[0]?.embedding || [];
  }

  function run(sql, p = []) {
    return Promise.resolve(db.prepare(sql).run(p));
  }
  function all(sql, p = []) {
    return Promise.resolve(db.prepare(sql).all(p));
  }
  function get(sql, p = []) {
    return Promise.resolve(db.prepare(sql).get(p));
  }

  function cosine(a, b) {
    let dot = 0;
    let na = 0;
    let nb = 0;
    for (let i = 0; i < Math.min(a.length, b.length); i += 1) {
      dot += a[i] * b[i];
      na += a[i] * a[i];
      nb += b[i] * b[i];
    }
    return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-9);
  }

  app.post('/api/memory/index', async (req, res) => {
    let raw = '';
    req.on('data', (d) => {
      raw += d;
    });
    await new Promise((resolve) => req.on('end', resolve));
    const body = raw ? JSON.parse(raw) : {};
    const id =
      body.id || `doc:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
    const text = String(body.text || '').slice(0, 200000);
    const meta = JSON.stringify({
      source: body.source || null,
      tags: body.tags || [],
    });
    if (!text) return res.status(400).json({ error: 'missing text' });
    await run(`INSERT OR REPLACE INTO docs(id,text,meta,ts) VALUES(?,?,?,?)`, [
      id,
      text,
      meta,
      Date.now(),
    ]);
    const chunks = [];
    for (let i = 0; i < text.length; i += 1000)
      chunks.push(text.slice(i, i + 1000));
    const embs = [];
    for (const chunk of chunks) {
      embs.push(await embed(chunk));
    }
    await run(`INSERT OR REPLACE INTO vecs(id,v) VALUES(?,?)`, [
      id,
      JSON.stringify(embs.flat().slice(0, 1536)),
    ]);
    return res.json({ ok: true, id });
  });

  app.post('/api/memory/search', async (req, res) => {
    let raw = '';
    req.on('data', (d) => {
      raw += d;
    });
    await new Promise((resolve) => req.on('end', resolve));
    const body = raw ? JSON.parse(raw) : {};
    const q = String(body.q || '').trim();
    const k = Math.max(1, Math.min(20, body.top_k || 5));
    if (!q) return res.status(400).json({ error: 'empty query' });
    const rows = await all(
      `SELECT id, text, meta FROM docs WHERE rowid IN (SELECT rowid FROM fts WHERE fts MATCH ? LIMIT 50)`,
      [q.split(/\s+/).join(' ')]
    );
    const qv = await embed(q);
    const scored = [];
    for (const r of rows) {
      const vrow = await get(`SELECT v FROM vecs WHERE id=?`, [r.id]);
      const v = vrow ? JSON.parse(vrow.v) : [];
      scored.push({
        id: r.id,
        score: cosine(qv, v),
        text: r.text.slice(0, 2000),
        meta: JSON.parse(r.meta || '{}'),
      });
    }
    scored.sort((a, b) => b.score - a.score);
    return res.json({ results: scored.slice(0, k) });
  });

  console.log('[memory] online:', DBP);
};
