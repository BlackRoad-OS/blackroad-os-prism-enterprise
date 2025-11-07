import { NextResponse } from "next/server";

interface AdmissionsRequest {
  proposal: string;
  love?: Record<string, number>;
}

function createTicketId(): string {
  const base = Date.now().toString(36).toUpperCase();
  const suffix = Math.floor(Math.random() * 10_000)
    .toString()
    .padStart(4, "0");
  return `LUC-${base}-${suffix}`;
}

export async function POST(request: Request) {
  try {
    const payload = (await request.json()) as AdmissionsRequest;
    if (!payload.proposal || payload.proposal.trim().length < 8) {
      return NextResponse.json({ error: "proposal_too_short" }, { status: 400 });
    }
    const ticketId = createTicketId();
    const logEntry = {
      kind: "bootcamp_admission",
      ticketId,
      proposalLength: payload.proposal.trim().length,
      love: payload.love,
      timestamp: new Date().toISOString(),
    } satisfies Record<string, unknown>;
    console.log(JSON.stringify(logEntry));
    return NextResponse.json({ ticketId });
  } catch (error) {
    return NextResponse.json({ error: "invalid_payload" }, { status: 400 });
  }
}
