# Integration proof — prune_excess ignores orphan peer-N dirs + empty nested .worktrees

**Date:** 2026-09-03  
**Role:** integration_architect  
**factory_meter_mode:** self_sufficient (hub kit flaw — external OSS proof deferred in CREATIVE_BACKLOG)

## Evidence (before)

- Live hub: `.worktrees/peer-20` **no `.git`**; empty `peer-1/.worktrees` and `peer-3/.worktrees`
- `git worktree list` showed only `peer-0..7` — porcelain never saw the orphan
- Needle: `list_excess_parallel_slots` (`scripts/peer_worktree.py`) iterates `list_worktrees` only; `prune_excess_parallel_pool` only `git worktree remove`s that list

## Hypothesis → fix

- After registered prune: `list_orphan_excess_dirs` rmtree `peer-N` with `N >= cap` and **no `.git`** (never floor slots / labeled trees)
- `list_empty_nested_worktree_dirs` `rmdir`s empty `peer-*/.worktrees`
- `_assert_under_pool` refuses paths outside hub pool dir

## Verify (after)

| Check | Result |
|-------|--------|
| unittest (peer-3) `test_prune_excess_reaps_orphan_dirs_and_empty_nests` + dry_run | **OK** |
| `python3 -m unittest tests.test_automation -q` peer-3 | **86 OK** |
| hub SoT `list_orphan_excess_dirs` independent PYTHONPATH | file=`/home/arnavrastogi/Automation/scripts/peer_worktree.py` |
| live inject `peer-20`/`peer-22` (no `.git`) + empty nests | pre orphans=`peer-9,peer-20,peer-22` nests=`peer-1,peer-3` |
| `./scripts/peer ensure-pool --count 8` | `orphans=3 empty_nests=2` reaped; floor skip-reset dirty |
| after independent readback | orphans=`[]` nests=`[]` floor `peer-0..7` all exist; `peer-coding` kept |
| dry_run unittest | dirs **not** deleted |

## Hub SoT writeback

- `/home/arnavrastogi/Automation/scripts/peer_worktree.py` + matching tests in `/home/arnavrastogi/Automation/tests/test_peer_worktree.py`
- Surgical patch only (did **not** overwrite hub `ensure_parallel_pool` worker_pool_size logic)

## Queue / deferral

- Flaw closed this cycle (self_sufficient — not falcon-ai external proof)
- Next OSS proof target remains deferred: `falcon-ai` then `deepseek-cursor-proxy` (CREATIVE_BACKLOG)
