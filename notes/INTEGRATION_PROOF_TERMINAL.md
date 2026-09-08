# Integration proof — Terminal (OSS registry target)

- **When:** 2026-09-04T17:40Z
- **Role:** integration_architect (peer-5)
- **Registry SoT:** `repos/registry.json` Terminal `status=adapt-verified-mac` (write+independent JSON readback on hub + `.worktrees/peer-5`)
- **Target path (Mac):** `/Users/togi/Terminal`
- **Prior lie:** hub status `offline-mac` / notes "not present on this host" — path was ON_DISK on Mac
- **Adapt:** `python3 scripts/automation_adapt.py --install "/Users/togi/Terminal" --write --quick` → kit + `automation.config.json` + local profile (exit 0); `--audit --quick` `ok=True`
- **Native verify (in target tree this cycle):**
  - `python3 -m compileall -q .` — EXIT 0
  - `python3 stress_test.py --quick` — Passed: 28 Failed: 0 — EXIT 0
  - `python3 break_test.py --no-pty` — Passed: 28 Failed: 0 — EXIT 0
- **Worktree:** `git worktree add …/Terminal-peer-integration-p5 peer/integration-p5` from clean HEAD — **BLOCK**: HEAD lacks uncommitted product modules (`theme`, `platform_util`, `catalog_theme`); stress 6/7 fail. Removed worktree; next step when meter=`external_proof`: commit Terminal WIP or worktree from dirty index, then re-verify in worktree.
- **Kit self-check noise (non-gating vs registry verify_commands):** unittest 1 fail; pytest/ruff/mypy missing on host Python 3.14
- **factory_meter_mode:** `self_sufficient` — do **not** claim `external-proof-adapted`; remaining Mac offline (Marketplace / F.I.R.E. / SaaS Health) + deepseek Mac kit gap deferred `notes/CREATIVE_BACKLOG.md`
- **Falsifier passed:** hub + peer-5 readback `status == adapt-verified-mac`; product stress/break 28/0 in `/Users/togi/Terminal`
