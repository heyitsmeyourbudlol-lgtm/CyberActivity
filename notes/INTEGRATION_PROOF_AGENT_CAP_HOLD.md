# Integration proof — agent_cap_hold clamp + refuse ROOT

**Date:** 2026-09-03  
**Role:** integration_architect  
**Mode:** `factory_meter_mode=self_sufficient` (hub dispatch fix; external OSS proof still deferred)

## Needle

1. `scripts/dgx_ram_events.py` `_agent_cap` / `agent_cap_for_mode` — `agent_cap_hold=48` in `automation.config.local.json` ignored `max_parallel_peers=8`.
2. `scripts/peer_parallel_dispatch.py` `run_parallel_niche_cycle` — `cwd = pool[i] if i < len(pool) else ROOT` launched niches on hub ROOT when pool short.

## Fix

- Hold/trim caps: `min(cfg, max_parallel_peers())` via `_agent_cap(..., clamp_peers=True)`.
- Short pool: trim batch to `len(pool)`; log `refuse ROOT cwd`; never launch with `cwd=ROOT`.

## Verify (actual)

```
max_parallel_peers 8
hold 8
trim 8
budget.ram_agent_cap 8
tests.test_dgx_ram_events + tests.test_peer_parallel_dispatch — 13 OK
./scripts/peer test-quick — 80 OK
```

## Expected vs actual

| Expected | Actual |
|----------|--------|
| `agent_cap_for_mode("hold")==8` with cfg 48 | 8 |
| niche not launched with cwd=ROOT | refuse ROOT + 1 launch on `/tmp/wt0` |
| test-quick green | 80 OK |

## Next

Related open: `factory_grid.hub_agent_cap` / `dgx_utilization target_agent_fill=48` / `dgx_install_services.sh` clobber — still uncapped upstream of this clamp.
