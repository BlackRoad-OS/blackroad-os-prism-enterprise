import fs from 'fs';
import path from 'path';

import { computeKPIs } from '../kpis/compute.js';
import { evaluateBudgets } from '../policies/check_budgets.js';

const DEFAULT_INDEX = 'data/timemachine/index.json';
const SAFE_RELATIVE_PATHS = [
  'sites/blackroad/public',
  'docs',
  'pulses',
  'data',
  'frontend/public',
];

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function createGuard(projectRoot) {
  const safeRoots = SAFE_RELATIVE_PATHS.map((relative) => path.resolve(projectRoot, relative));
  return function assertSafe(targetPath) {
    const resolved = path.resolve(targetPath);
    for (const safeRoot of safeRoots) {
      if (resolved.startsWith(safeRoot)) {
        return;
      }
    }
    throw new Error(`Path ${resolved} is outside the SAFE_PATHS whitelist.`);
  };
}

function ensureDirectory(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function ensurePreload(projectRoot, assertSafe) {
  const htmlPath = path.resolve(projectRoot, 'sites/blackroad/public/index.html');
  if (!fs.existsSync(htmlPath)) return false;
  assertSafe(htmlPath);
  const original = fs.readFileSync(htmlPath, 'utf-8');

  const imgMatch = original.match(/<img\b[^>]*src="([^"]+)"[^>]*>/i);
  if (!imgMatch) return false;
  const [imgTag, src] = imgMatch;
  let updated = original;

  if (!/fetchpriority=/i.test(imgTag)) {
    const replacement = imgTag.replace('<img', '<img fetchpriority="high"');
    updated = updated.replace(imgTag, replacement);
  }

  const preloadTag = `<link rel="preload" as="image" href="${src}" fetchpriority="high">`;
  const preloadRegex = new RegExp(`<link[^>]*rel="preload"[^>]*href="${escapeRegExp(src)}"`, 'i');
  if (!preloadRegex.test(updated)) {
    updated = updated.replace('</head>', `  ${preloadTag}\n</head>`);
  }

  if (updated !== original) {
    fs.writeFileSync(htmlPath, updated, 'utf-8');
    return true;
  }
  return false;
}

function ensureCacheHeaders(projectRoot, assertSafe) {
  const headersPath = path.resolve(projectRoot, 'sites/blackroad/public/_headers');
  assertSafe(headersPath);
  const desiredBlocks = [
    '/*\n  Cache-Control: public, max-age=600\n',
    '/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n',
  ];

  let content = '';
  if (fs.existsSync(headersPath)) {
    content = fs.readFileSync(headersPath, 'utf-8');
  }

  let changed = false;
  for (const block of desiredBlocks) {
    if (!content.includes(block)) {
      content = `${content.trim()}\n${block}`.trim() + '\n';
      changed = true;
    }
  }

  if (changed || !fs.existsSync(headersPath)) {
    ensureDirectory(headersPath);
    fs.writeFileSync(headersPath, `${content.trim()}\n`, 'utf-8');
    return true;
  }
  return false;
}

function listHtmlFiles(baseDir) {
  if (!fs.existsSync(baseDir)) return [];
  const files = [];
  const stack = [baseDir];
  while (stack.length) {
    const current = stack.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(entryPath);
      } else if (entry.name.endsWith('.html')) {
        files.push(entryPath);
      }
    }
  }
  return files;
}

function ensureAltAttributes(projectRoot, assertSafe) {
  const publicDir = path.resolve(projectRoot, 'sites/blackroad/public');
  if (!fs.existsSync(publicDir)) return false;
  const files = listHtmlFiles(publicDir);
  let changed = false;
  for (const filePath of files) {
    assertSafe(filePath);
    const original = fs.readFileSync(filePath, 'utf-8');
    const updated = original.replace(/<img\b([^>]*?)>/gi, (match) => {
      if (/alt\s*=/.test(match)) {
        return match;
      }
      const selfClosing = match.endsWith('/>');
      const suffix = selfClosing ? '/>' : '>';
      const trimmed = match.slice(0, match.length - suffix.length);
      return `${trimmed} alt=""${suffix}`;
    });
    if (updated !== original) {
      fs.writeFileSync(filePath, updated, 'utf-8');
      changed = true;
    }
  }
  return changed;
}

function refreshSitemap(projectRoot, assertSafe) {
  const sitemapPath = path.resolve(projectRoot, 'sites/blackroad/public/sitemap.xml');
  const robotsPath = path.resolve(projectRoot, 'sites/blackroad/public/robots.txt');
  const today = new Date().toISOString().split('T')[0];
  let changed = false;

  if (fs.existsSync(sitemapPath)) {
    assertSafe(sitemapPath);
    const original = fs.readFileSync(sitemapPath, 'utf-8');
    let updated = original;
    if (/<lastmod>[^<]*<\/lastmod>/i.test(original)) {
      updated = original.replace(/<lastmod>[^<]*<\/lastmod>/i, `<lastmod>${today}</lastmod>`);
    } else {
      updated = original.replace('</url>', `  <lastmod>${today}</lastmod>\n</url>`);
    }
    if (updated !== original) {
      fs.writeFileSync(sitemapPath, updated, 'utf-8');
      changed = true;
    }
  }

  const robotsLine = 'Sitemap: /sitemap.xml';
  assertSafe(robotsPath);
  let robotsContent = '';
  if (fs.existsSync(robotsPath)) {
    robotsContent = fs.readFileSync(robotsPath, 'utf-8');
  }
  if (!robotsContent.includes(robotsLine)) {
    robotsContent = `${robotsContent.trim()}\n${robotsLine}`.trim() + '\n';
    ensureDirectory(robotsPath);
    fs.writeFileSync(robotsPath, robotsContent, 'utf-8');
    changed = true;
  }

  return changed;
}

function runBudgetCheck(indexPath) {
  if (!indexPath || !fs.existsSync(indexPath)) {
    return [];
  }
  const index = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
  const report = computeKPIs(index);
  return evaluateBudgets(report);
}

function parseArgs(argv) {
  const options = {
    indexPath: DEFAULT_INDEX,
    projectRoot: process.cwd(),
    skipBudgets: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--index') {
      options.indexPath = argv[i + 1];
      i += 1;
    } else if (arg === '--root') {
      options.projectRoot = argv[i + 1];
      i += 1;
    } else if (arg === '--no-budget-check') {
      options.skipBudgets = true;
    }
  }
  return options;
}

function main(argv) {
  const options = parseArgs(argv);
  const assertSafe = createGuard(options.projectRoot);

  const actions = [];
  if (ensurePreload(options.projectRoot, assertSafe)) actions.push('preload');
  if (ensureCacheHeaders(options.projectRoot, assertSafe)) actions.push('cache-headers');
  if (ensureAltAttributes(options.projectRoot, assertSafe)) actions.push('alt-text');
  if (refreshSitemap(options.projectRoot, assertSafe)) actions.push('sitemap');

  if (!actions.length) {
    console.log('Autobuilder: no changes applied.');
  } else {
    console.log(`Autobuilder: applied fixes -> ${actions.join(', ')}`);
  }

  let exitCode = 0;
  if (!options.skipBudgets) {
    const issues = runBudgetCheck(options.indexPath ? path.resolve(options.indexPath) : null);
    if (issues.length) {
      exitCode = 1;
      for (const issue of issues) {
        console.error(`Budget violation: ${issue}`);
      }
    }
  }

  process.exit(exitCode);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main(process.argv.slice(2));
}
