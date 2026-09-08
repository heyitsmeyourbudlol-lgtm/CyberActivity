# Integration proof — local-cycle ready ≠ git_clean

**Date:** 2026-09-03  
**Role:** integration_architect  
**factory_meter_mode:** self_sufficient  
**Repo:** Automation Hub (peer-3 worktree)  
**Needle:** `scripts/run_peer_tasks.py` `run_local_cycle` post-verify return

## Problem

`run_local_cycle` ran `run_verify_commands` then set `ready` only if
`live.git_clean and live.tests_ok and success_metrics_ok(live)`.
`success_metrics_ok` also ANDs `git_clean` (`project_automation.py`).

Post-agent path already uses `verify_ok = failures == 0` (`peer_loop.py`),
so continue_on_dirty can be green while a notes-dirty **local tick** stamped
`last_cycle.verify_ok=False` → dispatch-held theater.

## Fix

After `failures == 0`, return `(0, True)` without re-measuring porcelain.
Ready means the verify gate passed, not that git is clean.

## Verify (this worktree)

```
python3 -m unittest tests.test_automation.PeerLoopTests.test_run_local_cycle_ready_ignores_git_dirty \
  tests.test_automation.PeerLoopTests.test_run_local_cycle_failures_not_ready -q
→ OK (2 tests)
```

Expected: dirty + `failures==0` → `ready=True`, `rc=0`.  
Actual: same (see unittest above).

## Hub writeback (factory_engineer 2026-09-03)

Hub `scripts/run_peer_tasks.py` still ANDed `git_clean` after verify at assignment
time; peer-3 already returned `(0, True)`. Live gap = hub SoT (`./scripts/peer`
often resolves hub scripts).

```
EXPECTED: dirty + failures==0 → rc=0 ready=True
ACTUAL:   rc=0 ready=True (hub inspect + LocalCycleReadyTests)
HOLD:     hub comment "ready iff verify gate passed — not git_clean" (T+15+)
Dedicated: tests/test_local_cycle_ready.py (hub test_automation clobbers often)
```

Landmine note: `assertFalse(success_metrics_ok(dirty))` flakes under
`zz_automation_oversight_patch` (strips git_clean from metrics at import). Prefer
`assertNotIn("git_clean and live.tests_ok", inspect.getsource(run_local_cycle))`.

## Registry

Hub `status=active`; proof path this file. OSS targets remain deferred under
`self_sufficient`.

## Re-verify (2026-09-03T21:31Z integration_architect)

Assignment re-dispatched with peer-3 still showing Active launch line; WQ already `[x]`.

| Check | Result |
|-------|--------|
| peer-3 `run_local_cycle` post-verify | `return 0, True` + "ready iff verify gate passed" |
| hub twin | same return; no `git_clean and live.tests_ok` |
| `LocalCycleReadyTests` + PeerLoop ready/fail | 4/4 OK |
| dirty + failures==0 smoke | EXPECTED rc=0 ready=True · ACTUAL rc=0 ready=True |
| md5 peer-3 vs hub | differ — hub-only verify-protect / SIGKILL soft-defer (unrelated) |

HOLD: hub comment + return `(0, True)` present at re-verify. Durable SoT = peer-3 + hub both landed for this needle. Hub `repos/registry.json` notes needle HOLD=True at T+0 and T+5 (cid=r09f5ee30).
