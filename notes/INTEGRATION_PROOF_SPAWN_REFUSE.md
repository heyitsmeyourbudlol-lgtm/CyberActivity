# Integration proof — hub spawn refuse already landed (queue theater)

**Date:** 2026-09-03  
**Role:** integration_architect  
**factory_meter_mode:** `self_sufficient` (hub kit flaw — external Newdrop/falcon proof deferred)

## Assignment

`[flaw-research] hub spawn refuse never landed — SpawnParallelTests FAIL` — claimed peer-3-only; hub lacks `_refuse_slot_out_of_cap`; silent-clamp recreates peer-20/22.

## Evidence (read this cycle)

| Probe | Result |
|-------|--------|
| Hub `scripts/peer_worktree.py:711` `_refuse_slot_out_of_cap` | **present** |
| Hub spawn wires `label` digit + `slot` (L914 / L918) | **refuse, not clamp** |
| `md5sum` hub vs peer-3 `peer_worktree.py` | **identical** `9cf1f392c9a8b9b30d48c1911cbe419e` |
| Hub `tests.test_automation.SpawnSlotCapTests` | **OK** (refuse 47 + label `"20"`) |
| Live probe `spawn(20)` dry_run cap=8 | `RuntimeError: refuse slot 20 outside [0, 8)` |
| Live `.worktrees/` excess peer-20/22 | **absent** (peer-0..7 + peer-coding only) |
| `./scripts/peer test-quick` (peer-3) | **114 OK** |

## Hypothesis → action

Root cause was **false-open queue** after land, not missing hub code. No re-land. Closed Active item with this proof; left related CE ASN `test-quick/verify omit tests.test_peer_worktree` untouched (SpawnSlotCapTests already in `tests.test_automation` / verify list).

## Falsifier (would reopen)

- Hub `spawn_parallel_worktree(47)` returns path without `RuntimeError`, or
- `SpawnSlotCapTests` FAIL on hub PYTHONPATH.

## Queue / deferral

- Closed: hub `notes/WORK_QUEUE.md` + `scripts/self_improve_context.md` (identical `[x]` text).
- Next OSS still deferred under self_sufficient: Newdrop / falcon-ai / deepseek (CREATIVE_BACKLOG).

## Side note (not this ASN)

Peer-3 `peer_self_heal._launchctl_running` is launchctl-only → plan-gate false-FAIL for improve daemon inside peer-N namespace. Hub SoT already has systemd probes. Assign factory_engineer if peer-3 plan-gate stays blocked.
