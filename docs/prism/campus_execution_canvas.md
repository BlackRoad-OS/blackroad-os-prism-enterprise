# Campus Execution Canvas

This canvas distills the immediate execution plan for the Origin Campus push: boot Unity
and Unreal clients against the existing Gateway contract, stand up the initial
native-AI org, and turn the campus rules into enforceable deployment gates. It blends
the Ellis-Island campus narrative with actionable engineering, product, and operations
moves.

## 1. Gateway-Compatible Client Stubs (Unity & Unreal)

The Gateway already supports the core lifecycle events (`join`, `spawn`,
`artifact.spawn`, `pedestal.task`). The first sprint focuses on scaffolding
Unity and Unreal clients that can connect, authenticate, and mirror the campus
state for rapid iteration.

### Shared Requirements

- **Transport**: Secure WebSocket (wss) connection to the Gateway with JSON
  envelope messages. Each payload includes `type`, `payload`, and `traceId`.
- **Authentication**: Signed visitor token exchanged during `join`. Clients must
  cache the token, include it in headers for reconnects, and surface re-auth
  prompts when tokens expire.
- **State Channels**: Subscribe to `presence`, `artifact`, `parcel`, and `task`
  streams. Maintain local caches keyed by `entityId` with server-authoritative
  versions.
- **Commands**: Emit debounced intent messages (`interaction.activate`,
  `parcel.claim`, `artifact.place`) that the Gateway validates before applying.
- **Telemetry**: Buffer client metrics (latency, dropped frames, interaction
  counts) and flush on interval to the Observability squad via the Gateway
  `telemetry` route.

### Unity P1 Prompt

```
You are scaffolding a Unity 2022 LTS project named "OriginCampusClient".
Requirements:
1. Create a `GatewayClient` C# script that manages a secure WebSocket to
   wss://gateway.prism.blackroad/gateway. Handle JSON envelopes with fields
   `type`, `payload`, `traceId`, and route `join`, `spawn`, `artifact.spawn`,
   and `pedestal.task` events to strongly-typed handlers.
2. Implement `JoinSequence` that requests a visitor token via REST, upgrades to
   WebSocket, and spawns the player avatar in the Harbor. Use ScriptableObjects
   to store environment config (Gateway URL, asset bundle paths, logging level).
3. Build a `PedestalController` that sends `pedestal.task` intents when the
   player interacts with Dome pedestals. Display returned task previews and
   completion states in a UI Toolkit panel.
4. Add a lightweight `ArtifactSpawner` that listens for `artifact.spawn`
   messages and instantiates placeholder prefabs (from `Assets/Prefabs/Artifacts`)
   with lineage metadata displayed on hover.
5. Wire up a `TelemetryReporter` coroutine that batches frame time, packet RTT,
   and interaction counts every 10 seconds and posts them to the `/telemetry`
   endpoint with the visitor token.
Generate Editor scripts only when necessary; focus on runtime components. Include
unit tests using the Unity Test Framework for the JSON routing logic.
```

### Unreal P1 Prompt

```
Spin up an Unreal Engine 5.3 C++ project named "OriginCampusUE".
Goals:
1. Implement a `UGatewaySubsystem` derived from `UGameInstanceSubsystem` that
   opens a secure WebSocket to the Gateway, authenticates with the visitor token,
   and broadcasts delegates for `OnJoin`, `OnSpawn`, `OnArtifactSpawn`, and
   `OnPedestalTask`.
2. Create an `AGatewayAvatar` actor that listens for spawn updates and teleports
   the player pawn to Harbor coordinates. Include reconciliation hooks to snap
   to server-authoritative transforms when drift exceeds thresholds.
3. Build a `UPedestalInteractionComponent` that sends `pedestal.task`
   interactions with serialized pedestal IDs, listens for task result payloads,
   and triggers UMG widgets with previews and remediation states.
4. Add a `UArtifactManifestComponent` that instantiates placeholder meshes from
   `/Game/Artifacts` when `artifact.spawn` arrives, applies lineage metadata to
   tooltips, and synchronizes attachment to pedestals or parcels.
5. Integrate a `UTelemetryCollector` that logs latency, packet loss, and
   interaction counters, flushing every 10 seconds through the Gateway REST
   client.
Favor modular components, enable hot reload, and provide automated tests for the
JSON envelope parsing using Unreal's automation framework.
```

### Handoff Checklist for Codegen Agents

1. Seed both prompts into the codegen agents with the current Gateway schema.
2. Validate generated projects compile locally (Unity Test Runner, `UnrealBuildTool`).
3. Hook CI to run headless client connection smoke tests against the staging Gateway.
4. Deliver artifact bundles back to the Campus Client squad for scene dressing.

## 2. Native-AI Org Blueprint

The org grows in three pulses: 0→20, 20→50, and 50→150. Each pulse preserves
clear reporting and lightweight governance to keep the campus shippable.

### Phase 0→20: Foundational Pod

- **Mission Control (5 seats)**: Gateway lead, client integration lead, QLM
  bridge lead, product owner, operations wrangler.
- **Campus Client Pod (5 seats)**: Unity lead, Unreal lead, UX, systems designer,
  technical artist.
- **QLM Lab Pod (4 seats)**: Quantum engineer, Python services engineer, policy
  analyst, data storyteller.
- **Economy & Simulation Pod (3 seats)**: Systems economist, simulation engineer,
  reward design lead.
- **Observability & Compliance Pod (3 seats)**: Telemetry engineer, Rego policy
  engineer, incident responder.

Reporting: Mission Control reports to the Campus GM. All pods meet in a weekly
Flight Review to unblock and align.

### Phase 20→50: Scaling Pods

- Split Mission Control into **Gateway Squad** (session, ledger, evidence log)
  and **Experience Squad** (client, parcels, events).
- Stand up **Content & Origin Map Pod** (Unity world builders, signage, Blender
  importer maintainer).
- Expand Observability into **Reliability & Trust** (SLO owner, security
  liaison, ops automation).
- Add **Economy Ops** (sim data analyst, reward balancing) reporting into the
  Economy lead.
- Introduce a lightweight **People Ops steward** to handle onboarding, role
  cards, and retention rituals.

### Phase 50→150: Federated Guilds

- Formalize **Guilds** across Clients, Gateway, Data, and Policy with elected
  stewards ensuring cross-pod standards.
- Add **Marketplace & Partnerships** pod to handle third-party parcels and
  compliance reviews.
- Create **Learning & Enablement** to maintain mission briefs, run skill
  bootcamps, and certify agents/humans for critical roles.
- Expand Reliability into a 24/7 **Campus NOC** with follow-the-sun coverage and
  automated runbooks sourced from the observability squad.
- Introduce **Community Trust** to handle moderation, appeals, and artifact
  provenance escalations.

## 3. Campus Masterplan Rules & Gates

Map the campus inspiration (Ellis Island, museum districts, science campuses)
into enforceable build standards and deployment policy.

### Wayfinding & Transit

- **Rule**: Every new parcel must expose two clear sightlines to Harbor
  landmarks and one accessible route to public transit nodes.
- **OPA Gate**: Validate submitted parcel geometry includes annotated
  wayfinding markers; reject builds lacking ADA-compliant paths.
- **KPI**: Average time-to-destination for first-time visitors ≤ 90 seconds in
  pathfinding simulations.

### Green & Public Space

- **Rule**: 30% of each block reserved for open green or civic space; enforce
  tree canopy density targets.
- **OPA Gate**: Check parcel manifests for `greenspaceRatio` ≥ 0.3 and
  `canopyScore` within threshold using environmental simulation outputs.
- **KPI**: Campus comfort index ≥ 80th percentile, measured via simulated crowd
  surveys and thermal models.

### Sociability & Programming

- **Rule**: Every shipping build must schedule at least one community programming
  hook (talk, workshop, guided tour) per week of activation.
- **OPA Gate**: Reject deployment manifests without `programSchedule` entries or
  missing diversity of formats.
- **KPI**: Weekly participation rate ≥ 60% of visiting cohort; track through
  Gateway attendance logs.

### Energy & Sustainability

- **Rule**: Enforce net-positive energy simulation per block, leveraging solar
  canopies and kinetic harvesters.
- **OPA Gate**: Confirm `energyBalance` field ≥ 0 in the sustainability model.
- **KPI**: Campus energy surplus ≥ 12% month-over-month in simulation.

### Access & Inclusion

- **Rule**: All parcels must expose multi-language signage packs and sensory
  accessibility modes.
- **OPA Gate**: Validate asset bundles include required localization keys and
  haptics/audio descriptions.
- **KPI**: Accessibility satisfaction score ≥ 4.5/5 in onboarding surveys.

## 4. Immediate Plays

1. **Kick the Clients**
   - Feed the Unity and Unreal P1 prompts to codegen agents.
   - Instrument CI to smoke-test WebSocket handshake and artifact spawn flows.
   - Ship scaffolded clients to the Campus Client pod for scene integration.

2. **Stand Up Mission Pods**
   - Appoint Mission Control steward and fill pod seats using the role cards
     above.
   - Schedule the first Flight Review and publish the reporting cadence.
   - Spin up shared OKR tracker keyed to Gateway readiness, client parity, and
     policy enforcement.

3. **Campus Rules Live**
   - Encode the masterplan rules into Rego policies and add them to the Gateway
     deploy pipeline.
   - Block parcel/build deploys that fail sociability, energy, or access checks.
   - Surface compliance status dashboards in RoadView for transparency.

This canvas can be handed directly to engineering, ops, and policy teams to
accelerate execution while honoring the campus narrative and guardrails.
