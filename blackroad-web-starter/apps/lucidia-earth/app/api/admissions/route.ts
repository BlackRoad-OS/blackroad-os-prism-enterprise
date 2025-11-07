import { NextRequest, NextResponse } from "next/server";
import { randomUUID, createHash } from "node:crypto";
import { z } from "zod";
import { getAgentById } from "@br/registry";

const submissionSchema = z.object({
  id: z.string().min(1),
  applicant: z.object({
    name: z.string().min(1).max(120),
    email: z.string().email(),
    reason: z.string().min(1),
  }),
});

const WINDOW_MS = 10 * 60 * 1000;
const MAX_REQUESTS = 5;

type RateLimitEntry = {
  count: number;
  resetAt: number;
};

const rateLimitStore = new Map<string, RateLimitEntry>();

function sanitize(input: string): string {
  return input.replace(/<[^>]+>/g, "").trim();
}

function enforceRateLimit(key: string): boolean {
  const now = Date.now();
  const entry = rateLimitStore.get(key);
  if (!entry || entry.resetAt <= now) {
    rateLimitStore.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return true;
  }

  if (entry.count >= MAX_REQUESTS) {
    return false;
  }

  entry.count += 1;
  return true;
}

function getClientKey(request: NextRequest): string {
  const forwarded = request.headers.get("x-forwarded-for");
  if (forwarded) {
    return forwarded.split(",")[0]?.trim() ?? "unknown";
  }

  return request.ip ?? "unknown";
}

function hashEmail(email: string): string {
  return createHash("sha256").update(email.toLowerCase()).digest("hex");
}

export async function POST(request: NextRequest) {
  const clientKey = getClientKey(request);
  if (!enforceRateLimit(clientKey)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const parsed = submissionSchema.safeParse(payload);
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid submission" }, { status: 400 });
  }

  const agent = await getAgentById(parsed.data.id);
  if (!agent) {
    return NextResponse.json({ error: "Agent not found" }, { status: 404 });
  }

  const name = sanitize(parsed.data.applicant.name);
  if (!name) {
    return NextResponse.json({ error: "Name is required" }, { status: 400 });
  }
  const reason = sanitize(parsed.data.applicant.reason);
  if (!reason) {
    return NextResponse.json({ error: "Reason is required" }, { status: 400 });
  }
  const reasonBytes = Buffer.byteLength(reason, "utf-8");
  if (reasonBytes > 2048) {
    return NextResponse.json({ error: "Reason must be under 2KB" }, { status: 413 });
  }

  const ticketId = randomUUID();
  const ts = new Date().toISOString();
  const emailHash = hashEmail(parsed.data.applicant.email);

  console.info(
    JSON.stringify({
      type: "admissions-ticket",
      ticketId,
      agentId: agent.id,
      emailHash,
      ts,
    })
  );

  return NextResponse.json({
    ticketId,
    agentId: agent.id,
    ts,
  });
}
