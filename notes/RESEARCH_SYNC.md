# Research sync — team handoff

_Updated 2026-09-08 04:25Z_ · both lanes · dispatched=False

> **For:** peer orchestrator, cursor-agent, automation_improve, full 8-worker team.
> Efficiency + output research run **synchronously** each cycle.

## Efficiency lane (speed × yield)

- **[high]** Hub improve-log path targeted scandir+TTL (L75) — path **~17→2.3ms** / HIT **0.001ms**; factory remiss **~35→~8ms**; next: git snapshot ~8ms or Active noop-break
- **[done]** Hub `_queue_md_index` (L74) — orphan remiss **~0.46→0.0003ms**; phased/sync share memo
- **[done]** Hub FIND_LATEST_ROOT_FP_GENERATION (L73) — past wall TTL find_latest **30.55→0.089ms** on 17k dirs
- **[done]** Hub LOG_TAIL_SEEK re-land (L72) — improve-loop.log **46MB** full-read **324→0.094ms**; factory remiss **~125→37.8ms**
- **[done]** Hub SCAN_BOTTLENECKS_TTL (L71) — scan remiss **220.7→0.001ms** + PROBE_TTL 2→30

## Output lane (monster factory)

- **[medium]** Factory progress below self-sufficient target — ./scripts/peer progress

## Executable enqueue (improve + peer)

- (none this cycle)

## Team instructions

1. **Orchestrator** — read this file + lane digests before Phase 1 Plan.
2. **Factory Engineer** — implement efficiency findings (hot path, queue, pre-dispatch).
3. **OSS Integration Architect** — implement output findings (external proof, PR).
4. **Queue Steward** — ensure enqueued `[efficiency-research]` / `[output-research]` items stay executable.
5. **Improve loop** — `./scripts/peer improve --write --research` consumes sync on next tick.

## Linked digests

- Efficiency: `notes/EFFICIENCY_RESEARCH.md`
- Output: `notes/OUTPUT_RESEARCH.md`
- Industry trends: `notes/AUTOMATION_TRENDS.md`

