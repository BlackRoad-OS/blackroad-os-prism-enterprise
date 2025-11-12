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
  const FALLBACK_FILE = process.env.MEMORY_FALLBACK_FILE || '/home/agents/cecilia/logs/memory.txt';

  let db = null;
  let fallbackMode = false;

  if (Database) {
    try {
      fs.mkdirSync(path.dirname(DBP), { recursive: true });
      db = new Database(DBP);
      db.exec(`CREATE TABLE IF NOT EXISTS docs (id TEXT PRIMARY KEY, text TEXT, meta TEXT, ts INTEGER);
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text, content='docs', content_rowid='rowid');
CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN INSERT INTO fts(rowid,text) VALUES (new.rowid, new.text); END;
CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN INSERT INTO fts(fts, rowid, text) VALUES('delete', old.rowid, old.text); END;
CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs BEGIN INSERT INTO fts(fts, rowid, text) VALUES('delete', old.rowid, old.text); INSERT INTO fts(rowid,text) VALUES (new.rowid, new.text); END;
CREATE TABLE IF NOT EXISTS vecs (id TEXT PRIMARY KEY, v TEXT);`);
    } catch (error) {
      fallbackMode = true;
      console.warn(`[memory] SQLite unavailable; using fallback file ${FALLBACK_FILE}`);
      console.warn(error);
    }
  } else {
    fallbackMode = true;
    const msg = databaseLoadError ? databaseLoadError.message : 'module load failed';
    console.warn(`[memory] better-sqlite3 unavailable (${msg}); using fallback file ${FALLBACK_FILE}`);
  }

  if (fallbackMode) {
    try {
      fs.mkdirSync(path.dirname(FALLBACK_FILE), { recursive: true });
      if (!fs.existsSync(FALLBACK_FILE)) fs.writeFileSync(FALLBACK_FILE, '', 'utf8');
    } catch (error) {
      console.error('[memory] unable to initialize fallback file', error);
    }
  }

  async function embed(text){
    // Call local Ollama embeddings endpoint (pull nomic-embed-text first)
    const r = await fetch('http://127.0.0.1:11434/api/embeddings', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ model: process.env.EMBED_MODEL || 'nomic-embed-text', prompt: text })
    });
    const j = await r.json();
    return j.embedding || j.data?.[0]?.embedding || [];
  }

  let run = async () => { throw new Error('SQLite unavailable'); };
  let all = async () => { throw new Error('SQLite unavailable'); };
  let get = async () => { throw new Error('SQLite unavailable'); };

  if (db) {
    run = (sql, p = []) => Promise.resolve(db.prepare(sql).run(p));
    all = (sql, p = []) => Promise.resolve(db.prepare(sql).all(p));
    get = (sql, p = []) => Promise.resolve(db.prepare(sql).get(p));
  }

  function cosine(a,b){ let dot=0,na=0,nb=0; for(let i=0;i<Math.min(a.length,b.length);i++){dot+=a[i]*b[i];na+=a[i]*a[i];nb+=b[i]*b[i];} return dot/(Math.sqrt(na)*Math.sqrt(nb)+1e-9); }

  app.post('/api/memory/index', async (req,res)=>{
    let raw=''; req.on('data',d=>raw+=d); await new Promise(r=>req.on('end',r));
    const body = raw?JSON.parse(raw):{};
    const id = body.id || `doc:${Date.now()}:${Math.random().toString(36).slice(2,8)}`;
    const text = String(body.text||'').slice(0, 200000);
    const metaObj = {source:body.source||null,tags:body.tags||[]};
    if (!text) return res.status(400).json({error:'missing text'});

    if (fallbackMode || !db) {
      const entry = { id, text, meta: metaObj, ts: Date.now() };
      try {
        fs.appendFileSync(FALLBACK_FILE, `${JSON.stringify(entry)}\n`, 'utf8');
      } catch (error) {
        console.error('[memory] fallback write failed', error);
        return res.status(500).json({ error: 'fallback write failed', details: String(error.message||error) });
      }
      return res.json({ok:true,id,fallback:true});
    }

    const meta = JSON.stringify(metaObj);
    await run(`INSERT OR REPLACE INTO docs(id,text,meta,ts) VALUES(?,?,?,?)`, [id,text,meta,Date.now()]);
    // embed a few chunks ~1k chars
    const chunks=[]; for(let i=0;i<text.length;i+=1000) chunks.push(text.slice(i,i+1000));
    const embs=[]; for(const c of chunks){ embs.push(await embed(c)); }
    await run(`INSERT OR REPLACE INTO vecs(id,v) VALUES(?,?)`, [id, JSON.stringify(embs.flat().slice(0,1536))]);
    res.json({ok:true,id});
  });

  app.post('/api/memory/search', async (req,res)=>{
    let raw=''; req.on('data',d=>raw+=d); await new Promise(r=>req.on('end',r));
    const body = raw?JSON.parse(raw):{};
    const q = String(body.q||'').trim(); const k = Math.max(1, Math.min(20, body.top_k||5));
    if (!q) return res.status(400).json({error:'empty query'});
    if (fallbackMode || !db) {
      const query = q.toLowerCase();
      const matches = [];
      const windowSize = Math.max(k, 50);
      let fileMissing = false;

      try {
        await new Promise((resolve, reject) => {
          const stream = fs.createReadStream(FALLBACK_FILE, { encoding: 'utf8' });
          let rl;
          stream.on('error', (error) => {
            if (rl) rl.close();
            stream.destroy();
            if (error.code === 'ENOENT') {
              fileMissing = true;
              resolve();
              return;
            }
            reject(error);
          });

          rl = readline.createInterface({ input: stream, crlfDelay: Infinity });
          rl.on('line', (line) => {
            if (!line.trim()) return;
            try {
              const entry = JSON.parse(line);
              if (!entry?.text) return;
              if (entry.text.toLowerCase().includes(query)) {
                matches.push({
                  id: entry.id,
                  score: 1,
                  text: String(entry.text || '').slice(0, 2000),
                  meta: entry.meta || {},
                  ts: entry.ts || 0,
                });
                matches.sort((a, b) => (b.ts || 0) - (a.ts || 0));
                if (matches.length > windowSize) {
                  matches.length = windowSize;
                }
              }
            } catch (error) {
              console.warn('[memory] failed to parse fallback entry', error);
            }
          });

          rl.on('close', resolve);
        });
      } catch (error) {
        console.error('[memory] fallback read failed', error);
        return res.status(500).json({ error: 'fallback read failed', details: String(error.message||error) });
      }

      if (fileMissing) {
        return res.json({ results: [], fallback: true });
      }

      return res.json({ results: matches.slice(0, k), fallback: true });
    }

    // coarse FTS
    const rows = await all(`SELECT id, text, meta FROM docs WHERE rowid IN (SELECT rowid FROM fts WHERE fts MATCH ? LIMIT 50)`, [q.split(/\s+/).join(' ')]);
    // embeddings rerank
    const qv = await (async()=>await embed(q))();
    const scored = [];
    for (const r of rows){
      const vrow = await get(`SELECT v FROM vecs WHERE id=?`, [r.id]);
      const v = vrow ? JSON.parse(vrow.v) : [];
      scored.push({ id:r.id, score: cosine(qv, v), text:r.text.slice(0,2000), meta: JSON.parse(r.meta||'{}') });
    }
    scored.sort((a,b)=>b.score-a.score);
    res.json({ results: scored.slice(0,k) });
  });

  if (fallbackMode || !db) {
    console.log('[memory] fallback mode active:', FALLBACK_FILE);
  } else {
    console.log('[memory] online:', DBP);
  }
};
