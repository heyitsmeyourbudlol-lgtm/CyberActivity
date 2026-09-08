# Integration proof — dual-namespace bootout heal log (QA smoke)

_Date: 2026-09-04 23:18 · role `tech_writer` · SoT hub · peer-5 synced_

**Assignment:** `[kit] peer_self_heal: apply_heals log_fn must emit dual_brain_hub_peer on bootout` — file `scripts/peer_self_heal.py`; unittest; `./scripts/peer test-quick`

**Operator SOP:** `notes/SOP_DUAL_NAMESPACE_SELF_HEAL.md` (indexed in `notes/SOP_INDEX.md`)

## Smoke checklist

| # | Step | Path | Expected | Actual | Result |
|---|------|------|----------|--------|--------|
| 1 | Probe `apply_heals` with capturing `log_fn` for `dual_brain_hub_peer` | hub `scripts/peer_self_heal.py` apply_heals | `LOGS` includes `self-heal: dual_brain_hub_peer →` | `test_apply_heals_dual_brain_hub_peer_logs_log_fn` | **PASS** |
| 2 | Healer writes dedicated PEER_LOG line | `_log_dual_namespace_heal_action` | `self-heal dual-namespace bootout:` | live at heal call sites | **PASS** |
| 3 | Unittest asserts PEER_LOG + apply_heals log_fn | `tests/test_peer_self_heal.py` | both tests green | both OK | **PASS** |
| 4 | Land-proof closes Active | `project_automation._LAND_PROOF_NEEDLES` | `_land_proof_present` True | True | **PASS** |

## Verdict

**PASS closed** — needle `OVERSEER_DUAL_NAMESPACE_BOOTOUT_LOG_2026_09_04`; land-proof needles×4; Active `[x]`. SOP linked for operators.

## Anchors

- `scripts/peer_self_heal.py` — `_log_dual_namespace_heal_action` + `_heal_dual_namespace_collision`
- `tests/test_peer_self_heal.py` — `test_heal_dual_namespace_bootout_logs_peer_log` + `test_apply_heals_dual_brain_hub_peer_logs_log_fn`
- `scripts/project_automation.py` — land-proof needles for dual-namespace bootout log
- `notes/SOP_DUAL_NAMESPACE_SELF_HEAL.md` — operator SOP
