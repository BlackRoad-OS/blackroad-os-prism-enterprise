// tools/pulse/write.js
// Usage: node tools/pulse/write.js data/kpis/latest.json > pulses/SYS-PERF-YYYY-WW.md
import fs from "node:fs";
import path from "node:path";

function isoWeek(dt=new Date()){
  const d=new Date(Date.UTC(dt.getFullYear(), dt.getMonth(), dt.getDate()));
  const dayNum = d.getUTCDay()||7; d.setUTCDate(d.getUTCDate()+4-dayNum);
  const yearStart=new Date(Date.UTC(d.getUTCFullYear(),0,1));
  const week=Math.ceil((((d - yearStart) / 86400000) + 1)/7);
  return {year:d.getUTCFullYear(), week};
}
function readJSON(p){ try{return JSON.parse(fs.readFileSync(p,"utf8"));}catch{return null;} }
function pct(x){ return (x==null)? "—" : (Math.round(x*1000)/10).toFixed(1)+"%"; }
function num(x, unit=""){ return (x==null)? "—" : `${Math.round(x)}${unit}`; }
function ms(x){ return (x==null)? "—" : `${Math.round(x)} ms`; }
function okBadge(b){ return b==null ? "–" : (b? "🟢" : "🔴"); }
function ensureDir(p){ fs.mkdirSync(path.dirname(p), {recursive:true}); }

const latest = readJSON(process.argv[2] || "data/kpis/latest.json") || {};
const {year, week} = isoWeek();
const title = `SYS-PERF-${year}-W${String(week).padStart(2,"0")}`;

const web = latest.kpis?.web||{};
const ci = latest.kpis?.ci||{};
const k6 = latest.kpis?.k6||{};
const sim = latest.kpis?.sim||{};
const flags = latest.flags||{};

const md = `# 📈 Performance & Reliability Pulse — ${title}

## Summary
- Web: perf=${web.perf_mean_7d??"—"} a11y=${web.a11y_mean_7d??"—"} LCP p75=${ms(web.lcp_p75_ms)} TBT p75=${ms(web.tbt_p75_ms)}
- CI: failure rate=${pct(ci.failure_rate_7d)} MTTR=${ms(ci.mttr_ms_7d)} deploys/7d=${ci.deploys_per_7d??"—"}
- k6 p95: ${Object.entries(k6.components||{}).map(([k,v])=>`${k}:${ms(v.p95)}`).join("  ")}
- Sim(solid): MAE=${sim.solid?.mae_mean_7d??"—"} RMSE=${sim.solid?.rmse_mean_7d??"—"} pass=${pct(sim.solid?.pass_fraction_mean_7d)}

## Budgets / SLOs
- Web: ${okBadge(flags.web?.perf_ok)} perf≥${latest.budgets?.web?.perf}  ${okBadge(flags.web?.a11y_ok)} a11y≥${latest.budgets?.web?.a11y}  ${okBadge(flags.web?.lcp_ok)} LCP p75≤${latest.budgets?.web?.lcp_p75_ms}ms  ${okBadge(flags.web?.tbt_ok)} TBT p75≤${latest.budgets?.web?.tbt_p75_ms}ms  ${okBadge(flags.web?.cls_ok)} CLS p95≤${latest.budgets?.web?.cls_p95}
- CI: ${okBadge(flags.ci?.failure_rate_ok)} fail≤${pct(latest.budgets?.ci?.failure_rate)}  ${okBadge(flags.ci?.mttr_ok)} MTTR≤${ms(latest.budgets?.ci?.mttr_ms)}  ${okBadge(flags.ci?.deploys_ok)} deploys≥${latest.budgets?.ci?.deploys_min_7d}
- k6: ${okBadge(flags.k6?.frontend_ok)} frontend p95≤${ms(latest.budgets?.k6?.frontend_p95_ms)}  ${okBadge(flags.k6?.quantum_ok)} quantum p95≤${ms(latest.budgets?.k6?.quantum_p95_ms)}  ${okBadge(flags.k6?.materials_ok)} materials p95≤${ms(latest.budgets?.k6?.materials_p95_ms)}

## Details
### Web (7d)
- perf=${web.perf_mean_7d??"—"}, a11y=${web.a11y_mean_7d??"—"}, best-practices=${web.bp_mean_7d??"—"}, SEO=${web.seo_mean_7d??"—"}
- LCP<2s coverage=${pct(web.lcp_lt2000_coverage_7d)}  TBT median=${ms(web.tbt_median_7d)}  CLS p95=${web.cls_p95_7d??"—"}

### CI (7d)
- failures/total=${pct(ci.failure_rate_7d)}  MTTR=${ms(ci.mttr_ms_7d)}  deploys=${ci.deploys_per_7d??"—"}

### k6 (latest)
${Object.entries(k6.components||{}).map(([k,v])=>`- ${k}: p50=${ms(v.p50)} p90=${ms(v.p90)} p95=${ms(v.p95)}`).join("\n")}

### Simulation (7d)
- solid: MAE=${sim.solid?.mae_mean_7d??"—"}, RMSE=${sim.solid?.rmse_mean_7d??"—"}, pass=${pct(sim.solid?.pass_fraction_mean_7d)}
- fluid: MAE=${sim.fluid?.mae_mean_7d??"—"}, RMSE=${sim.fluid?.rmse_mean_7d??"—"}, pass=${pct(sim.fluid?.pass_fraction_mean_7d)}

`;

const outPath = `pulses/${title}.md`;
ensureDir(outPath);
fs.writeFileSync(outPath, md, "utf8");
process.stdout.write(md);
