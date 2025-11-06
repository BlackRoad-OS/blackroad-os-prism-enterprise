import { PrismSpan } from "../../packages/prism-core/src";

type TraceRecord = {
  traceId: string;
  spans: PrismSpan[];
  startedAt: string;
  endedAt?: string;
};

type TraceTreeNode = PrismSpan & { durationMs?: number; children: TraceTreeNode[] };

type TraceQuery = {
  limit?: number;
};

class InMemoryTraceExporter {
  private traces = new Map<string, TraceRecord>();

  ingest(traceId: string, spans: PrismSpan[]): TraceRecord {
    const normalized = spans.map((span) => normalizeSpan(span));
    const existing = this.traces.get(traceId);
    const merged = existing ? mergeSpans(existing.spans, normalized) : normalized;
    const sorted = merged.slice().sort((a, b) => a.startTs.localeCompare(b.startTs));
    const startedAt = sorted[0]?.startTs ?? new Date().toISOString();
    const endedAt = sorted.reduce<string | undefined>((latest, span) => {
      if (!span.endTs) return latest;
      if (!latest || span.endTs > latest) return span.endTs;
      return latest;
    }, existing?.endedAt);
    const record: TraceRecord = {
      traceId,
      spans: sorted,
      startedAt,
      endedAt,
    };
    this.traces.set(traceId, record);
    return cloneRecord(record);
  }

  list(query: TraceQuery = {}): TraceRecord[] {
    const { limit } = query;
    const records = Array.from(this.traces.values())
      .slice()
      .sort((a, b) => b.startedAt.localeCompare(a.startedAt))
      .map(cloneRecord);
    return typeof limit === "number" ? records.slice(0, limit) : records;
  }

  get(traceId: string): TraceRecord | undefined {
    const record = this.traces.get(traceId);
    return record ? cloneRecord(record) : undefined;
  }

  toTree(traceId: string): TraceTreeNode[] {
    const record = this.traces.get(traceId);
    if (!record) return [];
    return buildTree(record.spans).map(cloneNode);
  }

  reset() {
    this.traces.clear();
  }
}

function normalizeSpan(span: PrismSpan): PrismSpan {
  return {
    ...span,
    attrs: span.attrs ? { ...span.attrs } : undefined,
    links: span.links ? [...span.links] : undefined,
  };
}

function mergeSpans(existing: PrismSpan[], incoming: PrismSpan[]): PrismSpan[] {
  const byId = new Map<string, PrismSpan>();
  for (const span of existing) {
    byId.set(span.spanId, normalizeSpan(span));
  }
  for (const span of incoming) {
    byId.set(span.spanId, normalizeSpan(span));
  }
  return Array.from(byId.values());
}

function buildTree(spans: PrismSpan[]): TraceTreeNode[] {
  const byParent = new Map<string | undefined, TraceTreeNode[]>();
  const nodes = new Map<string, TraceTreeNode>();
  for (const span of spans) {
    const node: TraceTreeNode = { ...span, children: [] };
    if (span.endTs) {
      node.durationMs = Math.max(Date.parse(span.endTs) - Date.parse(span.startTs), 0);
    }
    nodes.set(span.spanId, node);
    const key = span.parentSpanId ?? undefined;
    const list = byParent.get(key);
    if (list) {
      list.push(node);
    } else {
      byParent.set(key, [node]);
    }
  }
  for (const node of nodes.values()) {
    node.children = (byParent.get(node.spanId) ?? []).sort((a, b) => a.startTs.localeCompare(b.startTs));
  }
  const roots = byParent.get(undefined) ?? [];
  return roots.sort((a, b) => a.startTs.localeCompare(b.startTs));
}

function cloneNode(node: TraceTreeNode): TraceTreeNode {
  return {
    ...node,
    attrs: node.attrs ? { ...node.attrs } : undefined,
    links: node.links ? [...node.links] : undefined,
    children: node.children.map(cloneNode),
  };
}

function cloneRecord(record: TraceRecord): TraceRecord {
  return {
    traceId: record.traceId,
    startedAt: record.startedAt,
    endedAt: record.endedAt,
    spans: record.spans.map((span) => ({
      ...span,
      attrs: span.attrs ? { ...span.attrs } : undefined,
      links: span.links ? [...span.links] : undefined,
    })),
  };
}

const EXPORTER = new InMemoryTraceExporter();

export function getTraceExporter(): InMemoryTraceExporter {
  return EXPORTER;
}

export function resetTraceExporter(): void {
  EXPORTER.reset();
}
