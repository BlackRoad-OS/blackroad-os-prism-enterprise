import { useMemo } from "react";

type NodeStatus = "pending" | "running" | "done" | "error";

type GraphNode = {
  id: string;
  label: string;
  status?: NodeStatus;
};

type GraphEdge = {
  from: string;
  to: string;
  label?: string;
};

type GraphProps = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

type PositionedNode = GraphNode & { x: number; y: number };

const STATUS_COLOR: Record<NodeStatus, string> = {
  pending: "#64748b",
  running: "#2563eb",
  done: "#16a34a",
  error: "#dc2626",
};

function layout(nodes: GraphNode[], edges: GraphEdge[]): PositionedNode[] {
  const adjacency = new Map<string, string[]>();
  const indegree = new Map<string, number>();
  nodes.forEach((node) => {
    adjacency.set(node.id, []);
    indegree.set(node.id, 0);
  });
  edges.forEach((edge) => {
    adjacency.get(edge.from)?.push(edge.to);
    indegree.set(edge.to, (indegree.get(edge.to) ?? 0) + 1);
  });

  const queue: string[] = [];
  indegree.forEach((value, key) => {
    if (value === 0) queue.push(key);
  });

  const levels = new Map<string, number>();
  while (queue.length > 0) {
    const current = queue.shift()!;
    const level = levels.get(current) ?? 0;
    adjacency.get(current)?.forEach((neighbor) => {
      const next = (levels.get(neighbor) ?? level) + 1;
      if (!levels.has(neighbor) || next > (levels.get(neighbor) ?? 0)) {
        levels.set(neighbor, next);
      }
      const degree = (indegree.get(neighbor) ?? 1) - 1;
      indegree.set(neighbor, degree);
      if (degree === 0) queue.push(neighbor);
    });
  }

  const grouped = new Map<number, PositionedNode[]>();
  nodes.forEach((node) => {
    const level = levels.get(node.id) ?? 0;
    const column = grouped.get(level) ?? [];
    grouped.set(level, column);
    column.push({ ...node, x: level, y: column.length });
  });

  const horizontalSpacing = 180;
  const verticalSpacing = 120;

  const positioned: PositionedNode[] = [];
  grouped.forEach((column, level) => {
    column.forEach((node, index) => {
      positioned.push({ ...node, x: level * horizontalSpacing + 80, y: index * verticalSpacing + 60 });
    });
  });

  return positioned;
}

export default function Graph({ nodes, edges }: GraphProps) {
  const positioned = useMemo(() => layout(nodes, edges), [nodes, edges]);
  const nodeMap = new Map(positioned.map((node) => [node.id, node] as const));
  if (positioned.length === 0) {
    return <div>No nodes in graph.</div>;
  }
  const width = Math.max(...positioned.map((node) => node.x)) + 160 || 320;
  const height = Math.max(...positioned.map((node) => node.y)) + 160 || 240;

  return (
    <svg width={width} height={height} role="img" aria-label="execution-graph">
      {edges.map((edge) => {
        const from = nodeMap.get(edge.from);
        const to = nodeMap.get(edge.to);
        if (!from || !to) return null;
        const path = `M ${from.x} ${from.y} C ${(from.x + to.x) / 2} ${from.y}, ${(from.x + to.x) / 2} ${to.y}, ${to.x} ${to.y}`;
        return (
          <g key={`${edge.from}-${edge.to}`} className="graph-edge">
            <path d={path} fill="none" stroke="#94a3b8" strokeWidth={2} markerEnd="url(#arrowhead)" />
            {edge.label && (
              <text x={(from.x + to.x) / 2} y={(from.y + to.y) / 2} textAnchor="middle" className="graph-edge__label">
                {edge.label}
              </text>
            )}
          </g>
        );
      })}
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
        </marker>
      </defs>
      {positioned.map((node) => (
        <g key={node.id} className="graph-node" transform={`translate(${node.x - 50}, ${node.y - 20})`}>
          <rect width={100} height={40} rx={6} fill={STATUS_COLOR[node.status ?? "pending"]} opacity={0.85} />
          <text x={50} y={24} textAnchor="middle" fill="#fff">
            {node.label}
          </text>
        </g>
      ))}
    </svg>
  );
}
