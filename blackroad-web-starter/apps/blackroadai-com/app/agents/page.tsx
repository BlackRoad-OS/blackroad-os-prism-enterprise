import Link from "next/link";

const endpoints = [
  {
    method: "GET",
    path: "/api/agents",
    description: "Returns paginated registry entries with summary trust metrics.",
  },
  {
    method: "GET",
    path: "/api/agents/:id",
    description: "Retrieves a single agent record including mentor ring membership and current love weights.",
  },
  {
    method: "GET",
    path: "/api/agents/vitals",
    description: "Aggregated vitals with trust score T, refusal avoidance counts, and sparkline history.",
  },
  {
    method: "GET",
    path: "/api/agents/graph",
    description: "Mentor graph DAG with node metadata and radial layout coordinates.",
  },
];

const curlExamples = `curl https://blackroad.network/api/agents/vitals | jq
curl https://blackroad.network/api/agents/graph | jq`;

const schemaLinks = [
  { label: "Agent", href: "https://blackroad.network/api/agents/schema.json" },
  { label: "Vitals", href: "https://blackroad.network/api/agents/vitals/schema.json" },
  { label: "Graph", href: "https://blackroad.network/api/agents/graph/schema.json" },
];

export default function AgentsDocsPage() {
  return (
    <article className="prose prose-slate max-w-none">
      <h1>Agent API surface</h1>
      <p>
        Blackroad agent APIs center on trust: every response carries coherence signals and Love operator weights so teams
        can steer mentorship. The endpoints below mirror the dashboards on <Link href="https://blackroad.network/agents">blackroad.network/agents</Link>.
      </p>

      <h2>Endpoints</h2>
      <table>
        <thead>
          <tr>
            <th>Method</th>
            <th>Path</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {endpoints.map((endpoint) => (
            <tr key={endpoint.path}>
              <td>{endpoint.method}</td>
              <td>{endpoint.path}</td>
              <td>{endpoint.description}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Quick start</h2>
      <p>
        The vitals and graph endpoints stream JSON that stays under 10 KB so you can poll them in under a second.
        Example fetch calls:
      </p>
      <pre>
        <code>{curlExamples}</code>
      </pre>

      <h2>Schema links</h2>
      <p>
        Each response ships with a JSON Schema that the trust gate validates before emit. You can download them below and
        bake into your client tests.
      </p>
      <ul>
        {schemaLinks.map((schema) => (
          <li key={schema.href}>
            <Link href={schema.href} className="text-indigo-600 hover:text-indigo-500">
              {schema.label} schema
            </Link>
          </li>
        ))}
      </ul>

      <h2>Trust guardrails</h2>
      <p>
        Every write-bound request must present <code>X-Agent-Trust</code> and clear the gate at
        <code>TRUST_THRESHOLD</code> (currently 0.62). The vitals endpoint surfaces the same threshold so you can tune
        your automation without guessing.
      </p>
    </article>
  );
}
