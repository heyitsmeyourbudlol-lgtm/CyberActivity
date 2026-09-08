# Integration proof — `_live_from_quick_cache` tests_ok poison

**Date:** 2026-09-03  
**Role:** integration_architect  
**Cycle:** flaw-research `_live_from_quick_cache` poisons `tests_ok=False` as `tests: cached`  
**factory_meter_mode:** `self_sufficient` (external OSS proof deferred)

## Needle

- Hub `scripts/project_automation._live_from_quick_cache` (~:638) returned on `_quick_cache_valid` + `_quick_test_cache_usable` with `tests_ok=bool(cache.get("tests_ok"))`.
- `_quick_test_cache_usable` returns True for smoke/self-check detail tokens **even when** `tests_ok=False`.
- Probe (hub pre-fix): `smoke_fail → LiveState(tests_ok=False, tests_detail='tests: smoke ok (cached, git unchanged)')`.
- Hub unittest `test_live_from_quick_cache_skips_unusable_tests_fail` FAIL @ L777 until patch.

## Fix

Require `cache.get("tests_ok") is True` before returning a cached `LiveState`; hardcode `tests_ok=True` on the hit path.

## Evidence (this cycle)

| Surface | Result |
|---------|--------|
| peer-3 `test_live_from_quick_cache_skips_failed_tests_ok` + measure twin | **OK** |
| peer-3 `./scripts/peer test-quick` (hub peer CLI → peer-3 cwd) | **115 OK** |
| peer-coding smoke_fail probe | `None` |
| Hub immediate post-write unittest | **OK** (sha `843b0c8d…`) |
| Hub T+5 sha hold | **False** → `0d5e3b03…` (rsync clobber; `tests_ok=bool` restored) |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ OK

/home/arnavrastogi/Automation/scripts/peer test-quick  # cwd=peer-3
→ Ran 115 tests … OK
```

## Hub hold

Mac→DGX `rsync --server` reverts hub `scripts/project_automation.py` within ~5s. Durable SoT = peer-3 + peer-coding. Related backlog: exclude `scripts/` (and registry) from rsync / post-rsync pin.

## Paths

- `scripts/project_automation.py` (`_live_from_quick_cache`)
- `tests/test_automation.py` (skip failed / smoke-fail + measure fall-through)
- peer-coding `scripts/project_automation.py` (same guard)
- Queue: hub + peer-coding `WORK_QUEUE` / `self_improve_context` → `[x]`

## Re-verify 2026-09-03T21:26Z (integration_architect)

| Surface | Result |
|---------|--------|
| peer-3 `test_live_from_quick_cache_skips_failed_tests_ok` + measure twin | **OK** (2 tests) |
| hub `_live_from_quick_cache` `tests_ok is not True` guard | **True** |
| hub HOLD T+5 | **True** (sha `1009cb92bcaeb365…`) |
| peer-coding guard | **True** |
| WORK_QUEUE / self_improve_context | **[x]** (launch Active was stale) |

No code edit this cycle — assignment already landed; re-verify + HOLD only.

## Re-verify 2026-09-04T02:29Z (integration_architect)

Launch Active still listed this flaw; WORK_QUEUE/`self_improve_context` already `[x]`. No code edit.

| Surface | Result |
|---------|--------|
| peer-3 `scripts/project_automation.py:655` `tests_ok is not True` → `None` | **present** |
| hub same guard | **present** |
| peer-3 smoke_fail probe → `None` | **OK** |
| targeted unittest (2) | **OK** |
| hub HOLD T+0/T+5 | **True** (`9998d6a1207b7adc…`) |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

Note: full `./scripts/peer test-quick` still red on unrelated attrs (`_select_dispatch_items`, dirty-dispatch drop, daemon snapshots) — not this needle.

## Re-verify 2026-09-04T02:43Z (integration_architect)

Launch Active still listed this flaw; WORK_QUEUE/`self_improve_context` already `[x]`. No code edit.

| Surface | Result |
|---------|--------|
| peer-3 L655 `tests_ok is not True` → `None` | **present** |
| hub same guard | **present** |
| peer-3 smoke_fail probe → `None` | **OK** |
| targeted unittest (2) | **OK** |
| hub `project_automation` HOLD T+0/T+5 | **True** (`9998d6a1207b7adc…`) |
| hub `repos/registry.json` HOLD T+5 | **False** (Mac rsync; durable SoT=peer-3) |
| peer-coding guard | **True** |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Done self-check:** verify matched Plan (smoke_fail→None + twins OK + pa guard HOLD); queue already `[x]`; no code edit; external OSS deferred under `self_sufficient`.

## Re-verify 2026-09-04T02:47Z (integration_architect)

Launch Active still listed this flaw; WORK_QUEUE/`self_improve_context` already `[x]`. No code edit.

| Surface | Result |
|---------|--------|
| peer-3 L655 `tests_ok is not True` → `None` | **present** |
| hub same guard | **present** sha `9998d6a1207b7adc` |
| peer-coding guard | **True** |
| peer-3 smoke_fail probe → `None` | **OK** |
| targeted unittest (2) | **OK** |
| hub HOLD T+0/T+5 | **True** |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Done self-check:** expected smoke_fail→None + twins OK + hub HOLD True @L655; actual match; launch Active stale (WQ [x]); no code edit.

## Re-verify 2026-09-04T03:10Z (integration_architect)

Launch Active still listed this flaw; WORK_QUEUE/`self_improve_context` already `[x]`. No code edit.

| Surface | Result |
|---------|--------|
| peer-3 L655 `tests_ok is not True` → `None` | **present** sha `fbdc64513921` |
| hub same guard | **present** sha `9998d6a1207b` |
| peer-coding guard | **True** |
| peer-3 smoke_fail probe → `None` | **OK** |
| targeted unittest (2) | **OK** |
| hub HOLD T+0/T+5 | **True** (`9998d6a1207b7adc…`) |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |

```text
PYTHONPATH=scripts python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Strategy:** evidence=L655+WQ[x]; hypothesis=stale launch Active; falsifier=missing guard or test FAIL; verify=twins+HOLD; defy=no re-edit.

**Done self-check:** expected smoke_fail→None + 2 OK + hub HOLD True @L655; actual match; no code edit; external OSS deferred.

## Re-verify 2026-09-04T04:02Z (integration_architect)

Launch Active still listed this flaw; WORK_QUEUE/`self_improve_context` already `[x]`. No code edit.

| Surface | Result |
|---------|--------|
| peer-3 L655 `tests_ok is not True` → `None` | **present** sha `fbdc64513921` |
| hub same guard | **present** sha `9aadc98991e031` HOLD T+5 **True** |
| peer-coding guard | **True** (L572+L655) |
| peer-3 smoke_fail probe → `None` | **OK** |
| hub smoke_fail probe → `None` | **OK** |
| targeted unittest (2) | **OK** |
| `factory_meter_mode` | `self_sufficient` — Newdrop external deferred |

```text
env -u RAM_AUTOMATION_NO_SUBTEST PYTHONPATH=scripts python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Strategy:** evidence=L655+WQ[x]+PROJECT_LEARNING 02:48Z; hypothesis=stale launch Active; falsifier=missing guard/test FAIL; verify=twins+hub HOLD; defy=no re-edit.

**Done self-check:** expected smoke_fail→None + 2 OK + hub HOLD True @L655; actual match; no code edit; external OSS deferred.

## Re-verify 2026-09-04T04:15Z (integration_architect)

Launch Active still listed this flaw; WORK_QUEUE/`self_improve_context` already `[x]`. No code edit. cid=`r8fad749af57`.

| Surface | Result |
|---------|--------|
| peer-3 L655 `tests_ok is not True` → `None` | **present** sha `fbdc64513921` |
| hub same guard | **present** sha `9998d6a1207b7adc…` HOLD T+5 **True** |
| peer-3 smoke_fail probe → `None` | **OK** |
| targeted unittest (2) | **OK** |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Strategy:** evidence=L655+WQ[x]+PROJECT_LEARNING; hypothesis=stale launch Active; falsifier=missing guard/test FAIL; verify=twins+hub HOLD; defy=no re-edit.

**Done self-check:** expected smoke_fail→None + 2 OK + hub HOLD True @L655; actual match; no code edit; external OSS deferred.

## Re-verify 2026-09-04T04:29Z (integration_architect)

Launch Active still listed this flaw; WORK_QUEUE/`self_improve_context` already `[x]`. No code edit. cid=`r0b63504bb66`.

| Surface | Result |
|---------|--------|
| peer-3 L655 `tests_ok is not True` → `None` | **present** sha `fbdc64513921` |
| hub guard (post-rsync L670, `_git_cache_fresh` shape) | **present** sha `86987817e91e` (T+5 HOLD **False** — Mac rsync rewrote body; guard survived) |
| peer-3 smoke_fail → `None` / ok → `tests_ok=True` | **OK** |
| hub smoke_fail → `None` | **OK** |
| targeted unittest (2) | **OK** |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Strategy:** evidence=L655+WQ[x]+PROJECT_LEARNING 04:15Z; hypothesis=stale launch Active re-dispatch; falsifier=missing guard/test FAIL; verify=twins+hub smoke_fail→None; defy=no re-edit.

**Done self-check:** expected smoke_fail→None + 2 OK + guard present; actual match (hub HOLD False but guard survived rsync rewrite); no code edit; external OSS deferred.

## Re-verify 2026-09-04T04:38Z (integration_architect) cid=`r6a9a4be7`

Launch Active still listed closed WQ [x]. Guard already SoT — **fixture-only** fix.

| Surface | Result |
|---------|--------|
| peer-3 L768 `tests_ok is not True` → None | **present** |
| hub==peer-3 sha `86987817e91e5408` | **match** |
| smoke_fail / fail → None | **OK** |
| ok path without `git_ts` → None (false FAIL) | **root: fixture drift vs `_git_cache_fresh`** |
| peer-3 unittest after `git_ts` on fail_cache | **2 OK** |
| hub `test_live_from_quick_cache_skips_unusable_tests_fail` | **OK** (already had git_ts) |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |
| Edit | `tests/test_automation.py` only (add `git_ts`) — **no** `_live_from_quick_cache` re-edit |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

expected_vs_actual: expected=2 OK + smoke None + L768 · actual=match

## Re-verify 2026-09-04T00:54Z (integration_architect) cid=`r840c30d3ce6f`

Launch Active still listed closed WQ `[x]`. No code edit — re-verify only.

| Surface | Result |
|---------|--------|
| peer-3 L768 `tests_ok is not True` → None | **present** |
| hub L768 same guard | **present** (survived sha churn) |
| hub smoke_fail / fail_cache → None | **OK** |
| peer-3 unittest (2 twins) | **OK** |
| hub HOLD vs prior sha941645da | **False** (rsync rewrite) — guard still True |
| WQ / self_improve_context | **[x]** |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |
| Edit | **none** |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Strategy:** evidence=L768+WQ[x]+PROJECT_LEARNING 04:29Z; hypothesis=stale launch Active re-dispatch; falsifier=missing guard or smoke→LiveState; verify=twins+hub smoke_fail→None; defy=no re-edit.

**Done self-check:** expected smoke_fail→None + 2 OK + L768 present; actual match; done-gate mechanical OK after hub sync-queue; GLink DONE posted.

## Re-verify 2026-09-04T05:00Z (integration_architect) cid=`r51cb45b4e9c5`

Launch Active still listed closed WQ `[x]`. No code edit — re-verify only (prior lands hold).

| Surface | Result |
|---------|--------|
| peer-3 L768 `tests_ok is not True` → None | **present** |
| hub L768 same guard + `_git_cache_fresh` shape | **present** (func body match peer-3) |
| hub smoke_fail / fail_cache → None | **OK** |
| hub ok path → tests_ok True + cached detail | **OK** |
| peer-3 unittest (2 twins) | **OK** |
| hub `test_live_from_quick_cache_skips_unusable_tests_fail` | **OK** |
| WQ / self_improve_context | **[x]** |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |
| Edit | **none** |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

expected_vs_actual: expected=2 OK + hub fail/smoke→None + L768 guard · actual=match · edit=none

## Re-verify 2026-09-04T05:13Z (integration_architect) cid=`r6a084860744`

Launch Active still listed closed WQ `[x]`. No code edit — re-verify + hub HOLD only.

| Surface | Result |
|---------|--------|
| peer-3 L768 `tests_ok is not True` → None | **present** |
| hub L773 same guard + usable L475 `is True` | **present** |
| peer-coding L768 guard | **present** |
| hub/peer-3 smoke_fail → None | **OK** |
| peer-3 unittest (2 twins) | **OK** |
| hub HOLD T+0/T+5 | **True** (`8290b25af0f63dd0…`) |
| WQ / self_improve_context | **[x]** |
| `factory_meter_mode` | `self_sufficient` — external OSS deferred |
| Edit | **none** |

```text
env -u PYTHONPATH -u RAM_AUTOMATION_NO_SUBTEST python3 -m unittest \
  tests.test_automation.PeerLoopTests.test_live_from_quick_cache_skips_failed_tests_ok \
  tests.test_automation.PeerLoopTests.test_measure_live_state_does_not_pin_failed_quick_cache -q
→ Ran 2 tests … OK
```

**Strategy:** evidence=L768+WQ[x]+PROJECT_LEARNING; hypothesis=stale launch Active; falsifier=missing guard or smoke→LiveState; verify=twins+hub smoke→None+HOLD; defy=no re-edit.

**Done self-check:** expected smoke_fail→None + 2 OK + HOLD True; actual match.
