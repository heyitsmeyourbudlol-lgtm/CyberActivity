# Integration proof — factory_grid.global_agent_cap ≤ max_parallel_peers

**Date:** 2026-09-04  
**Role:** integration_architect  
**Mode:** `factory_meter_mode=self_sufficient` (hub/kit clamp; external OSS Newdrop deferred)

## Needle

1. `scripts/factory_grid.py` `global_agent_cap()` — raw `global_agents` (dgx_speed=48) must `min(raw, max_parallel_peers())`.
2. Fallback when `global_agents` unset/0: `hub_agent_cap() + external_agent_cap()` must also clamp to peers (hub previously returned 12 with hub=8+ext=4, peers=8).
3. Peer-3 lacked `tests/test_factory_grid.py` while hub lean verify + adapt expected it.

## Fix

- Peer-3 SoT already clamped raw + fallback (`min(..., peers)`).
- Hub writeback: sync `factory_grid.py` so fallback clamps (12→8).
- Land `tests/test_factory_grid.py` on peer-3 + hub (5 tests incl. raw48→8 + fallback).

## Verify

```
python3 -m unittest tests.test_factory_grid -q  → Ran 5 tests OK (peer-3 + hub)
HUB fallback after fix 8 · HUB raw48 after fix 8
```

## Expected vs actual

| Check | Expected | Actual |
|-------|----------|--------|
| global_agents=48, peers=8 | 8 | 8 |
| hub=8+ext=4, global=0, peers=8 | 8 | 8 |
| unittest exit | 0 | 0 |

## Status

`global_agent_cap` clamp landed; irreversible artifact = this proof + hub/peer-3 md5 match on `factory_grid.py` + `tests/test_factory_grid.py`.
