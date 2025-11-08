import fs from 'fs';
import path from 'path';

import { computeKPIs } from '../kpis/compute.js';

export const DEFAULT_THRESHOLDS = {
  perfTarget: Number.parseFloat(process.env.LH_PERF_TARGET || '0.9'),
  lcpDeltaPercentMax: Number.parseFloat(process.env.LCP_DELTA_MAX || '5'),
  latencyP95: Number.parseFloat(process.env.K6_P95_TARGET || '750'),
};

export function evaluateBudgets(report, thresholds = DEFAULT_THRESHOLDS) {
  const issues = [];
  if (report?.lighthouse?.perfScore != null && report.lighthouse.perfScore < thresholds.perfTarget) {
    issues.push(`Lighthouse performance score ${report.lighthouse.perfScore.toFixed(3)} below target ${thresholds.perfTarget}`);
  }

  const lcpDelta = report?.lighthouse?.lcpDeltaPercent;
  if (lcpDelta != null && lcpDelta > thresholds.lcpDeltaPercentMax) {
    issues.push(`LCP regression ${lcpDelta.toFixed(2)}% exceeds allowed ${thresholds.lcpDeltaPercentMax}%`);
  }

  const components = report?.k6?.components || {};
  for (const [name, metrics] of Object.entries(components)) {
    if (metrics?.p95 != null && metrics.p95 > thresholds.latencyP95) {
      issues.push(`k6 p95 latency for ${name} = ${metrics.p95}ms exceeds ${thresholds.latencyP95}ms`);
    }
  }

  if (report?.slo?.lighthouseCompliance?.compliance != null) {
    const compliance = report.slo.lighthouseCompliance.compliance;
    if (compliance < 0.9) {
      issues.push(`Weekly SLO compliance ${formatPercent(compliance)} below 90% threshold`);
    }
  }

  return issues;
}

function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}

function loadIndex(indexPath) {
  const resolved = path.resolve(indexPath);
  const raw = fs.readFileSync(resolved, 'utf-8');
  return JSON.parse(raw);
}

function loadReportFromKpis(kpiPath) {
  const resolved = path.resolve(kpiPath);
  const raw = fs.readFileSync(resolved, 'utf-8');
  return JSON.parse(raw);
}

function parseArgs(argv) {
  const options = { indexPath: null, kpiPath: null };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--index') {
      options.indexPath = argv[i + 1];
      i += 1;
    } else if (arg === '--kpis') {
      options.kpiPath = argv[i + 1];
      i += 1;
    }
  }
  return options;
}

function main(argv) {
  const options = parseArgs(argv);
  if (!options.indexPath && !options.kpiPath) {
    console.error('Usage: node check_budgets.js [--index path] [--kpis path]');
    process.exit(1);
  }

  let report;
  if (options.kpiPath) {
    report = loadReportFromKpis(options.kpiPath);
  } else {
    const index = loadIndex(options.indexPath);
    report = computeKPIs(index);
  }

  const issues = evaluateBudgets(report);
  if (issues.length) {
    for (const issue of issues) {
      console.error(issue);
    }
    process.exit(1);
  } else {
    console.log('All budgets are within thresholds.');
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main(process.argv.slice(2));
}
