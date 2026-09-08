# Compression train recipe card

**Status:** **LOCKED** — T0–T4 packing/scale probes Done; recipe frozen for auto-train unlock (`compression_auto_train.py`). Hot dtype **NVFP4**. No data prune. Post-train stress → integrate only after `stress_bars.json` all PASS.  
**Gate:** [`COMPRESSION_TRAIN_READY.md`](COMPRESSION_TRAIN_READY.md) · North star: [`COMPRESSION_NORTH_STAR.md`](COMPRESSION_NORTH_STAR.md)  
**Hypotheses:** [`COMPRESSION_NOVEL.md`](COMPRESSION_NOVEL.md) (ALBERT-BitMoE primary · LoRA-Hive control)  
**T0 needle:** `OVERSEER_COMPRESSION_T0_PACK_2026_09_05` — ALBERT \(S\)=83.33/98.04; Hive \(S\)=99.80/99.98 @ \(N_L\)=1e5/1e6; pack≈\(U/8\); **quality N/A**  
**T3 needle:** `OVERSEER_COMPRESSION_T3_BITDISTILL_2026_09_05` — teacher logit bank → SVD student; heldout KD≤ε; **no prune**; quality=**proxy**  
**T3 cache needle:** `OVERSEER_COMPRESSION_T3_LOGIT_CACHE_2026_09_05` — durable full-corpus bank dump/load (Lane U); `--check-cache` roundtrip  
**T3 logit-cache:** `OVERSEER_COMPRESSION_T3_LOGIT_CACHE_2026_09_05` — durable dump/load bank roundtrip KD-stable (`--write-bank`/`--read-bank`/`--check-cache`/`--ensure-default-bank`); canonical path `notes/compression_artifacts/t3_teacher_logit_bank.json`  
**T4 needle:** `OVERSEER_COMPRESSION_T4_SCALE_2026_09_06` — N=1e7→1e8; S stable ±20%; S≥100; evidence `notes/compression_artifacts/t4_scale_result.json`  
**Lock needle:** `OVERSEER_COMPRESSION_T4_SCALE_2026_09_06` + PM freeze 2026-09-06 — `recipe_locked=true`

| Field | Stub value |
|-------|------------|
| **Stack primary** | **ALBERT-BitMoE** — shared **NVFP4** expert FFN body across layers + small per-layer LoRA |
| **Stack control** | **LoRA-Hive** — shared **NVFP4** hive + per-expert LoRA deltas |
| **Bitwidth / dtype** | Hot path **NVFP4** locked ([`NVFP4_LOCK_APPLICABILITY.md`](NVFP4_LOCK_APPLICABILITY.md)). Unique views compared at **same NVFP4**. 1-bit = optional cold only. |
| **\(S\) target** | Unique-param \(S = N_{\mathrm{logic}}/U \approx \mathbf{100}\) at 1B→10M; T0 bar \(S\ge50\) **met** on toys (pack math was 1-bit probe — retarget pack tests to NVFP4 next) |
| **Distill teacher** | Independent-layer (or denser) expert stack → shared-body student; BitDistill / MiniLLM-class logits (+ optional hidden align). Distill = quality path **not** byte compressor (**C150**) |
| **Data policy** | **No data / example / token pruning.** Full corpus only. Weight sparsity only with explicit pack+index byte math |
| **Eval bar** | T0 (done): \(U\), bytes≈\(U/8\), \(N/U\ge50\). Next: heldout recon/task ε vs teacher on toys — never claim measured 1B→10M until scale gates + ledger |
| **Stop criteria** | Fail if unique/pack miss by >2×; fail if KD gap only closes via data prune → redesign. Do not jump to 1B on packing-only evidence |
| **Research-speed refs** | [`RESEARCH_SPEED_TRAINING.md`](RESEARCH_SPEED_TRAINING.md) **S01–S32** + Lane U (CPU synthetic T0, unittest gate, OA/Hyperband, teacher-logit cache) |

**Honesty locks:** Hot dtype **NVFP4** (**C153**). B1–B5 / Lane-C = hypothesis on quality (**C146/C152**). zstd = disk only (**C154**). SSD/Zamba = util (**C148/C149/C156**). PagedAttention = KV (**C158/C159**). Spark ≠ NVLink MoE fabric (**C161**).

_LOCKED 2026-09-06 · NVFP4 · T0–T4 Done · recipe_locked=true · unlock via compression_auto_train · integrate only after stress bars._

---
**OVERSEER_COMPRESSION_TRAIN_UNLOCK_2026_09_05** · auto-train · train_unlocked=true · 2026-09-06 09:06Z
Hot path **NVFP4**; minimize unique U and RAM; no data prune; ALBERT-BitMoE primary + LoRA-Hive control.
