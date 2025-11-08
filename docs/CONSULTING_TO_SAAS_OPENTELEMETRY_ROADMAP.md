# 90-Day Roadmap — Consulting → SaaS with OpenTelemetry (Prism Console)

**Author:** Alexa Louise / BlackRoad — Nov 8, 2025  
**Goal:** Stay independent. Monetize now via consulting, stand up SaaS in parallel, and use **OpenTelemetry** as our moat for proof, safety, and scale.

---

## North Stars (Non-Negotiables)

- **Never sell the company.** Build durable cashflow + defensible IP.
- **Verifiable autonomy.** Every claim is backed by traces, metrics, and artifacts.
- **Safety first.** “Refusals avoided” and consent/covenant checks as first-class signals.
- **Regulated-ready.** NIST AI RMF mapping, DPA/MSA ready, audit trails.

---

## Timeline (Weeks & Dates)

- **W1:** Nov 10–16, 2025
- **W2:** Nov 17–23, 2025
- **W3:** Nov 24–30, 2025
- **W4:** Dec 1–7, 2025
- **W5:** Dec 8–14, 2025
- **W6:** Dec 15–21, 2025
- **W7:** Dec 22–28, 2025
- **W8:** Dec 29, 2025 – Jan 4, 2026
- **W9:** Jan 5–11, 2026
- **W10:** Jan 12–18, 2026
- **W11:** Jan 19–25, 2026
- **W12:** Jan 26 – Feb 1, 2026
- **W13:** Feb 2–8, 2026

> Holiday note: W7–W8 assume reduced velocity; bias to infra and content.

---

## Workstreams (Overview)

1. **Consulting GTM** — $50K/engagement: inventory → deploy → train → policies.
2. **SaaS Productization** — multi-tenant Prism Console with Stripe checkout.
3. **OpenTelemetry & Observability** — traces/metrics/logs with privacy & sampling.
4. **Safety & Compliance** — NIST RMF ops templates, DPA/MSA, DPIA, audit trails.
5. **Content & Sales** — 3-min demo video, receipts deck, case studies, sequences.
6. **Licensing Ready** — package quantum eval + refusals metric for non-exclusive licenses.

---

## Week-by-Week Plan (Deliverables & Acceptance)

### W1 — Kickoff & Pipeline

**Deliverables**

- Finalize **ICP** (financial services, health tech, gov contractors; 5–50 agents).
- Publish **pricing**: Starter $500/mo, Pro $2.5K/mo, Enterprise $10K+ (SaaS).
- Record **3-min demo** per Slide 5 (registry → admissions → vitals → quantum → polyglot).
- **Sales assets**: 2 outreach emails (Safety/Infra), 1-pager PDF, update README top.

**Acceptance**: Video link, README updated, mail-merge ready CSV of 50 leads.

---

### W2 — OpenTelemetry Foundation (Server + Agents)

**Deliverables**

- Add **global trace context** to Prism event bus; propagate `traceparent` through Registry → Admissions → Vitals → Agents.
- Instrument **server** (Fastify) for HTTP, routes: `/events`, `/traces`, `/policy`, `/vitals`.
- Instrument **agents**: create spans for `agent.load`, `agent.plan`, `agent.invoke_llm`, `agent.apply_diff`, `agent.commit`.
- Define **custom semconv**: `prism.*` attributes (see below).
- Stand up **OTel Collector** (docker-compose) exporting to **Tempo (traces)**, **Prometheus (metrics)**, **Loki (logs)**.

**Acceptance**: Clicking a demo run shows a trace from admissions → vitals with LLM spans; Prometheus exposes counters; logs include `trace_id`.

---

### W3 — OpenTelemetry Web + Quantum + Privacy

**Deliverables**

- **Web (Next.js)**: add server-side spans for API routes and propagate `traceparent` to the browser (optional web SDK for fetch/doc load).
- **QLM Lab**: wrap CHSH test in a span; emit metric `quantum.chsh.value` + artifact link.
- **Privacy guardrails**: PII redaction stage in Collector; sampling rules (keep errors/refusals); 30-day retention policy.

**Acceptance**: Traces include web→server linkage; CHSH run appears with value + artifact URL; data-handling note in docs.

---

### W4 — SaaS Alpha (Billing + Tenancy)

**Deliverables**

- Stripe checkout: Starter/Pro tiers; webhook to create **tenant/org** + API key.
- Multi-tenant data separation (org id in all resource keys; RBAC: owner/admin/viewer).
- Admin: invite users, rotate org tokens, usage page (agents, spans/day, storage).

**Acceptance**: Self-serve signup creates an org; demo tenant can log in, see only their data; Stripe test mode charges.

---

### W5 — Pilot #1 (Consulting) & Vitals Expansion

**Deliverables**

- Close **Pilot Client #1** (FS or healthtech). SOW: inventory, deploy, train, policies.
- Add vitals: `policy_hits`, `latency_ms_p50/p95`, `error_rate`, `refusals_per_1k_calls`.
- Nightly **Quantum job** with trendline panel.

**Acceptance**: Pilot invoice sent; vitals chart shows 7-day trends; quantum trend page live.

---

### W6 — Compliance Pack v1

**Deliverables**

- Publish **NIST AI RMF** mapping (GOVERN/MAP/MEASURE/MANAGE) as living doc.
- Templates: **DPA**, **MSA**, **SLA**, **DPIA**, **Incident PR** (risk/trace blocks).
- SOC2 prep: asset inventory, access reviews, log retention, secure SDLC doc.

**Acceptance**: Contracts ready for redline; RMF doc links to product surfaces; SOC2 checklist started.

---

### W7 — Holidays Infra Sprint (Sampling & Cost)

**Deliverables**

- Tail-based sampling rules: keep spans where `prism.safety.refusal=true` or status>=error; sample 5–10% of the rest.
- Token/latency **budgets** per org; enforce via policy with alerts.
- Cost dashboard: span volume, storage, tokens → $/org.

**Acceptance**: Sampling verifies; budget breach triggers alert; finance view exported as CSV.

---

### W8 — Open Core Cut & Docs

**Deliverables**

- Split **open core** repo (registry + basic vitals + minimal traces).
- Keep enterprise features paid: quantum lab, advanced compliance, SSO, long-term audit.
- Contributor guide + demo dataset + quickstart.

**Acceptance**: Public repo builds; demo runs work; website page explains tiers.

---

### W9 — Pilot #2 and Case Study #1

**Deliverables**

- Close **Pilot #2** (gov contractor or vendor with 10–50 agents).
- Publish **Case Study #1**: baseline → after (trust↑, refusals↑, incidents↓, time-to-mitigation↓).
- Add **tenant-level exports** (NDJSON traces, CSV vitals).

**Acceptance**: Signed SOW; case study PDF; export command documented.

---

### W10 — SaaS Beta & SSO

**Deliverables**

- Beta label: invite-only orgs.
- Add **SSO (SAML/OIDC)** for Enterprise.
- Usage-based overages for span volume / artifact storage.

**Acceptance**: Enterprise tenant logs in via SSO; billing shows overage.

---

### W11 — Licensing Pack

**Deliverables**

- **Licensing kit**: quantum eval SDK (client lib + schema), refusals metric spec, sample dashboards.
- Pricing: non-exclusive $100–250K/yr/org; rev-share option.
- Target list + outreach email for research/defense labs.

**Acceptance**: SDK published privately; two outreach threads started.

---

### W12 — Training & Certification

**Deliverables**

- Course outlines: **Agent Safety Fundamentals**, **Quantum Evaluation**, **NIST AI RMF in Practice**.
- 30-question certification exam draft + lab exercises.
- Landing page with waitlist.

**Acceptance**: Syllabi + exam v1 complete; 50+ signups on waitlist.

---

### W13 — Launch Week & Metrics Review

**Deliverables**

- Public SaaS waitlist → paid conversions for Starter/Pro.
- Two live webinars (demo + safety deep dive).
- Board-style review: revenue, pilots, span volume, SNR, refusal deltas, churn.

**Acceptance**: First 10 paid tenants, 2 webinars recorded, KPI doc filed.

---

## OpenTelemetry Blueprint (Prism SemConv)

### Span Model (Core)

- `prism.admissions.check` — attributes: `prism.org.id`, `prism.agent.id`, `prism.covenant.list`, `prism.consent.dual=true|false`.
- `prism.vitals.compute` — `prism.vitals.trust_score`, `prism.vitals.refusals_avoided`, `prism.vitals.policy_hits`.
- `prism.agent.invoke_llm` — `llm.model`, `llm.tokens.input`, `llm.tokens.output`, `llm.stop_reason`.
- `prism.agent.apply_diff` — `git.repo`, `git.branch`, `diff.files`, `diff.hunks`, `diff.added`, `diff.removed`.
- `prism.quantum.chsh` — `quantum.chsh.value`, `quantum.shots`, `artifact.url`.
- `prism.policy.evaluate` — `policy.id`, `policy.decision=allow|deny|review`, `policy.rules.hit`.

> Always include W3C **trace context** (`traceparent`) and set `enduser.id` (hashed) when applicable.

### Metrics (Prometheus names)

- `prism_refusals_avoided_total{org,agent}` (counter)
- `prism_trust_score{org,agent}` (gauge, 0–100)
- `prism_policy_hits_total{org,policy}` (counter)
- `llm_tokens_total{org,model,type="in|out"}` (counter)
- `prism_run_latency_ms{org,stage}` (histogram)
- `quantum_chsh_value{org}` (gauge)
- `prism_error_rate{org}` (gauge)

### Logs

- Append `trace_id`, `span_id`, `org_id`, `agent_id`, `severity`, `safe_mode`.
- Redact PII before export; add `redaction.ruleset` attribute.

### Collector (minimal `otel-collector-config.yaml`)

```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:
processors:
  batch: {}
  attributes:
    actions:
      - key: user.email
        action: delete
      - key: prism.pii.*
        action: delete
  tail_sampling:
    policies:
      - name: errors-and-refusals
        type: and
        and:
          and_sub_policy:
            - type: status_code
              status_code:
                status_codes: [ERROR]
            - type: string_attribute
              string_attribute:
                key: prism.safety.refusal
                values: ["true"]
      - name: baseline-sample
        type: always_sample
exporters:
  tempo:
    endpoint: http://tempo:3200
  prometheus:
    endpoint: 0.0.0.0:9464
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, attributes, tail_sampling]
      exporters: [tempo]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [batch, attributes]
      exporters: [loki]
```

### Instrumentation Stubs (Node, Python, Web)

**Node (Fastify server)**

```ts
// apps/prism/server/src/otel.ts
import { NodeSDK } from '@opentelemetry/sdk-node'
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node'
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
import { Resource } from '@opentelemetry/resources'
import { SemanticResourceAttributes as R } from '@opentelemetry/semantic-conventions'

export const sdk = new NodeSDK({
  resource: new Resource({ [R.SERVICE_NAME]: 'prism-server' }),
  traceExporter: new OTLPTraceExporter({ url: process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT }),
  instrumentations: [getNodeAutoInstrumentations()],
})
```

```ts
// route span example
const span = tracer.startSpan('prism.vitals.compute', { attributes: { 'prism.org.id': orgId, 'prism.agent.id': agentId } })
try { /* compute vitals */ } finally { span.end() }
```

**Python (QLM Lab CHSH)**

```py
# qlm_lab/otel.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("qlm-lab")

# usage in CHSH run
with tracer.start_as_current_span("prism.quantum.chsh", attributes={"quantum.shots": shots}):
    value = run_chsh(shots)
    span = trace.get_current_span()
    span.set_attribute("quantum.chsh.value", value)
    span.set_attribute("artifact.url", artifact_url)
```

**Web (Next.js API route example)**

```ts
// apps/prism/apps/web/src/app/api/vitals/route.ts
import { context, trace } from '@opentelemetry/api'

export async function GET(req: Request) {
  const tracer = trace.getTracer('prism-web')
  return await tracer.startActiveSpan('prism.vitals.fetch', async (span) => {
    try {
      // fetch from server with incoming trace context
      const res = await fetch(process.env.PRISM_API + '/v1/vitals', { headers: { 'traceparent': trace.getSpan(context.active())?.spanContext().traceId || '' } })
      const data = await res.json()
      return Response.json(data)
    } finally { span.end() }
  })
}
```

---

## Consulting Offers (Cash Now)

1. **Agent Inventory & Risk (Week 1)** — $15K

   - Map agents, prompts, data access, policies; deliver risk matrix & telemetry plan.
2. **Deploy Prism + OTel (Weeks 2–3)** — $25K

   - Stand up console, collector, dashboards; wire refusals/trust metrics.
3. **Policy & Training (Week 4)** — $10K

   - Draft covenants, NIST mapping; run team workshop; hand over runbooks.

> Total: **$50K/client**; target 2–3 clients in first 6 weeks.

---

## SaaS Packaging (Tiers)

- **Starter ($500/mo):** up to 10 agents, basic vitals, 30-day retention.
- **Pro ($2,500/mo):** 100 agents, quantum eval, budgets/alerts, 90-day retention.
- **Enterprise ($10K+/mo):** unlimited agents, SSO, compliance suite, 1-year audit.

Overages: spans/day, artifact GB/month.

---

## Compliance Pack

- **Docs:** NIST AI RMF mapping, DPIA template, DPA, MSA/SLA, Incident PR template.
- **Controls:** access reviews, log retention, change management, secure SDLC.
- **Evidence:** OTel dashboards, quantum artifacts, policy hit logs, refusal deltas.

---

## KPIs (Scoreboard)

- **Revenue:** $150K consulting by W9; $10–25K MRR by W9–W13.
- **Telemetry:** ≥80% of agent flows traced E2E; p95 run latency; refusals↑ 20–40% where appropriate; incident MTTR↓ 50%.
- **Adoption:** 2 pilot logos; 10 paid tenants; webinar attendance 100+.

---

## Risks & Mitigations

- **Span cardinality/cost:** Tail sampling + attribute limits; nightly rollups.
- **PII exposure:** Collector redaction; hashed user ids; per-org retention.
- **Holiday slowdowns:** Front-load pilots; use W7–W8 for infra/content.

---

## Roles (Lightweight)

- **Founder/CEO (Alexa):** sales, product calls, safety/compliance messaging.
- **Eng Lead (contract):** OTel + multi-tenant plumbing.
- **Solutions (contract):** pilots, training, case studies.
- **Legal (fractional):** DPA/MSA/DPIA, SOC2 prep.

---

## Next 48 Hours (Do Now)

1. Record the **3-min demo** and update README top section.
2. Stand up **OTel Collector** (compose) and instrument server + one agent span.
3. Send **10 outreach emails** (Safety + Infra versions) with demo link + deck.
4. Schedule 3 discovery calls for Week 2.

---

*This plan keeps us independent, cash-positive, and defensible — with OpenTelemetry as the receipts engine that no one else at our stage is shipping.*
