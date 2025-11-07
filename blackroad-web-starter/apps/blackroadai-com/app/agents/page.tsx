import Link from "next/link";
import type { Metadata } from "next";
import { getAllAgents } from "@br/registry";

export const metadata: Metadata = {
  title: "Agent API Catalog",
  description: "Explore available agents and connect to their BlackRoad Network profiles.",
};

export default async function AgentsCatalogPage() {
  const agents = await getAllAgents();

  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Agent API Catalog</h1>
        <p className="max-w-2xl text-sm text-slate-600">
          Browse the public roster of BlackRoad agents. Tap into each agent's ethos and covenants before integrating with
          the BlackRoad Network API.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {agents.map((agent) => (
          <article
            key={agent.id}
            className="flex h-full flex-col justify-between gap-4 rounded-xl border border-slate-200 bg-white/80 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="space-y-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">Cluster {agent.cluster}</p>
                <h2 className="text-xl font-semibold text-slate-900">{agent.id}</h2>
                <p className="text-sm text-slate-600">{agent.ethos}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {agent.covenants.slice(0, 4).map((covenant) => (
                  <span
                    key={`${agent.id}-${covenant}`}
                    className="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-600"
                  >
                    {covenant}
                  </span>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-between text-sm text-slate-500">
              <span className="capitalize">{agent.generation} generation</span>
              <Link
                href={`https://blackroad.network/agents/${agent.id}`}
                className="text-sm font-medium text-slate-900 underline-offset-4 hover:underline"
              >
                View on blackroad.network
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
