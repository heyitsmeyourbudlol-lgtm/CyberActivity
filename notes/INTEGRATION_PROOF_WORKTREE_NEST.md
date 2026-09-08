# Integration proof — nested worktree pool explosion

**Date:** 2026-09-03  
**Role:** integration_architect  
**factory_meter_mode:** self_sufficient (hub kit flaw — not external OSS registry proof)

## Evidence (before)

- `git worktree list` showed **51** paths with ≥2 `.worktrees` segments
- `peer-31/.worktrees/` held **40** nested clones
- Root cause: `ensure_parallel_pool` / `ensure_coding_worktree` could re-root under caller `ROOT` when porcelain list failed; cwd under `.worktrees/peer-N` spawned a second pool

## Fix

- `scripts/peer_worktree.py`: pin hub via `git rev-parse --git-common-dir`; peel `.worktrees` fallback; `_refuse_nested_pool_target`; `prune_nested_pool_pollution`; `ensure_parallel_pool` always hub-anchors; `ensure-pool` CLI prunes first
- Hub SoT writeback: `/home/arnavrastogi/Automation/scripts/peer_worktree.py` + matching unittest

## Verify (after)

| Check | Result |
|-------|--------|
| `nested_pool_pollution_count()` | **0** |
| prune | found=51 removed=51 failed=0 |
| `./scripts/peer ensure-pool --count 8` | 8 paths under hub `.worktrees/peer-0..7` |
| ensure from peer-3 ROOT | still hub-anchored (1× `.worktrees`) |
| `python3 -m unittest tests.test_peer_worktree tests.test_automation -q` | OK (112) |

## Queue

- Hub `notes/WORK_QUEUE.md` + `scripts/self_improve_context.md`: **[x] Nested worktree pool explosion**
