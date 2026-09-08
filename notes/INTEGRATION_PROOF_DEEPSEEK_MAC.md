# Integration proof — deepseek-cursor-proxy (Mac peer-5)

- **When:** 2026-09-04T21:34Z
- **Role:** integration_architect (peer-5)
- **Registry SoT (this worktree):** `repos/registry.json` deepseek-cursor-proxy `status=adapted` (not `adapt-verified-mac`)
- **Prior DGX proof:** hub `notes/INTEGRATION_PROOF_DEEPSEEK.md` (kit+worktree verify on DGX; hub status can flap to `adapted` via Mac rsync)
- **Mac path:** `/Users/togi/deepseek-cursor-proxy`
- **Worktree (product-only, no kit):** `/Users/togi/deepseek-cursor-proxy/.worktrees/peer-5-ia-verify` @ detached `ea3da01`
- **Live probes this cycle:**
  - `test -d …/.git` — HAS_GIT (`main` @ `ea3da01`)
  - `automation.config.json` / `scripts/peer_orchestrate.py` — NO_KIT (main + WT)
  - Product native verify **in worktree** (main `.venv`, no kit install):
    - `cd …/.worktrees/peer-5-ia-verify && ../.venv/bin/python -m unittest discover -s tests -q`
    - → Ran **96** tests · OK (skipped=1) · EXIT **0**
- **Adapt / kit install (Mac):** **BLOCK** under `factory_meter_mode=self_sufficient` — do not `--install`; stay `adapted`
- **factory_meter_mode:** `self_sufficient` — keep `status=adapted`; do **not** claim `adapt-verified-mac` or Active-enqueue; kit install deferred `notes/CREATIVE_BACKLOG.md` **deepseek Mac kit**
- **Sibling leftovers (unchanged):** SaaS Health `offline-mac` typecheck PASS NO_GIT (`notes/INTEGRATION_PROOF_SAAS_HEALTH.md`); F.I.R.E./Marketplace empty-git husks `offline-mac`; hub leftover git/unaudited/needs-kit-install=NONE
- **Stale ASN note:** vault “Newdrop needs-kit-install” already cleared → hub SoT `adapt-verified-dgx` (2026-09-04T19:46Z)
- **Falsifier passed:** registry readback `status == adapted`; Mac still NO_KIT; WT product unittest EXIT 0; Active queue not extended for deepseek
