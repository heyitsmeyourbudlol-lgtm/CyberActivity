# Integration proof — compression rung0 (LOCAL ONLY)

_Needle: `OVERSEER_COMPRESSION_STRESS_THEN_INTEGRATE_2026_09_06`_  
_Local-only: `OVERSEER_MODEL_LOCAL_ONLY_2026_09_06`_  
_Landed: 2026-09-07T01:19:45Z_

## Verdict

**LOCAL workflow integrate: YES** — all `stress_bars.json` bars **PASS**; `integrate_allowed=true`; `publish_model=false`.

**Not:** public HF/endpoint release · not 1B north-star complete (`north_star_1b_complete=false`).

## Evidence

| Artifact | Path |
|----------|------|
| Stress bars | `notes/compression_artifacts/stress_bars.json` — status=PASS |
| Train status | `notes/compression_artifacts/rung0_train_status.json` — step=3000, heldout_kd≈0.1487≤0.15 |
| Checkpoint | `notes/compression_artifacts/rung0_checkpoints/rung0_latest.pt` (+ `rung0_final.pt`) |
| Skeleton | `notes/compression_artifacts/rung0_model_skeleton.json` — S≈134.09 @ N=1e7, U=74576, NVFP4 |
| Integrate stamp | `notes/compression_artifacts/local_integrate.json` |

## Bars (all PASS)

- S≥100 (134.09)
- unique U within budget (S≥100)
- NVFP4 pack bytes = U/2
- RAM residency min (≪512 MiB pack sketch)
- KD heldout ≤0.15
- no data prune
- T5 serve smoke

## Local factory wire

- CLEAN services kept active: `compression-auto-train` / `keep-alive` / `gpu-worker` / `result-watch` / `peer-loop`
- Rung0 process stays alive in complete-heartbeat (min-RAM NVFP4 student on disk)
- First consumer = Automation factory kit path only (`OVERSEER_FACTORY_FIRST_OSS_AUTOMATION_LOCAL_2026_09_06`)

## Next (not claimed done)

- Scale toward 1B logical / 10M unique north-star train rung (quality + residency)
- New BITNET_FACTCHECK C-rows when emitting new measured numbers
