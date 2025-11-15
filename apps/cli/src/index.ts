#!/usr/bin/env node
import { randomUUID } from "node:crypto";
import { promises as fs } from "node:fs";
import { resolve } from "node:path";
import { Command } from "commander";
import YAML from "yaml";
import {
  AccountFeePlan,
  FeeAccrualRecord,
  FeeSchedule,
  computeDailyAccrual,
  generateInArrearsInvoice,
  InMemoryExceptionQueue,
} from "@lucidia/core";
import { enforceFeeCap, requireCustodyAuthorization } from "@blackroad/policies";
import { renderInvoicePdf, submitCustodyDeduction } from "@blackroad/integrations";
import { appendWorm, loadState, saveState, StoredInvoice, InvoiceDataSnapshot } from "./state.js";

interface MarketValueFileEntry {
  accountId: string;
  marketValue: number;
  cryptoMarketValue?: number;
}

function toSchedule(spec: unknown, name: string): FeeSchedule {
  return {
    id: randomUUID(),
    name,
    status: "Active",
    spec: spec as FeeSchedule["spec"],
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

function findScheduleByName(state: Awaited<ReturnType<typeof loadState>>, name: string): FeeSchedule | undefined {
  return Object.values(state.schedules).find((schedule) => schedule.name === name);
}

function parseDate(input: string): Date {
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) {
    throw new Error(`Invalid date: ${input}`);
  }
  return date;
}

function parseQuarter(quarter: string): { start: Date; end: Date } {
  const match = quarter.match(/^(\d{4})Q([1-4])$/);
  if (!match) {
    throw new Error(`Invalid quarter format: ${quarter}`);
  }
  const year = Number(match[1]);
  const q = Number(match[2]);
  const startMonth = (q - 1) * 3;
  const start = new Date(Date.UTC(year, startMonth, 1));
  const end = new Date(Date.UTC(year, startMonth + 3, 0));
  return { start, end };
}

function asInvoiceSnapshot(draft: ReturnType<typeof generateInArrearsInvoice>): InvoiceDataSnapshot {
  return {
    billingPeriodStart: draft.billingPeriodStart.toISOString(),
    billingPeriodEnd: draft.billingPeriodEnd.toISOString(),
    billingGroupId: draft.billingGroupId ?? null,
    accountId: draft.accountId ?? null,
    currency: draft.currency,
    amount: draft.amount,
    lines: draft.lines,
    minimumAppliedUSD: draft.minimumAppliedUSD,
  };
}

const program = new Command();
program.name("blackroad-feeforge").description("FeeForge billing CLI");

program
  .command("schedule:create")
  .description("Create or update a fee schedule")
  .requiredOption("--name <name>")
  .requiredOption("--file <path>")
  .action(async (options) => {
    const state = await loadState();
    const specFile = await fs.readFile(resolve(options.file), "utf-8");
    const spec = YAML.parse(specFile);
    const existing = findScheduleByName(state, options.name);
    const schedule = toSchedule(spec, options.name);
    const scheduleId = existing ? existing.id : schedule.id;
    state.schedules[scheduleId] = { ...schedule, id: scheduleId };
    appendWorm(state, { type: "FEE_SCHEDULE", scheduleId, name: options.name, spec });
    await saveState(state);
    console.log(`Saved fee schedule ${options.name} (${scheduleId})`);
  });

program
  .command("plan:attach")
  .description("Attach a fee schedule to an account")
  .requiredOption("--account <id>")
  .requiredOption("--schedule <name>")
  .requiredOption("--freq <freq>", "Billing frequency (Monthly|Quarterly)")
  .requiredOption("--mode <mode>", "Billing mode (InArrears|InAdvance)")
  .option("--group <id>")
  .option("--custody-deduction", "Allow custody deduction")
  .option("--performance")
  .option("--start <date>", "Plan start date", new Date().toISOString())
  .action(async (options) => {
    const state = await loadState();
    const schedule = findScheduleByName(state, options.schedule);
    if (!schedule) {
      throw new Error(`Fee schedule ${options.schedule} not found`);
    }
    const plan: AccountFeePlan = {
      id: randomUUID(),
      accountId: options.account,
      feeScheduleId: schedule.id,
      billingGroupId: options.group ?? null,
      startDate: parseDate(options.start),
      endDate: null,
      billFrequency: options.freq,
      billMode: options.mode,
      billCurrency: "USD",
      custodyDeductionAllowed: Boolean(options.custodyDeduction),
      performanceFeeAllowed: Boolean(options.performance),
      createdAt: new Date(),
    };
    state.plans[plan.id] = plan;
    appendWorm(state, { type: "PLAN_ATTACHED", plan });
    await saveState(state);
    console.log(`Attached schedule ${options.schedule} to account ${plan.accountId} (${plan.id})`);
  });

program
  .command("accruals:run")
  .description("Run daily accruals for the given date")
  .requiredOption("--as-of <date>")
  .requiredOption("--market-file <path>", "JSON file of market values")
  .action(async (options) => {
    const state = await loadState();
    const asOf = parseDate(options["asOf"] ?? options.asOf);
    const marketRaw = await fs.readFile(resolve(options.marketFile), "utf-8");
    const marketEntries = JSON.parse(marketRaw) as MarketValueFileEntry[];
    const queue = new InMemoryExceptionQueue();
    const results: FeeAccrualRecord[] = [];
    const households = new Map<string, number>();
    for (const plan of Object.values(state.plans)) {
      if (!state.schedules[plan.feeScheduleId]) continue;
      if (plan.billingGroupId) {
        const total = marketEntries
          .filter((entry) => entry.accountId === plan.accountId || Object.values(state.plans).some((p) => p.accountId === entry.accountId && p.billingGroupId === plan.billingGroupId))
          .reduce((sum, entry) => sum + entry.marketValue + (entry.cryptoMarketValue ?? 0), 0);
        households.set(plan.billingGroupId, total);
      }
    }

    for (const plan of Object.values(state.plans)) {
      const schedule = state.schedules[plan.feeScheduleId];
      if (!schedule) continue;
      const mv = marketEntries.find((entry) => entry.accountId === plan.accountId);
      if (!mv) {
        continue;
      }
      const householdValue = plan.billingGroupId ? households.get(plan.billingGroupId) : undefined;
      const accrual = computeDailyAccrual({
        plan,
        schedule,
        marketValue: {
          accountId: plan.accountId,
          asOf,
          marketValue: mv.marketValue,
          cryptoMarketValue: mv.cryptoMarketValue,
        },
        householdValue,
      });
      const capViolation = enforceFeeCap({ effectiveBps: accrual.rateBps, scheduleSpec: schedule.spec });
      if (capViolation) {
        queue.enqueue({
          code: capViolation.code,
          severity: capViolation.severity,
          message: capViolation.message,
          metadata: capViolation.details,
        });
      }
      results.push(accrual);
    }

    state.accruals = state.accruals.filter(
      (existing) => new Date(existing.asOf).toISOString() !== asOf.toISOString()
    );
    state.accruals.push(...results);
    state.exceptions.push(...queue.listOpen());
    appendWorm(state, { type: "ACCRUAL_RUN", asOf: asOf.toISOString(), count: results.length });
    await saveState(state);
    console.log(`Computed ${results.length} accruals for ${asOf.toISOString().slice(0, 10)}`);
  });

program
  .command("invoices:generate")
  .description("Generate invoices for a quarter")
  .requiredOption("--period <period>", "Quarter in the form 2025Q3")
  .option("--account <id>")
  .option("--household <id>")
  .action(async (options) => {
    const state = await loadState();
    const { start, end } = parseQuarter(options.period);
    const invoices: StoredInvoice[] = [];
    for (const plan of Object.values(state.plans)) {
      if (options.account && plan.accountId !== options.account) continue;
      if (options.household && plan.billingGroupId !== options.household) continue;
      const schedule = state.schedules[plan.feeScheduleId];
      if (!schedule) continue;
      const accruals = state.accruals.filter(
        (accrual) =>
          accrual.planId === plan.id &&
          new Date(accrual.asOf) >= start &&
          new Date(accrual.asOf) <= end
      );
      if (accruals.length === 0) continue;
      const draft = generateInArrearsInvoice({
        plan,
        schedule,
        accruals,
        billingPeriodStart: start,
        billingPeriodEnd: end,
      });
      const snapshot = asInvoiceSnapshot(draft);
      const id = `INV-${randomUUID()}`;
      const stored: StoredInvoice = {
        id,
        status: "Draft",
        data: snapshot,
      };
      invoices.push(stored);
      appendWorm(state, { type: "INVOICE_GENERATED", invoiceId: id, period: options.period, amount: snapshot.amount });
    }
    state.invoices = state.invoices.filter(
      (existing) => !invoices.some((generated) => generated.data.accountId === existing.data.accountId && generated.data.billingPeriodStart === existing.data.billingPeriodStart)
    );
    state.invoices.push(...invoices);
    await saveState(state);
    console.log(`Generated ${invoices.length} invoices for ${options.period}`);
  });

program
  .command("invoices:issue")
  .description("Issue an invoice and render PDF evidence")
  .requiredOption("--id <invoiceId>")
  .action(async (options) => {
    const state = await loadState();
    const invoice = state.invoices.find((item) => item.id === options.id);
    if (!invoice) {
      throw new Error(`Invoice ${options.id} not found`);
    }
    const pdf = await renderInvoicePdf({
      billingPeriodStart: new Date(invoice.data.billingPeriodStart),
      billingPeriodEnd: new Date(invoice.data.billingPeriodEnd),
      billingGroupId: invoice.data.billingGroupId ?? undefined,
      accountId: invoice.data.accountId ?? undefined,
      currency: invoice.data.currency,
      amount: invoice.data.amount,
      lines: invoice.data.lines as any,
      minimumAppliedUSD: invoice.data.minimumAppliedUSD,
    });
    const outputDir = resolve(process.cwd(), "invoices");
    await fs.mkdir(outputDir, { recursive: true });
    const filePath = resolve(outputDir, pdf.filename);
    await fs.writeFile(filePath, pdf.buffer);
    invoice.status = "Issued";
    invoice.evidencePath = filePath;
    appendWorm(state, { type: "INVOICE_ISSUED", invoiceId: invoice.id, evidencePath: filePath });
    await saveState(state);
    console.log(`Issued invoice ${invoice.id} -> ${filePath}`);
  });

program
  .command("payments:record")
  .description("Record a payment against an invoice")
  .requiredOption("--invoice <id>")
  .requiredOption("--method <method>")
  .requiredOption("--amount <amount>")
  .option("--currency <currency>", "USD")
  .action(async (options) => {
    const state = await loadState();
    const invoice = state.invoices.find((item) => item.id === options.invoice);
    if (!invoice) {
      throw new Error(`Invoice ${options.invoice} not found`);
    }
    const amount = Number(options.amount);
    if (options.method === "CustodyDeduction") {
      const plan = Object.values(state.plans).find((p) => p.accountId === invoice.data.accountId);
      if (!plan) throw new Error("Associated plan not found for custody deduction");
      const violation = requireCustodyAuthorization({ plan, authorization: plan.custodyDeductionAllowed ? { planId: plan.id, granted: true } : null });
      if (violation) {
        appendWorm(state, { type: "PAYMENT_DENIED", invoiceId: invoice.id, violation });
        await saveState(state);
        throw new Error(violation.message);
      }
      await submitCustodyDeduction({
        plan,
        invoiceId: invoice.id,
        amount,
        currency: options.currency ?? "USD",
      });
    }
    invoice.status = amount >= invoice.data.amount ? "Paid" : "PartiallyPaid";
    appendWorm(state, { type: "PAYMENT_RECORDED", invoiceId: invoice.id, method: options.method, amount });
    await saveState(state);
    console.log(`Recorded ${options.method} payment for invoice ${invoice.id}`);
  });

program
  .command("exceptions:list")
  .description("List open compliance exceptions")
  .action(async () => {
    const state = await loadState();
    const open = state.exceptions.filter((ex) => ex.status === "Open");
    if (open.length === 0) {
      console.log("No open exceptions");
      return;
    }
    for (const exception of open) {
      console.log(`${exception.code} [${exception.severity}] -> ${exception.message ?? exception.details}`);
    }
  });

program.parseAsync();
import { Command } from "commander";
import { readFile } from "fs/promises";
import { createInMemoryDb } from "@blackroad/compliance-db";
import { gate, publishPolicy, recordAttestation } from "@blackroad/compliance-core";
import { advertising } from "@blackroad/compliance-reviewers";
import { verifyWormChain } from "@blackroad/compliance-archival";

const db = createInMemoryDb();
const program = new Command();
program.name("blackroad-compliance-os").description("Compliance OS CLI for Alexa Louise Amundson").version("0.1.0");

program
  .command("policy publish <file>")
  .description("Publish or update a policy definition")
  .action(async (file) => {
    const raw = await readFile(file, "utf-8");
    const payload = JSON.parse(raw);
    const record = await publishPolicy({
      db,
      actor: { id: "alexa", role: "admin", name: "Alexa Louise Amundson" },
      key: payload.key,
      title: payload.title,
      body: payload.body,
      controls: payload.controls ?? [],
      effectiveAt: new Date(payload.effectiveAt ?? new Date().toISOString()),
      status: payload.status ?? "Active",
    });
    console.log(`Published policy ${record.key} v${record.version}`);
  });

program
  .command("attest")
  .description("Record a policy attestation")
  .requiredOption("--policy <key>")
  .requiredOption("--user <id>")
  .requiredOption("--period <period>")
  .action(async (options) => {
    const attestation = await recordAttestation({
      db,
      policyKey: options.policy,
      userId: options.user,
      period: options.period,
      answers: { attestedAt: new Date().toISOString() },
    });
    console.log(`Recorded attestation ${attestation.id}`);
  });

const review = program.command("review").description("Run a review workflow");

review
  .command("advertising")
  .requiredOption("--in <file>")
  .option("--meta <file>")
  .action(async (opts) => {
    const content = await readFile(opts.in, "utf-8").catch(() => "");
    const meta = opts.meta ? JSON.parse(await readFile(opts.meta, "utf-8")) : {};
    const reviewResult = await advertising.runReview(db, {
      title: meta.title ?? opts.in,
      contentUrl: opts.in,
      content,
      containsPerformance: meta.containsPerformance,
      performancePeriods: meta.performancePeriods,
      containsTestimonials: meta.containsTestimonials,
      disclosures: meta.disclosures,
      cta: meta.cta,
      hypothetical: meta.hypothetical,
      thirdPartyRatings: meta.thirdPartyRatings,
    });
    console.log(JSON.stringify({
      reviewId: reviewResult.review.id,
      outcome: reviewResult.outcome,
      breaches: reviewResult.aggregate.breaches,
      riskScore: reviewResult.aggregate.riskScore,
    }, null, 2));
  });

review
  .command("aml")
  .requiredOption("--in <file>")
  .action(async () => {
    console.log("TODO: Implement AML review. Escalate to compliance officer.");
  });

program
  .command("gate <action>")
  .option("--state <state>")
  .option("--ce-complete")
  .action(async (action, options) => {
    const result = await gate(db, action, {
      state: options.state,
      ceCompleted: options.ceComplete ?? true,
    });
    console.log(JSON.stringify(result, null, 2));
  });

program
  .command("calendar list")
  .option("--open", "Only show open items")
  .action(async (options) => {
    const items = await db.calendar.listOpen();
    console.table(
      items.filter((item) => (options.open ? item.status === "Open" : true)).map((item) => ({
        id: item.id,
        key: item.key,
        due: item.due.toISOString(),
        status: item.status,
      }))
    );
  });

program
  .command("worm verify")
  .action(async () => {
    const result = await verifyWormChain(db);
    if (result.ok) {
      console.log("WORM chain verified");
    } else {
      console.error("WORM verification failed", result.issues);
      process.exitCode = 1;
    }
  });

program
  .command("audit export")
  .requiredOption("--out <file>")
  .action(async (options) => {
    console.log(`TODO: generate audit export at ${options.out}`);
  });

program.parseAsync(process.argv);
