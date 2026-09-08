# Integration proof — `_ensure_worktree_pool` ready-short-circuit skips prune_excess

**Date:** 2026-09-03  
**Role:** integration_architect  
**factory_meter_mode:** self_sufficient (hub kit flaw — external OSS proof deferred: falcon-ai in CREATIVE_BACKLOG)

## Evidence (before)

- Needle (pre-fix): `scripts/dgx_utilization.py` returned early when `peer-0..N-1` dirs existed:

```python
if all((pool_root / f"{prefix}-{i}").is_dir() for i in range(want)):
    return {"pool": want, "target": want, "ready": True}
```

- That skip never called `ensure_parallel_pool` / `prune_excess` → inflated pool stuck (live **39** excess `peer-8..47` at cycle start dry-run).
- Hub commits: `2d0b7e9` removed early return; `e53ef93` always calls `prune_excess_parallel_pool` first + reports `excess_found`/`excess_removed`.
- peer-3 worktree lacked colocated `scripts/dgx_utilization.py` (HEAD `c1821eb`) — tests imported hub only.

## Hypothesis → fix

- Floor-ready must **never** short-circuit; always `prune_excess_parallel_pool(cap=max_parallel_peers)` then `ensure_parallel_pool`.
- Colocate hub SoT into peer-3 + unittest `test_floor_dirs_still_call_ensure_parallel_pool`.

## Verify (after)

| Check | Result |
|-------|--------|
| dry-run excess before | **39** |
| `./scripts/peer ensure-pool --count 8` | `ok: 8 worktree(s) ready` |
| live inject peer-99 + `_ensure_worktree_pool` | `excess_found=2 excess_removed=2` (peer-9 + peer-99) |
| excess after | **[]** |
| peer-99 exists | **False** |
| `python3 -m unittest tests.test_dgx_utilization -q` | **4 OK** |
| `python3 -m unittest tests.test_automation -q` | **86 OK** |

## Hub SoT writeback

- `/home/arnavrastogi/Automation/scripts/dgx_utilization.py` + `tests/test_dgx_utilization.py` (already on hub)
- peer-3: colocated same files for independent worktree readback

## Queue / deferral

- Flaw closed this cycle (self_sufficient — not falcon-ai external proof)
- Next OSS proof target remains deferred: `falcon-ai` then `deepseek-cursor-proxy` (CREATIVE_BACKLOG)
