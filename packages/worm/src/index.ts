import { createHash } from "node:crypto";

export interface WormAppendInput<T = unknown> {
  payload: T;
}

export interface WormBlock<T = unknown> {
  idx: number;
  ts: Date;
  payload: T;
  prevHash: string;
  hash: string;
}

export interface WormLedger<T = unknown> {
  append(entry: WormAppendInput<T>): Promise<WormBlock<T>>;
  tail(): WormBlock<T> | null;
  all(): WormBlock<T>[];
}

export class InMemoryWormLedger<T = unknown> implements WormLedger<T> {
  private blocks: WormBlock<T>[] = [];

  async append(entry: WormAppendInput<T>): Promise<WormBlock<T>> {
    const prev = this.blocks[this.blocks.length - 1] ?? null;
    const block: WormBlock<T> = {
      idx: prev ? prev.idx + 1 : 1,
      ts: new Date(),
      payload: entry.payload,
      prevHash: prev?.hash ?? "GENESIS",
      hash: computeHash(prev?.hash ?? "GENESIS", entry.payload),
    };
    this.blocks.push(block);
    return block;
  }

  tail(): WormBlock<T> | null {
    return this.blocks[this.blocks.length - 1] ?? null;
  }

  all(): WormBlock<T>[] {
import { createHash } from "crypto";
import { nanoid } from "nanoid";
import type { WormBlock } from "@blackroad/db";

export interface WormAdapter {
  persistBlock(block: WormBlock): Promise<void>;
  getLastBlock(): Promise<WormBlock | undefined>;
}

export class InMemoryWormAdapter implements WormAdapter {
  private blocks: WormBlock[] = [];

  async persistBlock(block: WormBlock): Promise<void> {
    this.blocks.push(block);
  }

  async getLastBlock(): Promise<WormBlock | undefined> {
    return this.blocks.at(-1);
  }

  getAll(): WormBlock[] {
    return [...this.blocks];
  }
}

function computeHash(prevHash: string, payload: unknown): string {
  const content = JSON.stringify({ prevHash, payload });
  return createHash("sha256").update(content).digest("hex");
}

export async function append(adapter: WormAdapter, payload: Record<string, unknown>): Promise<WormBlock> {
  const last = await adapter.getLastBlock();
  const idx = last ? last.idx + 1 : 0;
  const ts = new Date();
  const prevHash = last?.hash ?? "GENESIS";
  const hash = createHash("sha256")
    .update(`${prevHash}:${ts.toISOString()}:${JSON.stringify(payload)}`)
    .digest("hex");
  const block: WormBlock = {
    id: nanoid(),
    idx,
    ts,
    payload,
    prevHash,
    hash,
  };
  await adapter.persistBlock(block);
  return block;
}
