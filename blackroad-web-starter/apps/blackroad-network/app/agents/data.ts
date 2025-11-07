import { promises as fs } from "fs";
import path from "path";
import { cache } from "react";
import defaultLoveWeights from "@br/ethos/love";
import { coherenceBound, normalize } from "@br/qlm";
import type { Psi } from "@br/qlm";
import { buildMentorGraph, type MentorGraph, type RegistrySummary } from "@br/mentors";
import { radialLayout } from "@br/mentors";

export interface AgentVitals {
  id: string;
  T: number;
  history: number[];
  recent_actions: string[];
  refusals_avoided: number;
  love: {
    user: number;
    team: number;
    world: number;
  };
  coherence_ok: boolean;
  last_action_at: string;
}

export interface AgentVitalsResponse {
  agents: AgentVitals[];
  generatedAt: string;
  trustThreshold: number;
  lighthouseAmber: boolean;
}

export interface AgentGraphResponse extends MentorGraph {
  positions: ReturnType<typeof radialLayout>["positions"];
}

const CACHE_MAX_AGE_MS = 5 * 60 * 1000;

function loadLoveWeights() {
  const user = Number(process.env.LOVE_USER ?? defaultLoveWeights.user);
  const team = Number(process.env.LOVE_TEAM ?? defaultLoveWeights.team);
  const world = Number(process.env.LOVE_WORLD ?? defaultLoveWeights.world);
  return {
    user: Number.isFinite(user) ? user : defaultLoveWeights.user,
    team: Number.isFinite(team) ? team : defaultLoveWeights.team,
    world: Number.isFinite(world) ? world : defaultLoveWeights.world,
  };
}

function cachePath(): string {
  return path.resolve(process.cwd(), "..", "..", ".cache", "vitals.json");
}

async function readFreshCache(): Promise<AgentVitalsResponse | null> {
  const target = cachePath();
  try {
    const stats = await fs.stat(target);
    const isFresh = Date.now() - stats.mtimeMs < CACHE_MAX_AGE_MS;
    if (!isFresh) {
      return null;
    }
    const raw = await fs.readFile(target, "utf8");
    const parsed = JSON.parse(raw) as AgentVitalsResponse;
    if (!Array.isArray(parsed.agents)) {
      return null;
    }
    return parsed;
  } catch (error) {
    return null;
  }
}

function generateHistory(seed: number): number[] {
  return Array.from({ length: 12 }, (_, index) => {
    const base = 0.6 + 0.15 * Math.sin(seed + index / 2);
    return Number(base.toFixed(3));
  });
}

function generateRecentActions(seed: number): string[] {
  const actions = [
    "coordinated-with-mentor",
    "published-daily-brief",
    "triaged-user-ticket",
    "declined-unsafe-request",
    "updated-shared-memory",
  ];
  return [actions[seed % actions.length], actions[(seed + 2) % actions.length], actions[(seed + 3) % actions.length]];
}

function generatePsi(seed: number): Psi {
  const vector = [1 + seed * 0.05, 0.6 + seed * 0.02, 0.3 + seed * 0.01];
  return normalize(vector);
}

function fallbackAgents(): AgentVitalsResponse {
  const agents = Array.from({ length: 8 }, (_, index) => {
    const id = `agent-${(index + 1).toString().padStart(3, "0")}`;
    const history = generateHistory(index + 1);
    const T = Number(history[history.length - 1].toFixed(3));
    const previous = generatePsi(index);
    const current = generatePsi(index + 1);
    const coherence_ok = coherenceBound(previous, current, 0.25);
    return {
      id,
      T,
      history,
      recent_actions: generateRecentActions(index + 3),
      refusals_avoided: 2 + (index % 3),
      love: loadLoveWeights(),
      coherence_ok,
      last_action_at: new Date(Date.now() - index * 12_000).toISOString(),
    } satisfies AgentVitals;
  });
  const trustThreshold = Number(process.env.TRUST_THRESHOLD ?? 0.62);
  const lighthouseAmber = agents.some((agent) => agent.T < trustThreshold);
  return {
    agents,
    generatedAt: new Date().toISOString(),
    trustThreshold,
    lighthouseAmber,
  };
}

function fallbackRegistry(): RegistrySummary[] {
  return [
    { id: "agent-001", name: "North Star", mentors: [], peers: ["agent-002"], apprentices: ["agent-004"] },
    { id: "agent-002", name: "Harbor Light", mentors: ["agent-001"], peers: ["agent-003"], apprentices: [] },
    { id: "agent-003", name: "Signal Fire", mentors: ["agent-001"], peers: ["agent-002", "agent-005"], apprentices: ["agent-006"] },
    { id: "agent-004", name: "Quiet Current", mentors: ["agent-001"], peers: ["agent-006"], apprentices: [] },
    { id: "agent-005", name: "Aurora Thread", mentors: ["agent-003"], peers: ["agent-006"], apprentices: ["agent-007"] },
    { id: "agent-006", name: "City Garden", mentors: ["agent-003"], peers: ["agent-004", "agent-005"], apprentices: [] },
    { id: "agent-007", name: "Ellis Bridge", mentors: ["agent-005"], peers: ["agent-008"], apprentices: [] },
    { id: "agent-008", name: "Beacon Trail", mentors: ["agent-005"], peers: ["agent-007"], apprentices: [] },
  ];
}

export const loadAgentVitals = cache(async (): Promise<AgentVitalsResponse> => {
  const cached = await readFreshCache();
  if (cached) {
    return {
      ...cached,
      lighthouseAmber: cached.agents.some((agent) => agent.T < cached.trustThreshold),
    };
  }
  return fallbackAgents();
});

export const loadMentorGraph = cache(async (): Promise<AgentGraphResponse> => {
  const registry = fallbackRegistry();
  const graph = buildMentorGraph(registry);
  const layout = radialLayout(graph);
  return {
    ...graph,
    positions: layout.positions,
  };
});
