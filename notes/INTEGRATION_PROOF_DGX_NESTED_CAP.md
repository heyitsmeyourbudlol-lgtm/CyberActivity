# Integration Proof — DGX Host Nested Caps Survive Overlay

**Date:** 2026-09-03
**Cycle:** peer-3 integration_architect
**Status:** FIXED + HUB SOT WRITEBACK VERIFIED

## Problem

Hub `automation.config.json` had `dgx_host.dgx_unittest_cap=96` and `dgx_host.dgx_max_cursor_agents=48`.
Top-level overlay only set `dgx_unittest_cap=2` and `max_parallel_peers=8`.
`_dgx_cfg()` returned nested values first, so `guard_shell_vars` / `dgx_watch` / `dgx_local_ram_guard.sh --shell-vars` saw 96/48 — unable to trim storms.

## Root Cause (pinpoint)

1. Hub SoT `scripts/dgx_ram_budget.py` `_dgx_cfg` only ceiling-clamped (96→24) and **ignored** top-level overlay 2.
2. Hub `guard_shell_vars` preferred nested-first (`cfg.get(...) or auto.CFG.get(...)`) so overlay never won.
3. Hub `dgx_watch._dgx_cfg` returned raw nested dict (96/48) with no overlay merge.
4. Peer-3 already had `_overlay_nested_caps`; hub SoT never received writeback → live daemons stayed broken.

## Fix (this cycle)

1. Hub writeback: `_overlay_nested_caps` + dict-copy `_dgx_cfg` + overlay-aware `guard_shell_vars` in `/Automation/scripts/dgx_ram_budget.py`.
2. Hub writeback: overlay+ceiling in `/Automation/scripts/dgx_watch.py` `_dgx_cfg` (kept hub remote-heal body intact).
3. Data already sane: nested caps 96/48 → 20/8 in hub + peer-3 `automation.config.json`.

## Evidence (expected vs actual)

| Probe | Expected | Actual |
|-------|----------|--------|
| Hub `_dgx_cfg` fake overlay 2/8 + nested 96/48 | `2 8` | `2 8` (was `24 8` before writeback) |
| Hub `guard_shell_vars` same fake | `unittest_cap=2 max_agents=8` | `2 / 8` |
| Hub `dgx_watch._dgx_cfg` same fake | `2 8` | `2 8` (was `96 48`) |
| Live hub `--shell-vars` (local overlay top=2 + nested 20) | `2 8 …` | `2 8 21.7 15.7 100.0 …` (was `20 8` pre-fix) |
| `tests.test_dgx_ram_budget` + watch overlay + `DgxHostNestedCapTests` | OK | 19 OK |

## Files

- `/home/arnavrastogi/Automation/scripts/dgx_ram_budget.py` — hub SoT
- `/home/arnavrastogi/Automation/scripts/dgx_watch.py` — hub SoT (`_dgx_cfg` only)
- peer-3 mirrors already had overlay path

## factory_meter_mode

`self_sufficient` — external OSS adapt proof deferred (Backlog). This cycle = hub SoT nested-cap clamp only.

## Next

- Hold hub writeback ≥45s against Mac→DGX rsync clobber.
- When meter ≠ `self_sufficient`: resume falcon-ai / deepseek-cursor-proxy adapt-verified-dgx.

## Hub hold (this cycle)

- T+0 writeback: overlay_fn True, fake CFG 2/8, live `--shell-vars` `2 8` (local overlay top=2 + nested 20).
- T+12s: still True (budget+watch).
- T+45s: still True — `_dgx_cfg` 2/8, live `--shell-vars` `2 8`. (Earlier this cycle Mac rsync rewound mtime to 11:53; this writeback held.)
