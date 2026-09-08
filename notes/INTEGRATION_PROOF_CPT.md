# Integration proof — CPT (OSS registry target)

- **When:** 2026-09-03 (hub SoT writeback cycle; prior DGX verify 2026-09-02)
- **Role:** integration_architect
- **Registry (hub ROOT SoT):** `repos/registry.json` → CPT `status=adapt-verified-dgx` (was hub=`adapted` until this writeback)
- **Target path (DGX):** `/home/arnavrastogi/CPT`
- **Re-verify this cycle:**
  - `.venv/bin/python -m pytest tests/test_pipeline.py tests/test_normalize.py tests/test_diff.py tests/test_extract.py -q` — **19/19 PASS** (0.23s)
  - `automation_adapt.py --audit --target /home/arnavrastogi/CPT` — verify OK (module_scope warns non-blocking)
- **Trap:** system `python3` lacks `bs4`; native verify must use `.venv/bin/python`. Live factory meter reads **hub ROOT** registry — peer-3-only status never moves readiness. Hub file can be restored by peer cycle — re-read after write.
- **Meter:** `factory_meter_mode=self_sufficient` — Doc2Api/battery/browser hub writeback + unaudited/offline-mac stay in `notes/CREATIVE_BACKLOG.md`
