# Project learning — inside-out mastery

_Updated 2026-09-08 00:27:29_ · all agents read each cycle · record via `./scripts/peer learn-record`

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

- **2026-09-07T23:40:16** `communications_engineer`: output-compare: match — ce-mcp-doc HAVE+horizon
- **2026-09-07T23:39:50** `communications_engineer`: output-compare: match — ce:vault_omit
- **2026-09-07T23:39:48** `communications_engineer`: 2026-09-07 CE: MCP REQ schema already hub-landed (mcp:<tool>); serialize ASN was NOTES ONLY — flip automation_comms_research kit_status partial→have + horizon REQ→MCP table so improve stops re-enqueue; peer-6 scripts stale (no MCP_NEED_PREFIX) — document/regenerate from hub SoT · paths: `notes/COMMS_TRENDS.md, notes/COMMS_HORIZON.md, scripts/automation_comms_research.py, scripts/automation_comms_improve.py`
- **2026-09-07T23:39:33** `communications_engineer`: 2026-09-07: COMMS_HORIZON Self-test RED was test_vault_prompt_omits_state_path — schema.caps lacked vault_omit_state_path and format_vault_block still emitted - state: paths; omit + basename empty-bus tip → −229B/3-role tip; PROTOCOL stays 1 · paths: `scripts/peer_agent_comms.py, tests/test_peer_agent_comms.py`
- **2026-09-07T17:59:45** `kit_a_to_z`: output-compare: match — kit_a_to_z false-green heal + live kit-run
- **2026-09-07T17:59:31** `kit_a_to_z`: 2026-09-07: peer-cycle f281724 clobbered heal_false_green_lock from factory_kit_run.py while PROOF stayed green; restore from pre-clobber + fix _commit_receipt recursion (must call write_receipt); kit-heal-false-green peer case; Phase4 stays red until SSH/gh — blocked_receipt ≠ green.
- **2026-09-07T17:54:24** `verify_runner`: 2026-09-07 auto-repair verify_ok=false while hub last_cycle.verify_ok=True note=continue_on_dirty: live verify-gate-quick EXIT:0 first_fail=none; assignment stale vs green stamp
- **2026-09-07T17:52:00** `queue_steward`: output-compare: match — QS cycle Staff twin + CREATIVE wrap close
- **2026-09-07T17:51:47** `queue_steward`: Hub SoT only: CREATIVE wrap compression-keep-alive was false-open after peer:226 + peer_commands PeerCommand landed; close CREATIVE not re-promote under Top10 freeze. Piping keep_alive --check to head masks fail-closed rc=1 as 0 — measure without pipe. · paths: `scripts/peer:226, notes/CREATIVE_BACKLOG.md, notes/WORK_QUEUE.md`
- **2026-09-07T17:50:25** `queue_steward`: output-compare: match — Expected and actual match exactly.
- **2026-09-07T17:50:08** `queue_steward`: 2026-09-07 QS: idle Active + keep_alive --check agents_ge_floor=false (7<8) → promote [research-speed] Staff floor twin Active (not re-confirm noop); twin-sync WQ-only factory:verify_memory [x] into scripts/self_improve_context.md; hub SoT Automation/notes+scripts
- **2026-09-07T17:24:05** `verify_runner`: output-compare: match — two-run verify-gate-quick + run_verify_commands PASS; auto-repair type=tests was soft-skip stamp
- **2026-09-07T17:23:58** `verify_runner`: 2026-09-07 auto-repair type=tests while last_cycle note=verify-gate cleared deferred soft-skip: live run_verify_commands failures=0 kind=None; peer.verify.fail can fire on soft-skip stamp — confirm with official gate before editing fixtures
- **2026-09-07T17:11:40** `queue_steward`: output-compare: match — QS promote fail-closed twin-sync
- **2026-09-07T17:11:27** `queue_steward`: Hub idle open=0: promote CREATIVE fail-closed --check (keep_alive.py:565-567 always return 0) to Active twins — do not re-confirm noop; peer-4 WQ stale invisible to sync_queue_drift (edit Automation/notes SoT) · paths: `notes/WORK_QUEUE.md, scripts/self_improve_context.md, notes/CREATIVE_BACKLOG.md, scripts/compression_keep_alive.py`
- **2026-09-07T16:47:02** `sre_release`: Staff CLEAN agents_ge_floor=false after FANOUT_TARGET=24 wave = OOM rc=-9 under swap, not dead keep-alive; heal with ram-purge first; never restart compression-keep-alive while niche agents are its cgroup children. Needle OVERSEER_RELEASE_HEALTH_WAVE58_SRE_2026_09_07
- **2026-09-07T16:46:53** `sre_release`: output-compare: match — agents_ge_floor=false soft residual until post-wave refill (documented RELEASE_HEALTH); not unexplained mismatch
- **2026-09-07T16:32:48** `qa_engineer`: fanout#15: keep_alive --check exits 0 even when agents_ge_floor=false — Staff AC is agents>=floor field not exit code; remasure before closing [x] · paths: `scripts/compression_keep_alive.py, notes/agent_vaults/qa_engineer/SMOKE_COMPRESSION_KEEP_ALIVE.md`
- **2026-09-07T16:32:47** `qa_engineer`: output-compare: match — qa-fanout15-match
- **2026-09-07T16:32:39** `qa_engineer`: keep_alive --check always exits 0 (compression_keep_alive.py:551-553) even when agents_ge_floor=false (:523); Staff AC is agents>=floor remasure not rc — fail-closed reopen Staff + ASN SRE · paths: `scripts/compression_keep_alive.py, notes/agent_vaults/qa_engineer/SMOKE_COMPRESSION_KEEP_ALIVE.md`

## Niche mastery goals

### Adapt Specialist
- Master: automation_adapt probe/heal/audit + profiles/local.json fingerprint.
- Master: repos/registry.json status fields and should_re_adapt().

_Recent:_
- peer-4 self-heal: Linux critical daemon false-alarms from launchctl-only probe; use systemd peer-loop.service/improve-lo
- Deferred/offline-mac registry rows with no on-disk path must not hide Linux checkouts: _registry_factory_gaps skipped al
- output-compare: match — battery proof + lean hub verify · hits=2 · hits=2 · hits=2 · hits=2 · hits=2

### Command Builder
- Master: peer_commands COMMANDS + COMPOUND_STEPS registry pattern.
- Master: which shell loops in logs repeat → compound candidates.

_Recent:_
- Restored adapt-stale-clear=adapt→audit→adapt-confirm on hub after 4k-line peer_commands truncate; needle COMPOUND_STEPS+
- Wrapped compression_keep_alive.py --check as ./scripts/peer compression-keep-alive (pivotal). Coverage top gap; forever 
- output-compare: match — compression-keep-alive wrap

### Communications Engineer
- Master: GLink message types, vault summary caps, bus append hot path.
- Master: automation_comms_improve verify gate and encoding options.

_Recent:_
- 2026-09-07 CE: MCP REQ schema already hub-landed (mcp:<tool>); serialize ASN was NOTES ONLY — flip automation_comms_rese
- output-compare: match — ce:vault_omit
- output-compare: match — ce-mcp-doc HAVE+horizon

### Compression Engineer
- Master: measure_live_state RSS path + daemon memory in peer/improve loops.
- Master: test_cache_ttl, quick vs full measure tradeoffs.

_Recent:_
- output-compare: match — exact match after measure · hits=2 · hits=2 · hits=2 · hits=2 · hits=2
- output-compare: discrepancy — compression reclaim after sparse cold + unload · hits=2 · hits=2 · hits=2 · hits=2 · hits=
- peer_loop RSS blew to 65GB because cold memory hybrid retrieve loaded mamba-790m into the forever process; fix=retrieve(

### Debrief Optimizer
- Master: DEBRIEF_LOG + peer_debrief kinds (aar/knowledge).
- Learn: convert one debrief into playbook or executable queue item.

### Efficiency Researcher
- Master: probe_efficiency findings and EFFICIENCY_RESEARCH agent notes format.
- Master: pre-dispatch, wake interval, noop-break interactions.

_Recent:_
- output-compare: match — OVERSEER_TRANSCRIPT_PATHS_CACHE_2026_09_07 final
- output-compare: match — OVERSEER_TRANSCRIPT_PATHS_CACHE_2026_09_07 scandir
- find_latest cold miss: Path.iterdir+max 169ms → os.scandir+os.stat one-pass ~31.6ms (~5.3×) on 17751 UUID dirs; keep TTL

### Factory Engineer
- Master: peer_loop → orchestrate → parallel_dispatch dispatch path end-to-end.
- Master: worktree pool (peer_worktree), continue_on_dirty, post-agent verify.
- Learn: factory_progress dimensions — what moves self_sufficient %.

_Recent:_
- Deferred soft-skip: record_cycle_outcome(failure_type=deferred, verify_ok=False) + format Verify:deferred(soft-skip); hy
- output-compare: match — deferred soft-skip port · hits=2 · hits=2 · hits=2 · hits=2 · hits=2
- Lock-held verify must return (-1,deferred) not (0,None): false verify_ok auto-commits and arms noop fp loops. Inject fai

### Integration Architect
- Master: registry → adapt → worktree → native verify → proof artifact chain.
- Master: factory_meter_mode deferral of external proof in self_sufficient mode.

_Recent:_
- needle: dual-research-findings.json item 5cde9ba441123ba5 (status=enqueued) kept re-hand_out Newdrop needs-kit ASN after
- needle: live factory reads hub ROOT registry — peer-3 adapt-verified-dgx never cleared vault ASN; writeback hub status+p
- needle: hub queue_fp is peer_transcript.current_queue_fingerprint on Automation ROOT — worktree [x] on Newdrop never mov

### Lessons Curator
- Master: peer_lessons harvest → squeeze → promote; facts_preserved=true.
- Master: memory journal + PROJECT_LEARNING + playbook as SoT — no parallel stores.
- Learn: squeeze unique store (dedupe/fold); never prune distinct needles.

### Output Researcher
- Master: probe_output + OUTPUT_RESEARCH; RESEARCH_SYNC handoff rules.
- Master: registry ready vs gap repos — when to defer in self_sufficient mode.

_Recent:_
- Wave-53: npm pin = dist.integrity sha512 MATCH + /-/npm/v1/attestations publish/v0.1 + SLSA provenance v1 workflow bind;
- output-compare: match — Expected and actual match exactly.
- Go sumdb h1 dirhash must hash FULL zip paths (module@version/...), not stripped paths — strip yields MISMATCH; go.mod al

### Pen Test Researcher
- Master: peer_pen_test scan patterns + PEN_TEST agent notes — defensive harden only.
- Master: product-forge target preferred; never exploit PoCs.

### Queue Steward
- Master: open_work_items sources (launch vs context) and sync_queue_drift.
- Master: theater markers vs factory-shaped queue lines.

_Recent:_
- output-compare: match — Expected and actual match exactly.
- Hub SoT only: CREATIVE wrap compression-keep-alive was false-open after peer:226 + peer_commands PeerCommand landed; clo
- output-compare: match — QS cycle Staff twin + CREATIVE wrap close

### Safety Auditor
- Master: SAFETY_GATES.md tiers (green/yellow/red) and veto workflow.
- Master: flaw-scan scanner persona — 7 reviews per subject niche.

_Recent:_
- TTL-skip ensure on dir-existence alone is unsafe: ensure_parallel_pool owns prune_nested(force)+prune_excess; hub live e

### Verify Runner
- Master: peer_tasks verify_commands + run_peer_tasks.py exit codes.
- Master: verify-gate-quick vs full unittest — when each runs.
- Learn: classify failures — test vs import vs lock vs timeout storm.

_Recent:_
- 2026-09-07 auto-repair type=tests while last_cycle note=verify-gate cleared deferred soft-skip: live run_verify_commands
- output-compare: match — two-run verify-gate-quick + run_verify_commands PASS; auto-repair type=tests was soft-skip stamp
- 2026-09-07 auto-repair verify_ok=false while hub last_cycle.verify_ok=True note=continue_on_dirty: live verify-gate-quic

## Debrief peek

## 2026-09-01T10:56:21 — POSTMORTEM: Verify failure — unknown
## 2026-09-01T10:57:01 — POSTMORTEM: Verify failure — self-check
## 2026-09-01T11:07:27 — FLAW_TRIAGE: Flaw scan round 2026-09-01
- **Factory Engineer:** Auto ensure-pool when count < worker_target
- **Factory Engineer:** Run verify gate scoped to worktree cwd before merge
- **Factory Engineer:** Tag worktree slots with registry namespace for OSS handoff
- **Factory Engineer:** Yellow-tier safety gate before foreign-repo worktree add
- **Verify Runner:** Parallelize independent verify_commands with fail-fast
