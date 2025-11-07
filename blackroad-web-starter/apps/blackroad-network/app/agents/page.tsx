import Link from "next/link";
import type { Metadata } from "next";
import { headers } from "next/headers";

type AgentListItem = {
  id: string;
  cluster: string;
  generation: string;
  ethos: string;
  covenants: string[];
  ssn: string;
};

type AgentsResponse = {
  total: number;
  items: AgentListItem[];
};

const PAGE_SIZE = 25;

export const metadata: Metadata = {
  title: "Agent Registry",
  description: "Browse the active BlackRoad agent registry.",
};

async function fetchAgents(): Promise<AgentsResponse> {
  const headerList = headers();
  const host = headerList.get("host") ?? "localhost:3000";
  const protocol = host.includes("localhost") || host.startsWith("127.") ? "http" : "https";
  const baseUrl = process.env.AGENTS_API_BASE ?? `${protocol}://${host}`;

  const response = await fetch(`${baseUrl}/api/agents`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to load agents: ${response.status}`);
  }

  return response.json();
}

export default async function AgentsPage({
  searchParams,
}: {
  searchParams?: { page?: string };
}) {
  let data: AgentsResponse | null = null;
  let error: string | null = null;

  try {
    data = await fetchAgents();
  } catch (err) {
    error = err instanceof Error ? err.message : "Unknown error";
  }

  const totalItems = data?.items.length ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const requestedPage = Number.parseInt(searchParams?.page ?? "1", 10);
  const currentPage = Number.isNaN(requestedPage)
    ? 1
    : Math.min(Math.max(requestedPage, 1), totalPages);

  const start = (currentPage - 1) * PAGE_SIZE;
  const pageItems = data?.items.slice(start, start + PAGE_SIZE) ?? [];
  const rangeStart = totalItems === 0 ? 0 : start + 1;
  const rangeEnd = totalItems === 0 ? 0 : Math.min(start + PAGE_SIZE, totalItems);

  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-slate-900">Agent Registry</h1>
        <p className="max-w-2xl text-sm text-slate-600">
          Live roster sourced from the BlackRoad Prism console. Searchable API available at
          <span className="font-medium"> /api/agents</span>.
        </p>
      </header>

      {error ? (
        <p className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}. Please try again later.
        </p>
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
                <tr>
                  <th scope="col" className="px-4 py-3">
                    Agent
                  </th>
                  <th scope="col" className="px-4 py-3">
                    Cluster
                  </th>
                  <th scope="col" className="px-4 py-3">
                    Generation
                  </th>
                  <th scope="col" className="px-4 py-3">
                    Covenants
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white text-sm text-slate-700">
                {pageItems.map((agent) => (
                  <tr key={agent.id}>
                    <td className="px-4 py-3">
                      <div className="space-y-1">
                        <p className="font-medium text-slate-900">{agent.id}</p>
                        <p className="text-xs text-slate-500">{agent.ethos}</p>
                        <p className="text-[11px] uppercase tracking-wider text-slate-400">
                          SSN {agent.ssn.slice(0, 8)}…
                        </p>
                      </div>
                    </td>
                    <td className="px-4 py-3">{agent.cluster}</td>
                    <td className="px-4 py-3 capitalize">{agent.generation}</td>
                    <td className="px-4 py-3">
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
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <footer className="flex items-center justify-between text-sm text-slate-600">
            <span>
              Showing {rangeStart}–{rangeEnd} of {totalItems} agents
            </span>
            <div className="flex items-center gap-2">
              <Link
                href={`/agents?page=${Math.max(currentPage - 1, 1)}`}
                className="rounded-md border border-slate-200 px-3 py-1 transition hover:border-slate-300 hover:text-slate-900"
                aria-disabled={currentPage === 1}
              >
                Previous
              </Link>
              <span className="text-xs uppercase tracking-wide">
                Page {currentPage} of {totalPages}
              </span>
              <Link
                href={`/agents?page=${Math.min(currentPage + 1, totalPages)}`}
                className="rounded-md border border-slate-200 px-3 py-1 transition hover:border-slate-300 hover:text-slate-900"
                aria-disabled={currentPage === totalPages}
              >
                Next
              </Link>
            </div>
          </footer>
        </>
      )}
    </section>
  );
}
