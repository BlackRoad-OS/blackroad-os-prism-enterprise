import fs from 'fs';
import path from 'path';

const DEFAULT_TEMPLATE = 'docs/pulses/template-06-performance-reliability-pulse.md';

function loadJson(filePath) {
  const raw = fs.readFileSync(path.resolve(filePath), 'utf-8');
  return JSON.parse(raw);
}

function loadTemplate(templatePath) {
  return fs.readFileSync(path.resolve(templatePath), 'utf-8');
}

function formatPercent(value, digits = 1) {
  if (value == null || Number.isNaN(value)) return 'n/a';
  return `${(value * 100).toFixed(digits)}%`;
}

function formatMs(value) {
  if (value == null || Number.isNaN(value)) return 'n/a';
  return `${Math.round(value)} ms`;
}

function formatHours(value) {
  if (value == null || Number.isNaN(value)) return 'n/a';
  if (value < 1) {
    return `${(value * 60).toFixed(1)} min`;
  }
  return `${value.toFixed(1)} h`;
}

function pickFrontendLatency(k6) {
  const components = k6?.components || {};
  if (components.frontend) return components.frontend.p95;
  if (components.global) return components.global.p95;
  const first = Object.values(components)[0];
  return first ? first.p95 : null;
}

function buildPerfTable(lighthouse) {
  const weeks = Object.keys(lighthouse.weekly.perf || {}).sort();
  if (!weeks.length) return '_No weekly Lighthouse history found._';
  const rows = weeks.slice(-6).map((week) => `| ${week} | ${formatPercent(lighthouse.weekly.perf[week], 1)} | ${formatPercent(lighthouse.weekly.a11y[week], 1)} |`);
  return ['| Week | Perf | A11y |', '| --- | --- | --- |', ...rows].join('\n');
}

function buildLcpTable(lighthouse) {
  const weeks = Object.keys(lighthouse.weekly.lcp || {}).sort();
  if (!weeks.length) return '_No LCP/TBT samples available._';
  const rows = weeks
    .slice(-6)
    .map((week) => `| ${week} | ${formatMs(lighthouse.weekly.lcp[week])} | ${formatMs(lighthouse.weekly.tbt[week])} |`);
  return ['| Week | LCP | TBT |', '| --- | --- | --- |', ...rows].join('\n');
}

function buildAlertTrend(alerts) {
  const entries = Object.entries(alerts.weeklyCounts || {}).sort(([a], [b]) => (a < b ? -1 : 1));
  if (!entries.length) return 'No alerts recorded.';
  return entries.slice(-6).map(([week, count]) => `${week}: ${count}`).join(', ');
}

function deriveIsoWeek(lighthouse, fallback = null) {
  const weeks = Object.keys(lighthouse.weekly.perf || {}).sort();
  return weeks[weeks.length - 1] || fallback;
}

function renderContext(report) {
  const latency = pickFrontendLatency(report.k6);
  const isoWeek = deriveIsoWeek(report.lighthouse, report.ci.currentDeployWeek);
  const latestLighthouseTs = report.lighthouse.latest?.ts || report.lighthouse.latest?.timestamp || null;
  const latestDeploy = report.ci.lastDeployAt ? new Date(report.ci.lastDeployAt).toISOString() : 'n/a';

  return {
    generatedAt: report.generatedAt,
    isoWeek: isoWeek || 'n/a',
    perfScore: formatPercent(report.lighthouse.perfScore, 1),
    a11yScore: formatPercent(report.lighthouse.a11yScore, 1),
    lcpCoverage: formatPercent(report.lighthouse.lcpCoverage, 1),
    tbtMedian: formatMs(report.lighthouse.tbtMedian),
    ciFailureRate: formatPercent(report.ci.failureRate, 1),
    mttr: formatHours(report.ci.mttrHours),
    deployFrequency:
      report.ci.currentDeployWeek
        ? `${report.ci.currentDeployCount} deploy(s) in ${report.ci.currentDeployWeek}`
        : 'n/a',
    p95Latency: formatMs(latency),
    sloCompliance: formatPercent(report.slo?.lighthouseCompliance?.compliance ?? null, 1),
    alertVolume:
      report.alerts.latestWeek
        ? `${report.alerts.latestWeekCount} in ${report.alerts.latestWeek}`
        : `${report.alerts.total}`,
    simMae: report.sim.maeMean != null ? report.sim.maeMean.toFixed(3) : 'n/a',
    agentCoverage: formatPercent(report.agents.coverage, 1),
    weeklyPerfTable: buildPerfTable(report.lighthouse),
    weeklyLcpTable: buildLcpTable(report.lighthouse),
    ciRunCount: String(report.ci.totalRuns ?? 0),
    alertTrend: buildAlertTrend(report.alerts),
    latestLighthouse: latestLighthouseTs ? new Date(latestLighthouseTs).toISOString() : 'n/a',
    latestDeploy,
  };
}

function renderTemplate(template, context) {
  return template.replace(/{{\s*(\w+)\s*}}/g, (match, key) => {
    if (Object.prototype.hasOwnProperty.call(context, key)) {
      return context[key];
    }
    return match;
  });
}

function main(argv) {
  if (!argv.length) {
    console.error('Usage: node write.js <kpi.json> [--template path]');
    process.exit(1);
  }

  let templatePath = DEFAULT_TEMPLATE;
  let kpiPath = null;
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--template') {
      templatePath = argv[i + 1];
      i += 1;
      continue;
    }
    if (!kpiPath) {
      kpiPath = arg;
    }
  }

  if (!kpiPath) {
    console.error('Missing KPI JSON path.');
    process.exit(1);
  }

  const report = loadJson(kpiPath);
  const template = loadTemplate(templatePath || DEFAULT_TEMPLATE);
  const context = renderContext(report);
  const output = renderTemplate(template, context);
  process.stdout.write(output);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main(process.argv.slice(2));
}
