# Integration proof — MATTERNTHREAD (OSS registry target)

- **When:** 2026-09-03 (hub SoT writeback confirmed via **independent-process** readback)
- **Role:** integration_architect
- **Registry (hub ROOT SoT):** `/home/arnavrastogi/Automation/repos/registry.json` → MATTERNTHREAD `status=adapt-verified-dgx`
  - **Before this cycle:** hub SoT was `adapted`
  - **After write+readback:** hub + peer-3 both `adapt-verified-dgx` (asserted in fresh Python process: `hub_sot_match adapt-verified-dgx`)
- **Target path (DGX):** `/home/arnavrastogi/MATTERNTHREAD`
- **Re-verify this cycle (in target tree):**
  - `python3 scripts/automation_adapt.py --audit --target /home/arnavrastogi/MATTERNTHREAD` — **ok=True**; local verify OK (`tests.test_automation`, `peer_orchestrate --self-check`); warns: test_command / verify_commands drift vs local.json (non-blocking)
  - `.venv/bin/python -m pytest tests/test_mdns_parser.py tests/test_otbr_client.py tests/test_bridge_recovery.py tests/test_dashboard_sdk.py tests/test_report_upload.py tests/test_live.py -q` — **19/19 PASS** (0.43s)
- **Trap:** Peer-3 `repos/registry.json` alone is not SoT — always re-read hub ROOT after write in a **new** process.
- **Meter:** `factory_meter_mode=self_sufficient` — next DGX-present adapted: `falcon-ai` (then `deepseek-cursor-proxy`); Mac-only offline deferred. Parked in `notes/CREATIVE_BACKLOG.md`.
- **Prior status:** hub `adapted` → hub `adapt-verified-dgx` (2026-09-03 writeback+readback)
