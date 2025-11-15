# Prism Hotspots & Punch List

## Hotspot files (last 3 non-merge commits)
The table below aggregates line additions across the three most recent non-merge commits to highlight where most energy landed recently.

| Rank | File | Additions | Notes |
| --- | --- | --- | --- |
| 1 | `agents/lucidia_encompass.py` | 366 | Lucidia Encompass orchestrator with agent wiring and vote handling. |
| 2 | `agents/personas.py` | 281 | Persona catalogue enumerations powering Encompass demos. |
| 3 | `ui/prompt_cards/index.html` | 209 | Static prompt-card gallery scaffolding for Silas demos. |
| 4 | `tests/test_encompass_vote.py` | 157 | Vote tallying tests that anchor the new Encompass flow. |
| 5 | `schemas/persona_packet.json` | 119 | JSON schema for persona packets exchanged during runs. |
| 6 | `ui/lucidia_viewer/src/style.css` | 101 | Styling for the Lucidia viewer, including diff + timeline themes. |
| 7 | `ui/lucidia_viewer/src/main.js` | 96 | Viewer bootstrapper that hydrates the Lucidia client. |
| 8 | `scripts/encompass_demo.py` | 79 | Demo driver wiring Encompass flows for CLI demos. |
| 9 | `docs/LUCIDIA_ENCOMPASS.md` | 61 | Briefing notes for the Encompass starter kit. |
| 10 | `ui/prompt_cards/cards.json` | 57 | Prompt definitions backing the Silas prompt card demos. |

## Ten punch-list opportunities
1. **Teach the diff apply endpoint how to apply patches.** `apps/prism/server/api/diffs.ts` simply appends the selected hunk text into the worktree file instead of parsing unified diffs, so deletions/overwrites never happen. Wiring this route through the agents' `applyUnifiedDiff` (or similar) would unlock real edits and reduce corruption risk.
2. **Put a retention policy in front of the event store.** `apps/prism/server/store/eventStore.ts` keeps every event in memory with no cap or TTL, which will balloon process memory for long-running sessions. Adding a bounded ring buffer or persistence backend (with pruning) will keep the server healthy.
3. **Bound trace storage and expose richer queries.** `apps/prism/server/store/traceExporter.ts` keeps every span for all traces without any max entries or TTL and only serves a full dump; pagination + eviction would prevent runaway memory and give the UI incremental loading.
4. **Upgrade the execution graph layout to handle cycles and dense DAGs.** `apps/prism/apps/web/src/components/prism/Graph.tsx` assumes a clean DAG and uses a simple topological pass; cycles fall back to column `0` and overlapping nodes. Detecting cycles and spacing siblings dynamically would improve readability.
5. **Make the wizard form inputs controlled + resettable.** In `apps/prism/apps/web/src/components/prism/Wizard.tsx` the inputs never receive `value`/`checked` bindings tied to `answers`, which breaks resetting and makes default values impossible. Controlling the inputs would stabilize the UX.
6. **Present trace attributes with structure.** `apps/prism/apps/web/src/components/prism/Traces.tsx` just dumps `JSON.stringify(node.attrs)` inline, making larger payloads unreadable. A collapsible key/value renderer (with syntax highlighting) would help.
7. **Add secret toggles + value filtering to the env panel.** `apps/prism/apps/web/src/components/prism/Env.tsx` masks secrets permanently and only filters keys. Providing a "reveal once" control and matching on values would make on-call triage easier.
8. **Harden the event fetch loop against network errors.** `apps/prism/apps/web/src/state/prismStore.ts` throws on any non-OK fetch and lacks retry/backoff, so the UI can crash during transient outages. Adding exponential backoff + listener notification would make polling robust.
9. **Broaden debugger diagnostics and severity.** `apps/prism/packages/agents/src/runners/debugger.ts` only covers four regexes and returns bare strings. Enriching rules with severity levels, links, and runbook IDs will make automated triage more actionable.
10. **Teach the coder runner about `\ No newline at end of file`.** `apps/prism/packages/agents/src/runners/coder.ts` skips diff metadata lines that begin with a backslash, so patches containing the sentinel fail to apply cleanly. Recognizing and ignoring those sentinel lines will align with Git's format.
