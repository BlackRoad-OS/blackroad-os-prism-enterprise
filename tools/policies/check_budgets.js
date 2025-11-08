// tools/policies/check_budgets.js
// Usage: node tools/policies/check_budgets.js data/kpis/latest.json
import fs from "node:fs";

const file = process.argv[2] || "data/kpis/latest.json";
const latest = JSON.parse(fs.readFileSync(file, "utf8"));

function fail(msg){ console.error("❌", msg); process.exitCode = 1; }
function ok(msg){ console.log("✅", msg); }

const f = latest.flags || {};
const checks = [
  ["web.perf_ok", f.web?.perf_ok],
  ["web.a11y_ok", f.web?.a11y_ok],
  ["web.lcp_ok", f.web?.lcp_ok],
  ["web.tbt_ok", f.web?.tbt_ok],
  ["web.cls_ok", f.web?.cls_ok],
  ["ci.failure_rate_ok", f.ci?.failure_rate_ok],
  ["ci.mttr_ok", f.ci?.mttr_ok],
  ["ci.deploys_ok", f.ci?.deploys_ok],
  ["k6.frontend_ok", f.k6?.frontend_ok],
  ["k6.quantum_ok", f.k6?.quantum_ok],
  ["k6.materials_ok", f.k6?.materials_ok],
];

let anyFail = false;
for (const [name, flag] of checks){
  if (flag === null || flag === undefined) { console.log("–", name, "n/a"); continue; }
  if (flag){ ok(name); } else { fail(name); anyFail = true; }
}

if (anyFail) process.exit(1);
console.log("All budgets satisfied.");
