# Project learning — inside-out mastery

_Updated 2026-09-08 00:12:14_ · all agents read each cycle · record via `./scripts/peer learn-record`

**Learn as you work** — cumulative inside-out mastery (every cycle):

1. **Read before Plan** — `notes/PROJECT_LEARNING.md` + your niche notes in vault; never re-discover documented facts.
2. **Trace before edit** — follow imports/callers in your scope until you can explain the data flow in one paragraph.
3. **Record after work** — append ONE dated learning (non-obvious insight, trap, or file map) via `./scripts/peer learn-record`.
4. **Improve the kit** — mistake patterns → `notes/AGENT_ERROR_PLAYBOOK.md`; process wins → `notes/DEBRIEF_LOG.md` or SOP.
5. **Deepen over time** — each cycle you should know more of the repo than last cycle; teach the team in shared learnings.

## Inside-out map

- `scripts/peer_loop.py` (✓) — Forever driver — dispatch, verify gate, noop, worktrees
- `scripts/peer_orchestrate.py` (✓) — Orchestrator plan — phase gates, Task peer tasks
- `scripts/automation_improve.py` (✓) — Improve forever — horizon, enqueue, hand_out
- `scripts/automation_team.py` (✓) — Improve ↔ peer bridge — worker pool, team gaps
- `scripts/peer_team_context.py` (✓) — Shared brain — TEAM_CONTEXT, team-sync, cycle_id
- `scripts/peer_persona_rules.py` (✓) — Hardwired MUST/MUST NOT per niche
- `scripts/peer_agent_comms.py` (✓) — GLink bus + vaults + per-agent notes.jsonl
- `scripts/peer_critical_thinking.py` (✓) — Intelligence layer — evidence, root cause, Plan/Act gates
- `notes/CRITICAL_THINKING.md` (✓) — Critical thinking canon — read before Plan
- `scripts/peer_hallucination_guard.py` (✓) — Hallucination guard — self-aware strategy to defy drift
- `notes/HALLUCINATION_GUARD.md` (✓) — Assume hallucination soon — strategize before edit
- `scripts/peer_agent_human_gap.py` (✓) — Agent vs human — gap matrix + countermeasures
- `notes/AGENT_VS_HUMAN.md` (✓) — 20 agent weaknesses vs humans — kit fix per row
- `scripts/peer_idea_synthesis.py` (✓) — Grounded idea synthesis — novelty from current knowledge
- `notes/IDEA_SYNTHESIS.md` (✓) — Articulate new ideas with ≥2 anchors — not chat fantasy
- `scripts/peer_agent_gates.py` (✓) — Executable plan-gate + done-gate for all 20 gaps
- `notes/AGENT_GATES.md` (✓) — Run plan-gate before edit; done-gate before DONE
- `scripts/peer_precision_habits.py` (✓) — Precision habits — needle-in-a-haystack for all model tiers
- `notes/PRECISION_HABITS.md` (✓) — Surgical accuracy canon — read before first edit
- `scripts/peer_output_compare.py` (✓) — Expected vs actual output — discrepancy check before DONE
- `notes/OUTPUT_COMPARE.md` (✓) — Output compare canon — expected vs actual side-by-side
- `scripts/peer_agent_mini_apps.py` (✓) — Mini apps — self-built agent tools when repetition hurts
- `notes/AGENT_MINI_APPS.md` (✓) — Mini app charter — scaffold, test, register, promote
- `scripts/agent_tools/` (missing) — Directory for agent-built single-purpose scripts
- `scripts/peer_self_diagnose.py` (✓) — Self-diagnosis — errors, miscalculations, poor logic
- `notes/SELF_DIAGNOSE.md` (✓) — Diagnose canon — instant scan before Plan
- `notes/AGENT_SURVIVAL.md` (✓) — Hazard map — stalls, chicken-eggs, false labels (read every cycle)
- `scripts/peer_agent_survival.py` (✓) — Inject survival briefing into every persona prompt
- `notes/AGENT_ERROR_PLAYBOOK.md` (✓) — Symptom → mechanical fix catalog
- `scripts/peer_playbook.py` (✓) — Playbook match + sync AGENT_ERROR_PLAYBOOK.md
- `scripts/peer_work_assign.py` (✓) — Peer assignment — ETA vs cursor-agent deadline, GLink ASN
- `notes/WORK_ASSIGN.md` (✓) — Assignment canon — assign, eta, when=now|later|miss
- `scripts/peer_memory_span.py` (✓) — Memory span — 100x tiered external memory (hot/warm/cold)
- `notes/MEMORY_SPAN.md` (✓) — Memory canon — journal, retrieve, tier budgets
- `scripts/peer_lessons.py` (✓) — Lessons curator — harvest + lossless squeeze (facts_preserved)
- `scripts/peer_roles.py` (✓) — Job titles — assign_worker_pool, L-shards
- `scripts/peer_tasks.json` (✓) — agent_roles, templates, verify_commands
- `scripts/project_automation.py` (✓) — Config, live state, queue, factory_meter_mode
- `scripts/factory_progress.py` (✓) — Self-sufficient / external-proof readiness meter
- `scripts/peer_dual_research.py` (✓) — Efficiency + output research lanes
- `notes/TEAM_CONTEXT.md` (✓) — Live team snapshot — read every cycle
- `scripts/peer_agent_gates.py` (✓) — Plan-gate + done-gate — executable countermeasures
- `notes/AGENT_GATES.md` (✓) — Run plan-gate before edit; done-gate before DONE
- `scripts/peer_commands.py` (✓) — Agent CLI registry — compound recipes
- `scripts/peer_parallel_dispatch.py` (✓) — Parallel cursor-agent niche dispatch
- `scripts/peer_transcript.py` (✓) — Transcript → next prompt + last_cycle
- `scripts/cursor_self_improve.py` (✓) — Paste/dispatch bridge to orchestrator
- `scripts/peer_command_builder.py` (✓) — Command Builder agent prompt + digest
- `notes/WORK_QUEUE.md` (✓) — Executable queue (sync with self_improve_context)
- `notes/OPERATING_SYSTEM.md` (✓) — Debrief + flaw scan + optimization pillars
- `AGENTS.md` (✓) — Operator preferences and verify commands

## Recent team learnings

_No learnings recorded yet — agents append via learn-record each cycle._

## Niche mastery goals

### Adapt Specialist
- Master: automation_adapt probe/heal/audit + profiles/local.json fingerprint.
- Master: repos/registry.json status fields and should_re_adapt().

### Command Builder
- Master: peer_commands COMMANDS + COMPOUND_STEPS registry pattern.
- Master: which shell loops in logs repeat → compound candidates.

### Communications Engineer
- Master: GLink message types, vault summary caps, bus append hot path.
- Master: automation_comms_improve verify gate and encoding options.

### Compression Engineer
- Master: measure_live_state RSS path + daemon memory in peer/improve loops.
- Master: test_cache_ttl, quick vs full measure tradeoffs.

### Debrief Optimizer
- Master: DEBRIEF_LOG + peer_debrief kinds (aar/knowledge).
- Learn: convert one debrief into playbook or executable queue item.

### Efficiency Researcher
- Master: probe_efficiency findings and EFFICIENCY_RESEARCH agent notes format.
- Master: pre-dispatch, wake interval, noop-break interactions.

### Factory Engineer
- Master: peer_loop → orchestrate → parallel_dispatch dispatch path end-to-end.
- Master: worktree pool (peer_worktree), continue_on_dirty, post-agent verify.
- Learn: factory_progress dimensions — what moves self_sufficient %.

### Integration Architect
- Master: registry → adapt → worktree → native verify → proof artifact chain.
- Master: factory_meter_mode deferral of external proof in self_sufficient mode.

### Lessons Curator
- Master: peer_lessons harvest → squeeze → promote; facts_preserved=true.
- Master: memory journal + PROJECT_LEARNING + playbook as SoT — no parallel stores.
- Learn: squeeze unique store (dedupe/fold); never prune distinct needles.

### Output Researcher
- Master: probe_output + OUTPUT_RESEARCH; RESEARCH_SYNC handoff rules.
- Master: registry ready vs gap repos — when to defer in self_sufficient mode.

### Pen Test Researcher
- Master: peer_pen_test scan patterns + PEN_TEST agent notes — defensive harden only.
- Master: product-forge target preferred; never exploit PoCs.

### Queue Steward
- Master: open_work_items sources (launch vs context) and sync_queue_drift.
- Master: theater markers vs factory-shaped queue lines.

### Safety Auditor
- Master: SAFETY_GATES.md tiers (green/yellow/red) and veto workflow.
- Master: flaw-scan scanner persona — 7 reviews per subject niche.

### Verify Runner
- Master: peer_tasks verify_commands + run_peer_tasks.py exit codes.
- Master: verify-gate-quick vs full unittest — when each runs.
- Learn: classify failures — test vs import vs lock vs timeout storm.

## Debrief peek

## 2026-09-01T10:56:21 — POSTMORTEM: Verify failure — unknown
## 2026-09-01T10:57:01 — POSTMORTEM: Verify failure — self-check
## 2026-09-01T11:07:27 — FLAW_TRIAGE: Flaw scan round 2026-09-01
- **Factory Engineer:** Auto ensure-pool when count < worker_target
- **Factory Engineer:** Run verify gate scoped to worktree cwd before merge
- **Factory Engineer:** Tag worktree slots with registry namespace for OSS handoff
- **Factory Engineer:** Yellow-tier safety gate before foreign-repo worktree add
- **Verify Runner:** Parallelize independent verify_commands with fail-fast
