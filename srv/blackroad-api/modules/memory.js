// Local memory index/search using SQLite + FTS5 + Ollama embeddings
// DB: /srv/blackroad-api/memory.db  Tables: docs(id TEXT PK, text, meta JSON, ts INT)
//      fts(content uses content=docs, content_rowid=rowid)
const fs = require('fs');
const path = require('path');
const readline = require('readline');

let Database;
let databaseLoadError = null;
try {
  Database = require('better-sqlite3');
} catch (error) {
  databaseLoadError = error;
}

module.exports = function attachMemory({ app }) {
  const DBP = process.env.MEMORY_DB || '/srv/blackroad-api/memory.db';
  const FALLBACK_FILE =
    process.env.MEMORY_FALLBACK_FILE || '/home/agents/cecilia/logs/memory.txt';

  fs.mkdirSync(path.dirname(DBP), { recursive: true });

  let db;
  let fallbackMode = false;

  try {
    if (!Database) {
      throw databaseLoadError || new Error('better-sqlite3 unavailable');
    }
    db = new Database(DBP);
    db.exec(`CREATE TABLE IF NOT EXISTS docs (id TEXT PRIMARY KEY, text TEXT, meta TEXT, ts INTEGER);
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text, content='docs', content_rowid='rowid');
CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN INSERT INTO fts(rowid,text) VALUES (new.rowid, new.text); END;
CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN INSERT INTO fts(fts, rowid, text) VALUES('delete', old.rowid, old.text); END;
CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs BEGIN INSERT INTO fts(fts, rowid, text) VALUES('delete', old.rowid, old.text); INSERT INTO fts(rowid,text) VALUES (new.rowid, new.text); END;
CREATE TABLE IF NOT EXISTS vecs (id TEXT PRIMARY KEY, v TEXT);`);
  } catch (error) {
    fallbackMode = true;
    const dir = path.dirname(FALLBACK_FILE);
    fs.mkdirSync(dir, { recursive: true });
    console.warn(
      `[memory] SQLite unavailable (${error.message}); using fallback file ${FALLBACK_FILE}`
    );
  }

  async function embed(text) {
    if (fallbackMode) return [];
    // Call local Ollama embeddings endpoint (pull nomic-embed-text first)
    const r = await fetch('http://127.0.0.1:11434/api/embeddings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: process.env.EMBED_MODEL || 'nomic-embed-text', prompt: text })
    });
    const j = await r.json();
    return j.embedding || j.data?.[0]?.embedding || [];
  }

  let run;
  let all;
  let get;
  if (!fallbackMode) {
    run = function(sql, p = []) {
      return Promise.resolve(db.prepare(sql).run(p));
    };
    all = function(sql, p = []) {
      return Promise.resolve(db.prepare(sql).all(p));
    };
    get = function(sql, p = []) {
      return Promise.resolve(db.prepare(sql).get(p));
    };
  } else {
    const notAvailable = () =>
      Promise.reject(new Error('Database unavailable: fallback mode active'));
    run = notAvailable;
    all = notAvailable;
    get = notAvailable;
  }

  function cosine(a, b) {
    let dot = 0,
      na = 0,
      nb = 0;
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      dot += a[i] * b[i];
      na += a[i] * a[i];
      nb += b[i] * b[i];
    }
    return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-9);
  }

  app.post('/api/memory/index', async (req, res) => {
    let raw = '';
    req.on('data', d => (raw += d));
    await new Promise(r => req.on('end', r));
    const body = raw ? JSON.parse(raw) : {};
    const id = body.id || `doc:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
    const text = String(body.text || '').slice(0, 200000);
    const meta = { source: body.source || null, tags: body.tags || [] };
    if (!text) return res.status(400).json({ error: 'missing text' });

    if (fallbackMode) {
      const entry = {
        id,
        text,
        meta,
        ts: Date.now()
      };
      await fs.promises.appendFile(
        FALLBACK_FILE,
        `${JSON.stringify(entry)}\n`,
        'utf8'
      );
      return res.json({ ok: true, id, fallback: true });
    }

    await run(`INSERT OR REPLACE INTO docs(id,text,meta,ts) VALUES(?,?,?,?)`, [
      id,
      text,
      JSON.stringify(meta),
      Date.now()
    ]);
    // embed a few chunks ~1k chars
    const chunks = [];
    for (let i = 0; i < text.length; i += 1000) chunks.push(text.slice(i, i + 1000));
    const embs = [];
    for (const c of chunks) {
      embs.push(await embed(c));
    }
    await run(`INSERT OR REPLACE INTO vecs(id,v) VALUES(?,?)`, [
      id,
      JSON.stringify(embs.flat().slice(0, 1536))
    ]);
    res.json({ ok: true, id });
  });

  app.post('/api/memory/search', async (req, res) => {
    let raw = '';
    req.on('data', d => (raw += d));
    await new Promise(r => req.on('end', r));
    const body = raw ? JSON.parse(raw) : {};
    const q = String(body.q || '').trim();
    const k = Math.max(1, Math.min(20, body.top_k || 5));
    if (!q) return res.status(400).json({ error: 'empty query' });

    if (fallbackMode) {
      try {
        await fs.promises.access(FALLBACK_FILE, fs.constants.F_OK);
      } catch (accessError) {
        return res.json({ results: [], fallback: true });
      }

      const matches = [];
      const query = q.toLowerCase();
      let stream;
      let rl;
      try {
        stream = fs.createReadStream(FALLBACK_FILE, { encoding: 'utf8' });
        rl = readline.createInterface({ input: stream, crlfDelay: Infinity });
        for await (const line of rl) {
          if (!line.trim()) continue;
          try {
            const entry = JSON.parse(line);
            if ((entry.text || '').toLowerCase().includes(query)) {
              matches.push({
                id: entry.id,
                score: 1,
                text: (entry.text || '').slice(0, 2000),
                meta: entry.meta || {},
                ts: entry.ts
              });
            }
          } catch (err) {
            // ignore malformed lines
          }
        }
      } catch (error) {
        return res
          .status(500)
          .json({ error: 'fallback read failed', detail: error.message });
      } finally {
        if (rl) rl.close();
        if (stream && typeof stream.close === 'function') stream.close();
      }

      matches.sort((a, b) => (b.ts || 0) - (a.ts || 0));
      return res.json({ results: matches.slice(0, k), fallback: true });
    }

    // coarse FTS
    const rows = await all(
      `SELECT id, text, meta FROM docs WHERE rowid IN (SELECT rowid FROM fts WHERE fts MATCH ? LIMIT 50)`,
      [q.split(/\s+/).join(' ')]
    );
    // embeddings rerank
    const qv = await embed(q);
    const scored = [];
    for (const r of rows) {
      const vrow = await get(`SELECT v FROM vecs WHERE id=?`, [r.id]);
      const v = vrow ? JSON.parse(vrow.v) : [];
      scored.push({ id: r.id, score: cosine(qv, v), text: r.text.slice(0, 2000), meta: JSON.parse(r.meta || '{}') });
    }
    scored.sort((a, b) => b.score - a.score);
    res.json({ results: scored.slice(0, k) });
  });

  if (fallbackMode) {
    console.log('[memory] fallback mode active:', FALLBACK_FILE);
  } else {
    console.log('[memory] online:', DBP);
  }
};
