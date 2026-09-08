# Integration proof — stale pool adapt-state null fp poison

**Date:** 2026-09-03  
**Role:** integration_architect  
**factory_meter_mode:** self_sufficient (hub kit flaw — external OSS proof deferred CREATIVE_BACKLOG)

## Evidence (before)

- `~/.config/automation-hub/adapt-state.json` had `git_fingerprint: null` (mtime ~00:40)
- 8/8 `.worktrees/peer-0..7` HEADs ≠ hub tip; all dirty (hard-reset unsafe)
- peer-0/1/2/7 kept `config_namespace=automation-hub` and pre-refuse-null `save_adapt_state` (raw `json.dumps`)
- Stale trees hub-anchored writes to shared hub adapt-state → `adapt_stale` dispatch hold

## Fix

1. `scripts/peer_worktree.py` `ensure_parallel_pool` after ensure:
   - `sync_pool_adapt_refuse_null` — copy hub `automation_adapt.py` into slots lacking refuse-null
   - `isolate_pool_adapt_namespaces` — rewrite shared hub ns → `peer-N`
   - `align_parallel_pool_to_hub` — soft `git reset --hard` hub tip when porcelain clean
2. `scripts/peer` — from `.worktrees/*`, adapt/heal/ensure-pool/self-heal prefer `HUB_ROOT` scripts
3. Operational: `./scripts/peer ensure-pool` + hub `automation_adapt --heal --write --quick`

## Verify (after)

| Check | Result |
|-------|--------|
| peer-0..7 `config_namespace` | `peer-0` … `peer-7` (no shared `automation-hub`) |
| refuse-null synced | peer-0,1,2,3,5,6,7 (peer-4 already had it) |
| hub adapt-state `git_fingerprint` | non-null (`28c76d7f…` + porcelain) |
| peer-0 `save_adapt_state(null)` | writes `~/.config/peer-0/…`; hub file unchanged |
| `python3 -m unittest tests.test_peer_worktree tests.test_automation -q` | OK |

## Queue

- Hub `notes/WORK_QUEUE.md` + `scripts/self_improve_context.md`: **[x] Stale peer worktrees poison shared adapt-state with null fp**
