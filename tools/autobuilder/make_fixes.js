// tools/autobuilder/make_fixes.js
// Usage: node tools/autobuilder/make_fixes.js --index data/timemachine/index.json
import fs from "node:fs";
import path from "node:path";

const args = Object.fromEntries(process.argv.slice(2).map((x,i,arr)=>{
  if (x.startsWith("--")) return [x.replace(/^--/,""), arr[i+1] && !arr[i+1].startsWith("--") ? arr[i+1] : true];
  return [null,null];
}).filter(Boolean));

const INDEX = args.index || "data/timemachine/index.json";
function ensureDir(p){ fs.mkdirSync(path.dirname(p), {recursive:true}); }
function log(action, payload={}){
  const line = JSON.stringify({ts:new Date().toISOString(), action, ...payload});
  ensureDir("data/aiops/actions.jsonl");
  fs.appendFileSync("data/aiops/actions.jsonl", line+"\n");
}

function upsertFile(p, content, tag){
  const exists = fs.existsSync(p);
  fs.mkdirSync(path.dirname(p), {recursive:true});
  fs.writeFileSync(p, content, "utf8");
  log("write_file", {path:p, tag, existed:exists});
}

const index = JSON.parse(fs.readFileSync(INDEX, "utf8"));

//
// 1) HTML tweaks (index.html) — add fetchpriority + alt; add preload hint if missing.
//
const INDEX_HTML = "sites/blackroad/public/index.html";
if (fs.existsSync(INDEX_HTML)) {
  let html = fs.readFileSync(INDEX_HTML, "utf8");
  let changed = false;

  // add fetchpriority="high" to first <img ...> if not present
  html = html.replace(/<img([^>]*?)>/i, (m, attrs)=>{
    if (/fetchpriority=/i.test(attrs)) return m;
    changed = true;
    if (!/alt=/i.test(attrs)) attrs += ' alt=""';
    return `<img${attrs} fetchpriority="high">`;
  });

  // add a generic preload for first stylesheet/script if no preload present
  if (!/rel=["']preload["']/.test(html)) {
    const mCss = html.match(/href=["']([^"']+\.css)["']/i);
    const mJs  = html.match(/src=["']([^"']+\.js)["']/i);
    if (mCss) {
      const link = `<link rel="preload" as="style" href="${mCss[1]}">`;
      html = html.replace(/<head>/i, `<head>\n  ${link}`);
      changed = true;
    } else if (mJs) {
      const link = `<link rel="preload" as="script" href="${mJs[1]}">`;
      html = html.replace(/<head>/i, `<head>\n  ${link}`);
      changed = true;
    }
  }

  if (changed) {
    fs.writeFileSync(INDEX_HTML, html, "utf8");
    log("modify_html", {path: INDEX_HTML});
  }
}

//
// 2) Static hosting headers — write _headers for cache policy (safe)
//
const HEADERS = "sites/blackroad/public/_headers";
if (!fs.existsSync(HEADERS)) {
  const content = `/*
  Cache-Control: no-store

/assets/*
  Cache-Control: public, max-age=604800, immutable
`;
  upsertFile(HEADERS, content, "cache_headers");
}

//
// 3) robots.txt & sitemap.xml if missing
//
const ROBOTS = "sites/blackroad/public/robots.txt";
if (!fs.existsSync(ROBOTS)) {
  upsertFile(ROBOTS, `User-agent: *\nAllow: /\nSitemap: https://blackroad.io/sitemap.xml\n`, "robots");
}
const SITEMAP = "sites/blackroad/public/sitemap.xml";
if (!fs.existsSync(SITEMAP)) {
  upsertFile(SITEMAP, `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://blackroad.io/</loc></url>
  <url><loc>https://blackroad.io/portal</loc></url>
  <url><loc>https://blackroad.io/status</loc></url>
</urlset>`, "sitemap");
}

console.log("Autobuilder completed.");
