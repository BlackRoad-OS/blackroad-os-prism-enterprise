import { PrismEvent } from "../../packages/prism-core/src";
import { getEventBus } from "../events/bus";

type EventQuery = {
  topic?: string | RegExp;
  actor?: string;
  since?: string;
  limit?: number;
  reverse?: boolean;
};

class InMemoryEventStore {
  private events: PrismEvent[] = [];
  private subscription: (() => void) | null = null;

  constructor() {
    this.bindToBus();
  }

  private bindToBus() {
    if (this.subscription) return;
    const bus = getEventBus();
    this.subscription = bus.subscribe((event) => {
      this.append(event);
    });
  }

  append(event: PrismEvent) {
    this.events.push(cloneEvent(event));
  }

  list(query: EventQuery = {}): PrismEvent[] {
    const { topic, actor, since, limit, reverse } = query;
    let items = [...this.events];
    if (since) {
      const index = items.findIndex((evt) => evt.id === since);
      if (index >= 0) {
        items = items.slice(index + 1);
      }
    }
    if (topic) {
      const matcher = typeof topic === "string" ? new RegExp(`^${topic.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")}$`) : topic;
      items = items.filter((evt) => matcher.test(evt.topic));
    }
    if (actor) {
      items = items.filter((evt) => evt.actor === actor);
    }
    if (reverse) {
      items.reverse();
    }
    if (typeof limit === "number") {
      items = items.slice(0, limit);
    }
    return items.map(cloneEvent);
  }

  latest(): PrismEvent | undefined {
    return this.events.length > 0 ? cloneEvent(this.events[this.events.length - 1]) : undefined;
  }

  size(): number {
    return this.events.length;
  }

  reset() {
    this.events = [];
  }
}

function cloneEvent(event: PrismEvent): PrismEvent {
  return {
    ...event,
    payload: { ...(event.payload ?? {}) },
    kpis: event.kpis ? { ...event.kpis } : undefined,
    memory_deltas: event.memory_deltas ? event.memory_deltas.map((delta) => ({ ...delta })) : undefined,
  };
}

const STORE = new InMemoryEventStore();

export function getEventStore(): InMemoryEventStore {
  return STORE;
}

export function resetEventStore(): void {
  STORE.reset();
}
