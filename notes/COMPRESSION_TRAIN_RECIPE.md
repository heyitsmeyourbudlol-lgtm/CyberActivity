# Compression train recipe card (stub)

**Status:** **T0–T4 GREEN (proxy) · TRAIN-LOCKED** — packing + \(k\)-sweep + SVD + BitDistill + scale U/N proven on toys; do **not** start real model training. Fill/lock this card for a train rung only after explicit quality gates (T4≠unlock).  
**Gate:** [`COMPRESSION_TRAIN_READY.md`](COMPRESSION_TRAIN_READY.md) · North star: [`COMPRESSION_NORTH_STAR.md`](COMPRESSION_NORTH_STAR.md)  
**Hypotheses:** [`COMPRESSION_NOVEL.md`](COMPRESSION_NOVEL.md) (ALBERT-BitMoE primary · LoRA-Hive control · SVD-TieStack · BitDistill)  
**T0 needle:** `OVERSEER_COMPRESSION_T0_PACK_2026_09_05` — ALBERT \(S\)=83.33/98.04; Hive \(S\)=99.80/99.98 @ \(N_L\)=1e5/1e6; pack≈\(U/8\); **quality N/A**  
**T0 pack-cache needle:** `OVERSEER_COMPRESSION_T0_PACK_CACHE_2026_09_05` — durable dump/load/`--ensure-default-pack` → `notes/compression_artifacts/t0_pack_report.json`; **TRAIN still LOCKED**  
**Dual SoT (pack+logit) gate:** `python3 scripts/compression_t0_pack.py --dual-sot-check` — requires `t0_pack_report.json` + `t3_teacher_logit_bank.json` both green (`dual_sot_ok`); **still TRAIN-LOCKED** (green Dual SoT ≠ unlock)  
**T1 needle:** `OVERSEER_COMPRESSION_T1_SHARE_2026_09_05` — \(k\in\{2,4,8,16\}\) ALBERT+Distill-Fold \(U\downarrow\); recon MSE↑; **cliff before \(S\approx100\)**; `data_prune=false`; quality=**proxy**  
**T1 share-cache needle:** `OVERSEER_COMPRESSION_T1_SHARE_CACHE_2026_09_05` — durable dump/load/`--ensure-default-ablation` → `notes/compression_artifacts/t1_share_ablation_report.json`; refuse prune/unlock; **TRAIN still LOCKED**  
**T2 needle:** `OVERSEER_COMPRESSION_T2_SVD_LORA_2026_09_05` — SVD+LoRA heldout MSE↓ under \(U\) budget; quality=**proxy**  
**T2 svd-cache needle:** `OVERSEER_COMPRESSION_T2_SVD_LORA_CACHE_2026_09_05` — durable dump/load/`--ensure-default-report` → `notes/compression_artifacts/t2_svd_lora_report.json`; refuse prune/unlock; **TRAIN still LOCKED**  

**T3 needle:** `OVERSEER_COMPRESSION_T3_BITDISTILL_2026_09_05` — teacher logit bank → SVD student; heldout KD≤ε; **no prune**; quality=**proxy**  
**T3 cache needle:** `OVERSEER_COMPRESSION_T3_LOGIT_CACHE_2026_09_05` — durable full-corpus bank dump/load (Lane U); `--check-cache` roundtrip; **not** a train unlock  
**T3 logit-cache:** `OVERSEER_COMPRESSION_T3_LOGIT_CACHE_2026_09_05` — durable dump/load bank roundtrip KD-stable (`--write-bank`/`--read-bank`/`--check-cache`/`--ensure-default-bank`); canonical path `notes/compression_artifacts/t3_teacher_logit_bank.json`; **TRAIN still LOCKED**  
**T4 needle:** `OVERSEER_COMPRESSION_T4_SCALE_2026_09_05` — \(N_L\in\{10^6,10^7,10^8\}\) ALBERT+Hive U/N ±20% (max |rel−1|≈1.94%); pack util smoke; quality=**proxy**  
**T4 scale-cache needle:** `OVERSEER_COMPRESSION_T4_SCALE_CACHE_2026_09_05` — durable dump/load/`--ensure-default-report` → `notes/compression_artifacts/t4_scale_report.json`; refuse prune/unlock; **TRAIN still LOCKED**

| Field | Stub value |
|-------|------------|
| **Stack primary** | **ALBERT-BitMoE** — shared 1-bit expert FFN body across layers + small per-layer LoRA |
| **Stack polish** | **SVD-TieStack + LoRA** — tied truncated-SVD init under same \(U\) budget (T2 winner on toys) |
| **Distill** | **BitDistill** — teacher logit bank → body-shared student (T3); freeze readouts; full corpus |
| **Stack control** | **LoRA-Hive** — shared 1-bit hive + per-expert LoRA deltas |
| **Bitwidth** | Same **1-bit** packed baseline on logical and unique views (ternary/binary BitNet-class OK) |
| **\(S\) target** | Unique-param \(S = N_{\mathrm{logic}}/U \approx \mathbf{100}\) at 1B→10M; T0 bar \(S\ge50\) **met** on toys |
| **Distill teacher** | Independent-layer (or denser) expert stack → shared-body student; BitDistill / MiniLLM-class logits (+ optional hidden align). Distill = quality path **not** byte compressor (**C150**) |
| **Data policy** | **No data / example / token pruning.** Full corpus only. Weight sparsity only with explicit pack+index byte math |
| **Eval bar** | T0–T4 (done): pack/\(U\)/\(k\)-cliff/SVD/BitDistill KD + scale U/N ±20% proxies on toys. Never claim measured 1B→10M until quality gates + ledger + recipe TRAIN-LOCK |
| **Stop criteria** | Fail if unique/pack miss by >2×; fail if KD gap only closes via data prune → redesign. Do not jump to 1B on packing-only evidence |
| **Dual SoT (TRAIN-LOCK)** | Both green before any real train unlock: `t0_pack_report.json` (`--ensure-default-pack` / `--dual-sot-check` / `--ensure-dual-sot`) **and** `t3_teacher_logit_bank.json` (`--ensure-default-bank`). CLI: `python3 scripts/compression_t0_pack.py --ensure-dual-sot --json` → `dual_sot_ok=true` · `train_unlocked=false`. Dual SoT ≠ unlock. |
| **Research-speed refs** | [`RESEARCH_SPEED_TRAINING.md`](RESEARCH_SPEED_TRAINING.md) **S01–S32** + Lane U (CPU synthetic T0, unittest gate, OA/Hyperband, **teacher-logit cache GREEN** via T3 dump/load + `--ensure-default-bank` → `notes/compression_artifacts/t3_teacher_logit_bank.json`) |

**Honesty locks:** B1–B5 / Lane-C stacks = **hypothesis** on quality until measured (**C146/C152**). SSD/Zamba = serve util only (**C148/C149**). FP16→1-bit 16× ≠ north star (**C147**).

_Stub 2026-09-05 · fact_checker pristine audit. TRAIN-LOCKED until explicit recipe lock (T0–T4 toys ≠ unlock). T4 scale filed 2026-09-05._
