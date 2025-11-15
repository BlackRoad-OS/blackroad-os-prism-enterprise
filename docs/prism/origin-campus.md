# Origin Campus Architecture

This note captures the first-pass layout for the Origin Campus experience and the
supporting systems that make the Ellis-Island metaphor work in-engine.

## Campus Flow

1. **Harbor (spawn)** – Players and agent-run PCs arrive by shuttle and are
   greeted by compliance signage plus the current build notes. Spawn kiosks
   issue a temporary visitor token tied to the next available registry pedestal.
2. **Registry Hall** – Identity stations record a short introduction, bind the
   visitor token to a campus profile, and explain rules of engagement. From
   here, visitors proceed to the Proof Wing.
3. **QLM Dome** – Pedestals fan out around the dome floor. Activating one queues
   a QLM task (Bell/CHSH demo, Grover search, code synthesis, etc.) and
   displays a deterministic preview. Successful runs mint an artifact (image or
   JSON) and stamp the visitor profile. Failed runs surface remediation tips.
4. **Sandbox Parcels** – Visa-stamped visitors can claim a parcel, place their
   artifact, and annotate it with lineage metadata. Parcel kits include simple
   structures, lighting presets, and RoadCoin reward plaques.
5. **Archive Walk** – Gallery boards surface recent artifacts, lineage chains,
   and compliance verdicts. Visitors can replay the generating task with
   provenance intact.
6. **RoadView Tower** – Search and analytics hub. Queries fan out to the
   evidence log, parcel registry, and RoadCoin ledger (simulation only) for
   dashboards and digests.

## System Split

- **Client (Unity)** – Owns presence, input, physics, UI, parcel editing, and
  local visualization of artifacts. All authoritative state comes from the
  gateway; local predictions are reconciled against server truth.
- **Authoritative Gateway (Node/TypeScript)** – Maintains player sessions,
  parcel ownership, artifact registry, and RoadCoin balances. Spawns artifacts
  when upstream services emit a signed lineage bundle. Exposes a WebSocket API
  for Unity and REST/gRPC surfaces for external tooling.
- **QLM Lab Service (Python)** – Accepts queued quantum-learning missions,
  executes deterministic demos (Bell/CHSH, Grover, phase estimation), hashes the
  outputs, and returns artifact manifests. Runs under strict policy guardrails
  (no outbound network, bounded artifact size) and reports telemetry to the
  gateway.

## Agent PCs & Task Flow

- **QLM PCs** are avatars plus a task queue. Interacting with them or with
  Dome pedestals enqueues a QLM job.
- Jobs carry lineage metadata: requester identity, policy pack versions, seed,
  and expected outcome range (e.g., CHSH S between 2.4 and 2.8).
- QLM Lab returns signed manifests (artifact URI, preview, lineage block). The
  gateway verifies signatures, stores the manifest, and instructs Unity to spawn
  the artifact at the correct pedestal or parcel.
- Failure paths include remediation hints, queue retries (bounded), and policy
  escalation if measured S-values fall outside the allowed range.

## Economy (Simulation Only)

- RoadCoin credits exist purely inside the campus simulation. They reward
  verified builds, completed lessons, or peer instruction sessions.
- The gateway mints and burns credits; no external wallet or chain integration
  is permitted in-campus. Balances reset when a profile leaves the sandbox
  unless promoted to contributor status by staff.

## Evidence & Compliance

- Every action (arrival, task queue, artifact spawn, parcel update) emits an
  append-only JSONL entry with hash chaining.
- Continuous Integration gates use Rego policies to confirm:
  - Artifacts referenced by campus state exist and are hash-matched.
  - QLM metrics (e.g., CHSH S statistic) fall within safe ranges.
  - Test coverage and secret scans meet the configured thresholds.
- Audit dashboards in RoadView consume these logs to display lineage proof,
  error spikes, and compliance posture.

## Modding Path

- Contributors import Blender assets through a lightweight Unity importer that
  enforces scale/origin conventions and tags bundles for parcel placement.
- Parcel kits expose scripted hooks so agent PCs can annotate, repair, or
  extend community-built structures without overwriting creator intent.
- Agent-authored improvements run through the same artifact/lineage pipeline,
  ensuring parity between human and agent contributions.

## Parallel Prompt Tracks

1. **Unity Foundations** – Input, locomotion, camera, and core campus scaffold.
2. **Gateway & Persistence** – Node/TypeScript service, session handling,
   artifact registry, RoadCoin ledger, and hash-chained logs.
3. **QLM Bridge** – Task queue, gRPC/REST contract, artifact verification,
   lineage payloads, and policy integration.
4. **Parcels & Economy (Sim)** – Parcel claim flow, placement tools, simulated
   RoadCoin rules, and staff moderation hooks.
5. **Observability / Policy / CI** – Rego gates, coverage enforcement, telemetry
   export, dashboards, and incident loops.
6. **Content Pipeline & Origin Map** – Blender→Unity importer, parcel kits,
   signage, and the first-pass campus map described above.

These tracks advance in parallel but handshake through the authoritative
gateway and the append-only evidence log to keep campus truth synchronized.
