// tools/miners/bridge.js
// Polls miner summary endpoints and posts miner.sample events to Prism.
// OPSEC: no wallet keys, no secrets in logs.

import fetch from "node-fetch";

const PRISM_API = process.env.PRISM_API; // e.g. http://localhost:4000 or your gateway
const PRISM_TOKEN = process.env.PRISM_TOKEN || ""; // if your /events needs auth
const ORG_ID = process.env.PRISM_ORG_ID || "default";

if (!PRISM_API) {
  console.error("Set PRISM_API (e.g., http://localhost:4000)");
  process.exit(1);
}

const watchers = [];

const xmrigUrl = process.env.XMRIG_URL || "http://xmrig:18080/2/summary";
if (xmrigUrl) {
  watchers.push({
    miner: "xmrig",
    agentId: process.env.MINER_AGENT_ID || "miner:xmrig",
    pollMs: coercePoll(process.env.XMRIG_POLL_MS, 15_000),
    request: () => ({ url: xmrigUrl, init: { method: "GET" } }),
    parser: parseXmrig,
  });
}

const verusUrl = process.env.VERUS_URL || process.env.VERUS_SUMMARY_URL || null;
if (verusUrl) {
  watchers.push({
    miner: "verusminer",
    agentId: process.env.VERUS_AGENT_ID || "miner:verus",
    pollMs: coercePoll(process.env.VERUS_POLL_MS, 20_000),
    request: () => cpuminerRequest(verusUrl),
    parser: parseCpuminer("verusminer"),
  });
}

const ltcUrl = process.env.LTC_URL || process.env.LTC_SUMMARY_URL || null;
if (ltcUrl) {
  watchers.push({
    miner: "ltc-cpuminer",
    agentId: process.env.LTC_AGENT_ID || "miner:ltc",
    pollMs: coercePoll(process.env.LTC_POLL_MS, 20_000),
    request: () => cpuminerRequest(ltcUrl),
    parser: parseCpuminer("ltc-cpuminer"),
  });
}

const chiaUrl = process.env.CHIA_URL || process.env.CHIA_SUMMARY_URL || null;
if (chiaUrl) {
  watchers.push({
    miner: "chia",
    agentId: process.env.CHIA_AGENT_ID || "farmer:chia",
    pollMs: coercePoll(process.env.CHIA_POLL_MS, 60_000),
    request: () => ({ url: chiaUrl, init: { method: "GET" } }),
    parser: parseChia,
  });
}

if (watchers.length === 0) {
  console.warn("No miner endpoints configured. Set XMRIG_URL / VERUS_URL / LTC_URL / CHIA_URL env vars.");
}

watchers.forEach((watcher) => {
  const poll = async () => {
    try {
      const { url, init } = watcher.request();
      const response = await fetch(url, init);
      if (!response.ok) throw new Error(`${watcher.miner} ${response.status}`);
      const summary = await response.json();
      const payload = watcher.parser(summary);
      payload.ts = new Date().toISOString();

      await postSample(watcher.miner, watcher.agentId, payload);
    } catch (error) {
      console.error(`[bridge] ${watcher.miner} error:`, error.message);
    }
  };

  console.log(
    `[bridge] watcher ready for ${watcher.miner} (agent ${watcher.agentId}) every ${watcher.pollMs}ms`
  );
  poll();
  setInterval(poll, watcher.pollMs);
});

function coercePoll(value, fallback) {
  const parsed = Number.parseInt(value ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function cpuminerRequest(url) {
  const endpoint = url.endsWith("/") ? url : `${url}/`;
  return {
    url: endpoint,
    init: {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({ command: "summary" }),
    },
  };
}

async function postSample(miner, agentId, payload) {
  const ev = {
    type: "miner.sample",
    orgId: ORG_ID,
    agentId,
    payload: { miner, ...payload },
  };

  const res = await fetch(`${PRISM_API}/events`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(PRISM_TOKEN ? { authorization: `Bearer ${PRISM_TOKEN}` } : {}),
    },
    body: JSON.stringify(ev),
  });

  if (!res.ok) {
    const txt = await res.text();
    console.error(`[bridge] prism events POST failed (${miner}):`, res.status, txt.slice(0, 200));
    return;
  }

  console.log(
    `[bridge] posted miner.sample for ${miner}: ${payload.shares_accepted ?? "?"}/${payload.shares_rejected ?? "?"} @ ${payload.hashrate_1m ?? payload.hashrate ?? payload.hashrate_khs ?? "?"}`
  );
}

function parseXmrig(summary) {
  return {
    pool: summary.connection?.pool || summary.connection?.url || null,
    hashrate_1m: summary.hashrate?.total?.[0] ?? summary.hashrate?.total?.[1] ?? null,
    hashrate_15m: summary.hashrate?.total?.[2] ?? null,
    shares_accepted:
      summary.results?.shares_good ?? summary.results?.accepted ?? summary.results?.shares ?? null,
    shares_rejected: summary.results?.shares_bad ?? summary.results?.rejected ?? null,
    shares_total: summary.results?.shares_total ?? null,
  };
}

function parseCpuminer(miner) {
  return (summary) => {
    const stats = Array.isArray(summary.SUMMARY) ? summary.SUMMARY[0] : null;
    if (!stats) {
      throw new Error("no SUMMARY block in cpuminer API response");
    }

    const accepted = stats.Accepted ?? stats.accepted ?? stats.Shares_Accepted ?? null;
    const rejected = stats.Rejected ?? stats.rejected ?? stats.Shares_Rejected ?? null;
    const total = stats.Shares_Total ?? (accepted != null && rejected != null ? accepted + rejected : null);
    const khs = stats.KHS ?? stats["KHS 5s"] ?? stats["KHS av"] ?? null;

    return {
      algo: stats.Algorithm || stats.ALGO || null,
      hashrate_khs: khs,
      hashrate_1m: khs != null ? khs * 1000 : null,
      shares_accepted: accepted,
      shares_rejected: rejected,
      shares_total: total,
      pool: stats["Stratum Active"] ? stats["Stratum URL"] || null : null,
    };
  };
}

function parseChia(summary) {
  const farmer = summary.farmer ?? summary;
  const plots = farmer.plots ?? farmer.plot_count ?? farmer.totalPlots ?? null;

  return {
    status: farmer.status ?? farmer.farmer_status ?? null,
    signage_points_last_24h:
      farmer.signage_points_last_24h ??
      farmer.signagePointsLast24H ??
      summary.signage_points_last_24h ??
      null,
    plots_total: typeof plots === "number" ? plots : plots?.total ?? null,
    plots_farmer: farmer.plots_farmer ?? plots?.farmer ?? null,
    plots_harvester: farmer.plots_harvester ?? plots?.harvester ?? null,
    space_bytes:
      farmer.space_bytes ??
      farmer.total_size_bytes ??
      farmer.space?.bytes ??
      summary.total_size_bytes ??
      null,
    last_height_farmed: farmer.last_height_farmed ?? summary.last_height_farmed ?? null,
    wallet_balance_xch: farmer.wallet_balance_xch ?? summary.wallet_balance_xch ?? null,
  };
}
