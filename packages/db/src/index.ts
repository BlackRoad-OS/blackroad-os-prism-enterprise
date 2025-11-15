import { PrismaClient } from "@prisma/client";

export const prisma = new PrismaClient();

export async function withPrisma<T>(handler: (client: PrismaClient) => Promise<T>): Promise<T> {
  return handler(prisma);
}

export type { PrismaClient };

export * from "./types.js";
export { createInMemoryDb } from "./in-memory.js";

// Prisma binding is provided as a factory to avoid requiring a database for tests.
export { createPrismaComplianceDb } from "./prisma-adapter.js";
