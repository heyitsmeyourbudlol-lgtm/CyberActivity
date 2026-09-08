# Integration proof — excess parallel pool never retires dirty slots

**Date:** 2026-09-03  
**Role:** integration_architect  
**factory_meter_mode:** self_sufficient (hub kit flaw — external OSS proof deferred in CREATIVE_BACKLOG)

## Evidence (before)

- Live hub pool: **40** excess numbered slots (`peer-8`…`peer-47`) with `max_parallel_peers=8`
- `prune_excess_parallel_pool` called `remove_worktree` **without** `force=True` (`scripts/peer_worktree.py` ~477)
- Needle confirm: `git worktree remove …/peer-40` → `contains modified or untracked files, use --force to delete it` → **0 retired**

## Hypothesis → fix

- Same root cause as nested prune: dirty trees stick forever unless `git worktree remove --force`
- Default `force=True` on `prune_excess_parallel_pool` (CLI `remove` stays force-off)
- Canonical `peer-0..7` never listed by `list_excess_parallel_slots`

## Verify (after)

| Check | Result |
|-------|--------|
| excess before | **40** |
| `./scripts/peer ensure-pool --count 8` | `excess slots found=40 removed=40 failed=0 (cap 8)` + `--force` log per slot |
| excess after (hub PYTHONPATH) | **0** |
| second ensure-pool | no excess prune lines; `ok: 8 worktree(s)` |
| unittest force default | `test_prune_excess_parallel_pool_defaults_force` OK |
| `python3 -m unittest tests.test_automation -q` | **85 OK** |

## Hub SoT writeback

- `/home/arnavrastogi/Automation/scripts/peer_worktree.py` + matching unittest (ensure-pool / peer_loop use `HUB_ROOT`)
- Independent readback: `list_excess_parallel_slots(cap=8)` → `[]`; signature `force` default `True`

## Queue / deferral

- Flaw closed this cycle (self_sufficient — not falcon-ai external proof)
- Next OSS proof target remains deferred: `falcon-ai` then `deepseek-cursor-proxy` (CREATIVE_BACKLOG)
