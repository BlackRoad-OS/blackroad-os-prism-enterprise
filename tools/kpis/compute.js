// tools/kpis/compute.js
// Usage: node tools/kpis/compute.js data/timemachine/index.json > data/kpis/latest.json
import fs from "node:fs";
import path from "node:path";

function readJSON(p) {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return null; }
}
function ensureDir(p){ fs.mkdirSync(path.dirname(p), {recursive:true}); }

function quantile(values, q){
  const a=values.filter(v=>typeof v==="number" && !isNaN(v)).sort((x,y)=>x-y);
  if(!a.length) return null;
  const pos=(a.length-1)*q, base=Math.floor(pos), rest=pos-base;
  return a[base] + (a[base+1]!==undefined ? rest*(a[base+1]-a[base]) : 0);
}
function median(vs){ return quantile(vs,0.5); }
function avg(vs){
  const a=vs.filter(v=>typeof v==="number" && !isNaN(v));
  return a.length? a.reduce((s,v)=>s+v,0)/a.length : null;
}

function withinDays(tsIso, days){
  if(!tsIso) return false;
  const t = new Date(tsIso).getTime();
  if (isNaN(t)) return false;
  const now = Date.now();
  return (now - t) <= days*24*3600*1000;
}

function computeKPIs(index){
  const out = { generated_at: new Date().toISOString(), kpis: {}, flags: {}, notes: [] };

  // LH (7d window)
  const lh = (index.lh?.history)||[];
  const lh7 = lh.filter(r => withinDays(r.ts, 7));
  const get = (rows, k)=> rows.map(x=>x?.[k]).filter(n=>typeof n==="number");

  const perf7 = avg(get(lh7,"perf"));
  const a11y7 = avg(get(lh7,"a11y"));
  const bp7 = avg(get(lh7,"bp"));
  const seo7 = avg(get(lh7,"seo"));
  const lcp7 = get(lh7,"LCP");
  const tbt7 = get(lh7,"TBT");
  const cls7 = get(lh7,"CLS");

  const lcpCoverage7 = lcp7.length ? (lcp7.filter(v=>v<2000).length / lcp7.length) : null;
  const tbtMedian7 = median(tbt7);
  const lcpP75 = quantile(lcp7, 0.75);
  const tbtP75 = quantile(tbt7, 0.75);
  const clsP95_7 = quantile(cls7, 0.95);

  out.kpis.web = {
    perf_mean_7d: perf7,
    a11y_mean_7d: a11y7,
    bp_mean_7d: bp7,
    seo_mean_7d: seo7,
    lcp_p75_ms: lcpP75,
    tbt_p75_ms: tbtP75,
    lcp_lt2000_coverage_7d: lcpCoverage7,
    tbt_median_7d: tbtMedian7,
    cls_p95_7d: clsP95_7
  };

  // CI (7d)
  const runs = (index.ci?.runs)||[];
  const r7 = runs.filter(r => withinDays(r.ts, 7));
  const total = r7.length;
  const failed = r7.filter(r => (r.conclusion||"").toLowerCase().includes("fail")).length;
  const failureRate = total? failed/total : null;

  // naive MTTR: for each failed run, time to next success in same workflow
  let mttrMs = null;
  if (r7.length){
    const byWf = {};
    for (const r of r7){
      const k = r.name||"";
      (byWf[k] ||= []).push(r);
    }
    const diffs=[];
    for (const [_, arr] of Object.entries(byWf)){
      arr.sort((a,b)=> new Date(a.ts)-new Date(b.ts));
      for (let i=0;i<arr.length;i++){
        if ((arr[i].conclusion||"").toLowerCase().includes("fail")){
          const next = arr.slice(i+1).find(x=> (x.conclusion||"").toLowerCase().includes("success"));
          if (next){
            diffs.push(new Date(next.ts)-new Date(arr[i].ts));
          }
        }
      }
    }
    if (diffs.length) mttrMs = avg(diffs);
  }

  // Deploy frequency (successful runs with 'deploy' in name)
  const deploys = r7.filter(r => /deploy/i.test(r.name||"") && /(success|completed)/i.test(r.conclusion||"")).length;

  out.kpis.ci = {
    failure_rate_7d: failureRate,
    mttr_ms_7d: mttrMs,
    deploys_per_7d: deploys
  };

  // k6 latest summary + components
  const k6sum = index.k6?.summary || {};
  const comps = index.k6?.components || [];
  const k6 = {
    http_reqs_rate: k6sum.http_reqs_rate ?? null,
    duration_p95: k6sum.duration_p95 ?? null,
    components: {}
  };
  for (const c of comps){
    if (!c?.component) continue;
    k6.components[c.component] = { p50: c.p50 ?? null, p90: c.p90 ?? null, p95: c.p95 ?? null };
  }
  out.kpis.k6 = k6;

  // Simulation (7d)
  const simRuns = (index.sim?.runs)||[];
  const sim7 = simRuns.filter(r => withinDays(r.generated_at, 7));
  const solidMae = avg(sim7.map(r => r?.solid?.mae));
  const solidRmse = avg(sim7.map(r => r?.solid?.rmse));
  const solidPass = avg(sim7.map(r => r?.solid?.pass_fraction));
  const fluidMae = avg(sim7.map(r => r?.fluid?.mae));
  const fluidRmse = avg(sim7.map(r => r?.fluid?.rmse));
  const fluidPass = avg(sim7.map(r => r?.fluid?.pass_fraction));
  out.kpis.sim = {
    solid: { mae_mean_7d: solidMae, rmse_mean_7d: solidRmse, pass_fraction_mean_7d: solidPass },
    fluid: { mae_mean_7d: fluidMae, rmse_mean_7d: fluidRmse, pass_fraction_mean_7d: fluidPass }
  };

  // Alerts (7d)
  const alerts = (index.alerts?.alerts)||[];
  const alerts7 = alerts.filter(a => withinDays(a.ts || a.time || a.timestamp, 7));
  out.kpis.alerts = { volume_7d: alerts7.length };

  // Agent coverage (best-effort)
  const agentItems = (index.agents?.items)||[];
  out.kpis.agents = {
    tracked_files: agentItems.length
  };

  // Budgets / SLO flags (v1)
  const budgets = {
    web: { perf: 0.93, a11y: 0.98, lcp_p75_ms: 2000, tbt_p75_ms: 150, cls_p95: 0.1 },
    k6: { frontend_p95_ms: 250, quantum_p95_ms: 1200, materials_p95_ms: 1400 },
    ci: { failure_rate: 0.02, mttr_ms: 2*60*60*1000, deploys_min_7d: 3 }
  };

  // Evaluate flags
  function ok(b){ return b===null || b===undefined ? null : Boolean(b); }

  out.flags = {
    web: {
      perf_ok: ok(perf7!==null && perf7>=budgets.web.perf),
      a11y_ok: ok(a11y7!==null && a11y7>=budgets.web.a11y),
      lcp_ok: ok(lcpP75!==null && lcpP75<=budgets.web.lcp_p75_ms),
      tbt_ok: ok(tbtP75!==null && tbtP75<=budgets.web.tbt_p75_ms),
      cls_ok: ok(clsP95_7!==null && clsP95_7<=budgets.web.cls_p95)
    },
    ci: {
      failure_rate_ok: ok(failureRate!==null && failureRate<=budgets.ci.failure_rate),
      mttr_ok: ok(mttrMs!==null && mttrMs<=budgets.ci.mttr_ms),
      deploys_ok: ok(deploys!==null && deploys>=budgets.ci.deploys_min_7d)
    },
    k6: {
      frontend_ok: ok((k6.components?.frontend?.p95 ?? null) !== null && k6.components.frontend.p95 <= budgets.k6.frontend_p95_ms),
      quantum_ok: ok((k6.components?.["quantum-lab"]?.p95 ?? null) !== null && k6.components["quantum-lab"].p95 <= budgets.k6.quantum_p95_ms),
      materials_ok: ok((k6.components?.["materials-service"]?.p95 ?? null) !== null && k6.components["materials-service"].p95 <= budgets.k6.materials_p95_ms)
    }
  };

  out.budgets = budgets;
  return out;
}

const input = process.argv[2] || "data/timemachine/index.json";
const index = readJSON(input) || {};
const out = computeKPIs(index);
ensureDir("data/kpis/latest.json");
fs.writeFileSync("data/kpis/latest.json", JSON.stringify(out, null, 2));
process.stdout.write(JSON.stringify(out, null, 2));
