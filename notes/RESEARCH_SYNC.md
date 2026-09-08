# Research sync — team handoff

_Updated 2026-09-08 02:56:00Z_ · both lanes · dispatched=False

> **For:** peer orchestrator, cursor-agent, automation_improve, full 8-worker team.
> Efficiency + output research run **synchronously** each cycle.

## Efficiency lane (speed × yield)

- **[critical]** Verify gate blocking dispatch — ./scripts/peer heal-all — fix verify before next agent dispatch

## Output lane (monster factory)

- **[closed]** Prove improve→peer closed loop — CLEAN self_sufficiency=1.0 · wake peer fresh · high=0 med=0 · factory pct=99 · NO PAY

## Executable enqueue (improve + peer)

- _(none from output-research — improve→peer proven CLOSED)_

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

