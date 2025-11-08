import fs from 'fs';
import path from 'path';

const PERF_TARGET = 0.9;
const LCP_TARGET_MS = 2000;
const TBT_TARGET_MS = 200;
const LATENCY_P95_TARGET_MS = 750;

function toNumber(value) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function parseDate(entry) {
  if (!entry || typeof entry !== 'object') return null;
  const candidates = ['ts', 'timestamp', 'time', 'date', 'updated_at', 'started_at', 'created_at'];
  for (const key of candidates) {
    if (entry[key]) {
      const date = new Date(entry[key]);
      if (!Number.isNaN(date.valueOf())) {
        return date;
      }
    }
  }
  return null;
}

function isoWeekKey(date) {
  if (!date) return null;
  const tmp = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  const dayNum = tmp.getUTCDay() || 7;
  tmp.setUTCDate(tmp.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil(((tmp - yearStart) / 86400000 + 1) / 7);
  return `${tmp.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`;
}

function average(values) {
  if (!values.length) return null;
  const total = values.reduce((sum, value) => sum + value, 0);
  return total / values.length;
}

function median(values) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1] + sorted[mid]) / 2;
  }
  return sorted[mid];
}

function computeWeekly(history, pick) {
  const buckets = new Map();
  for (const entry of history) {
    const date = parseDate(entry);
    const key = isoWeekKey(date);
    if (!key) continue;
    const value = toNumber(pick(entry));
    if (value == null) continue;
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(value);
  }
  const result = {};
  for (const [key, values] of buckets.entries()) {
    result[key] = average(values);
  }
  return result;
}

function countByWeek(history) {
  const counts = {};
  for (const entry of history) {
    const date = parseDate(entry);
    const key = isoWeekKey(date);
    if (!key) continue;
    counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
}

function latestEntries(history) {
  const sorted = history
    .map((entry) => ({ entry, date: parseDate(entry) }))
    .filter((item) => item.date)
    .sort((a, b) => b.date.valueOf() - a.date.valueOf());
  return {
    latest: sorted[0]?.entry ?? null,
    previous: sorted[1]?.entry ?? null,
  };
}

function computeLighthouse(lhRaw) {
  const history = Array.isArray(lhRaw?.history) ? lhRaw.history : Array.isArray(lhRaw) ? lhRaw : [];
  const perfScores = history.map((entry) => toNumber(entry.perf)).filter((value) => value != null);
  const a11yScores = history.map((entry) => toNumber(entry.a11y)).filter((value) => value != null);
  const lcps = history.map((entry) => toNumber(entry.LCP ?? entry.lcp)).filter((value) => value != null);
  const tbts = history.map((entry) => toNumber(entry.TBT ?? entry.tbt)).filter((value) => value != null);

  const weeklyPerf = computeWeekly(history, (entry) => entry.perf);
  const weeklyA11y = computeWeekly(history, (entry) => entry.a11y);
  const weeklyLcp = computeWeekly(history, (entry) => entry.LCP ?? entry.lcp);
  const weeklyTbt = computeWeekly(history, (entry) => entry.TBT ?? entry.tbt);

  const { latest, previous } = latestEntries(history);

  const latestLcp = latest ? toNumber(latest.LCP ?? latest.lcp) : null;
  const previousLcp = previous ? toNumber(previous.LCP ?? previous.lcp) : null;
  let lcpDeltaPercent = null;
  if (latestLcp != null && previousLcp != null && previousLcp !== 0) {
    lcpDeltaPercent = ((latestLcp - previousLcp) / previousLcp) * 100;
  }

  const weeklySummaries = Object.keys(weeklyPerf).map((week) => ({
    week,
    perf: weeklyPerf[week] ?? null,
    lcp: weeklyLcp[week] ?? null,
    tbt: weeklyTbt[week] ?? null,
  }));

  const sloWeeks = weeklySummaries.filter((week) =>
    week.perf != null && week.lcp != null && week.tbt != null
  );
  const sloPassing = sloWeeks.filter(
    (week) => week.perf >= PERF_TARGET && week.lcp <= LCP_TARGET_MS && week.tbt <= TBT_TARGET_MS
  );

  return {
    sampleCount: history.length,
    perfScore: average(perfScores),
    a11yScore: average(a11yScores),
    lcpCoverage:
      history.length && lcps.length
        ? lcps.filter((value) => value <= LCP_TARGET_MS).length / history.length
        : null,
    tbtMedian: median(tbts),
    weekly: {
      perf: weeklyPerf,
      a11y: weeklyA11y,
      lcp: weeklyLcp,
      tbt: weeklyTbt,
    },
    latest,
    previous,
    latestLcp,
    previousLcp,
    lcpDeltaPercent,
    weeklySummaries,
    slo: {
      totalWeeks: sloWeeks.length,
      passingWeeks: sloPassing.length,
      compliance:
        sloWeeks.length > 0 ? sloPassing.length / sloWeeks.length : null,
    },
  };
}

function computeCI(ciRaw) {
  const runs = Array.isArray(ciRaw?.runs) ? ciRaw.runs : Array.isArray(ciRaw) ? ciRaw : [];
  const sortedRuns = runs
    .map((run) => ({ run, date: parseDate(run) ?? parseDate({ updated_at: run.updated_at }) }))
    .filter((item) => item.date)
    .sort((a, b) => a.date.valueOf() - b.date.valueOf());

  const totalRuns = runs.length;
  const failedRuns = runs.filter((run) => run.conclusion && run.conclusion !== 'success');
  const failureRate = totalRuns ? failedRuns.length / totalRuns : null;

  const mttrDurations = [];
  let failureStart = null;
  for (const { run, date } of sortedRuns) {
    const conclusion = run.conclusion || run.status;
    if (conclusion && conclusion !== 'success') {
      if (!failureStart) {
        failureStart = date;
      }
      continue;
    }
    if (conclusion === 'success' && failureStart) {
      const resolvedAt = new Date(run.updated_at || run.completed_at || run.started_at || date);
      if (!Number.isNaN(resolvedAt.valueOf())) {
        mttrDurations.push((resolvedAt.valueOf() - failureStart.valueOf()) / 3_600_000);
      }
      failureStart = null;
    }
  }

  const weeklyDeploys = {};
  let lastDeployAt = null;
  for (const run of runs) {
    const name = `${run.name || ''} ${run.wf || ''}`.toLowerCase();
    const isDeploy = name.includes('deploy');
    if (!isDeploy) continue;
    if (run.conclusion !== 'success') continue;
    const deployDate = parseDate(run) || parseDate({ timestamp: run.updated_at });
    const week = isoWeekKey(deployDate);
    if (!week) continue;
    weeklyDeploys[week] = (weeklyDeploys[week] || 0) + 1;
    if (!lastDeployAt || deployDate > lastDeployAt) {
      lastDeployAt = deployDate;
    }
  }

  const weeklyRuns = countByWeek(runs);
  const deployWeeks = Object.keys(weeklyDeploys).sort();
  const currentDeployWeek = deployWeeks[deployWeeks.length - 1] || null;

  return {
    totalRuns,
    failureRate,
    mttrHours: average(mttrDurations),
    weeklyDeploys,
    lastDeployAt: lastDeployAt ? lastDeployAt.toISOString() : null,
    weeklyRuns,
    currentDeployWeek,
    currentDeployCount: currentDeployWeek ? weeklyDeploys[currentDeployWeek] : 0,
  };
}

function computeK6(k6Raw) {
  const metrics = k6Raw?.metrics && typeof k6Raw.metrics === 'object' ? k6Raw.metrics : {};
  const components = {};
  for (const [name, metric] of Object.entries(metrics)) {
    if (!name.startsWith('http_req_duration')) continue;
    if (!metric || typeof metric !== 'object') continue;
    const p95 = toNumber(metric['p(95)'] ?? metric.p95 ?? metric['95'] ?? metric['p95']);
    if (p95 == null) continue;
    let component = 'global';
    const match = name.match(/component:([^,}]+)/);
    if (match) {
      component = match[1];
    } else if (metric.tags && metric.tags.component) {
      component = metric.tags.component;
    }
    components[component] = { p95 };
  }

  return { components };
}

function computeAlerts(alertsRaw) {
  const alerts = Array.isArray(alertsRaw) ? alertsRaw : [];
  const weeklyCounts = {};
  for (const alert of alerts) {
    const date = parseDate(alert);
    const week = isoWeekKey(date);
    if (!week) continue;
    weeklyCounts[week] = (weeklyCounts[week] || 0) + 1;
  }
  const total = alerts.length;
  const sortedWeeks = Object.keys(weeklyCounts).sort();
  const latestWeek = sortedWeeks[sortedWeeks.length - 1];

  return {
    total,
    weeklyCounts,
    latestWeek,
    latestWeekCount: latestWeek ? weeklyCounts[latestWeek] : 0,
  };
}

function computeSim(simRaw) {
  const metrics = simRaw?.metrics && typeof simRaw.metrics === 'object' ? simRaw.metrics : {};
  const maes = [];
  for (const value of Object.values(metrics)) {
    if (value && typeof value === 'object') {
      const mae = toNumber(value.mae);
      if (mae != null) {
        maes.push(mae);
      }
    }
  }
  return {
    maeMean: average(maes),
    maeSamples: maes.length,
    latestRun: simRaw?.generated_at || simRaw?.run_id || null,
  };
}

function computeAgents(agentsRaw) {
  const entries = Array.isArray(agentsRaw) ? agentsRaw : [];
  let plannedRoles = null;
  let completedRoles = null;
  for (const entry of entries) {
    if (!entry || typeof entry !== 'object') continue;
    if (entry.path && entry.path.endsWith('tree.json') && entry.data) {
      const population = entry.data.population || {};
      plannedRoles = toNumber(population.target) ?? plannedRoles;
      const seed = toNumber(population.seed_count);
      const descendants = toNumber(population.descendants_per_seed);
      if (seed != null) {
        if (descendants != null) {
          completedRoles = seed * (1 + descendants);
        } else {
          completedRoles = seed;
        }
      }
    }
  }
  let coverage = null;
  if (plannedRoles && completedRoles != null) {
    coverage = Math.min(1, completedRoles / plannedRoles);
  }
  return { plannedRoles, completedRoles, coverage };
}

function computeSlo(lighthouse, k6) {
  const latencyOk = Object.values(k6.components || {}).every(
    (component) => component.p95 <= LATENCY_P95_TARGET_MS
  );
  return {
    thresholds: {
      perf: PERF_TARGET,
      lcp: LCP_TARGET_MS,
      tbt: TBT_TARGET_MS,
      latencyP95: LATENCY_P95_TARGET_MS,
    },
    lighthouseCompliance: lighthouse.slo,
    latencyOk,
    overallCompliance:
      lighthouse.slo.compliance != null && latencyOk ? Math.min(lighthouse.slo.compliance, 1) : lighthouse.slo.compliance,
  };
}

export function computeKPIs(index) {
  const lighthouse = computeLighthouse(index?.lh ?? {});
  const ci = computeCI(index?.ci ?? {});
  const k6 = computeK6(index?.k6 ?? {});
  const alerts = computeAlerts(index?.alerts ?? []);
  const sim = computeSim(index?.sim ?? {});
  const agents = computeAgents(index?.agents ?? []);
  const slo = computeSlo(lighthouse, k6);

  return {
    generatedAt: new Date().toISOString(),
    lighthouse,
    ci,
    k6,
    alerts,
    sim,
    agents,
    slo,
  };
}

function loadIndex(indexPath) {
  const resolved = path.resolve(indexPath);
  const raw = fs.readFileSync(resolved, 'utf-8');
  return JSON.parse(raw);
}

function writeReport(report, outputPath) {
  const data = JSON.stringify(report, null, 2);
  if (outputPath) {
    fs.writeFileSync(path.resolve(outputPath), data + '\n');
  } else {
    process.stdout.write(data);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [indexPath, outputPath] = process.argv.slice(2);
  if (!indexPath) {
    console.error('Usage: node compute.js <index.json> [out.json]');
    process.exit(1);
  }
  const index = loadIndex(indexPath);
  const report = computeKPIs(index);
  writeReport(report, outputPath);
}
