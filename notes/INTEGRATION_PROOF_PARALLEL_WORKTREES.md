# Integration proof — parallel worktrees spawn helper (trend have)

**Date:** 2026-09-04  
**Role:** integration_architect · peer-5  
**factory_meter_mode:** `self_sufficient` (hub kit status — external OSS deferred CREATIVE_BACKLOG)

## Assignment

`Parallel agents via git worktrees` — Add optional worktree spawn helper for parallel peer tasks (divide-and-conquer).

## Ground truth

| Probe | Result |
|-------|--------|
| `notes/WORK_QUEUE.md:166` | already `[x]` — shipped `peer_worktree` + `ensure-pool` |
| `scripts/peer_worktree.py:990` `spawn_parallel_worktree` | present |
| `./scripts/peer ensure-pool --count 8` | `ok: 8 worktree(s) ready` EXIT 0 |
| dry_run `spawn(47)` | `RuntimeError: refuse slot 47 outside [0, 8)` |
| SpawnSlotCapTests + SpawnParallelWorktreeTests | 8 OK |
| Root cause of Launch re-hand | `automation_research.CURATED_TRENDS` `parallel_worktrees` still `kit_status="partial"` → improve enqueues `[trend]` |

## Fix (this cycle)

- `scripts/automation_research.py` — `parallel_worktrees` `kit_status` `partial` → `have`; opportunity text documents shipped helper
- `notes/AUTOMATION_TRENDS.{json,md}` rewritten via `automation_research.py --write` (partial count 3→2; theme absent from actionable kit map)
- Hub writeback of research SoT + trends; T+8 sticky check
- Registry Hub notes + this proof

## Falsifier (would reopen)

- `trends_to_opportunities` includes `parallel_worktrees`, or
- `./scripts/peer ensure-pool --count 8` fails / pool < 8, or
- `spawn_parallel_worktree(47)` does not refuse

## Deferral

External Newdrop/falcon/deepseek proof remains deferred under `self_sufficient` → `notes/CREATIVE_BACKLOG.md`.
