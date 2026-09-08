# N01 research stress gaps

**Needle:** `OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04`  
**Run:** 2026-09-06 · role `niche_distiller` · heldout acc **1.000** (9/9) · full corpus **45**  
**Method:** `--eval-only` on `N01_*_heldout.jsonl` + live WORK_QUEUE / Backlog bullets via `predict`

Do **not** prune the corpus. Append JSONL / tighten rule baseline; neural ~10M swap later.

## Miss classes

| ID | Gap | Evidence | Falsifier | Status |
|----|-----|----------|-----------|--------|
| G1 | **Bare module scope** — `` `peer_watch` `` without `scripts/` → `scope=""` vs gold `scripts/peer_watch.py` | Stall-watch row (`OVERSEER_WATCH_HOLD_PRIMARY`) | Row exact-matches after `_MOD_TICK_RE` | **fixed** 2026-09-05 — `_MOD_TICK_RE` → `scripts/<mod>.py` if file exists |
| G2 | **Unknown bracket tags → kit=null** — `[compression-train]`, `[flaw-research]`, `[comms-improve]`, `[research-speed]` | Live Active + train exemplars | Serve → `kit=false` | **fixed** — tags in `_KIT_TAG_FALSE`; flaw-research gold kit corrected false |
| G3 | **Glob / wildcard paths** — `scripts/compression_t4_*` | Active T4 scale rung | Scope `scripts/compression_t4_*` | **fixed** — `*` allowed in `_SCOPE_BARE_RE` |
| G4 | **Notes-relative bare filenames** — `COMPRESSION_TRAIN_RECIPE.md` | Active Freeze TRAIN recipe | Scope `notes/COMPRESSION_TRAIN_RECIPE.md` | **fixed** — `_NOTES_MD_BARE_RE` |
| G5 | **Tags-only / prose-only → empty scope** — `[comms-improve]` Active lines mention `bus.jsonl` / `peer_loop.` without `scripts/`/`notes/` path | Live Active Compact encodings + GibberLink | Gold `scope=""` exact-match; do **not** invent `notes/COMMS_TRENDS.md` | **fixed** 2026-09-05 — appended 2 JSONL exemplars (no prune); accept empty scope |
| G6 | **`[factory:…]` lane tags → kit=null** — `[factory:grounded_loop]` missing from `_KIT_TAG_FALSE` | Live WORK_QUEUE (2026-09-06) | Serve → `kit=false` (scope still from bare `peer_loop` / paths) | **fixed** 2026-09-06 — `factory:[a-z0-9_]+` in `_KIT_TAG_FALSE`; +2 JSONL (no prune) |
| G7 | **Bare `stress_bars.json` → empty / wrong notes/** — Backlog write lacks `notes/compression_artifacts/` | Live Backlog `OVERSEER_COMPRESSION_STRESS_*`; canonical `notes/COMPRESSION_TRAIN_READY.md` | Serve → `scope=notes/compression_artifacts/stress_bars.json` (not `notes/stress_bars.json`) | **fixed** 2026-09-06 — `_ARTIFACT_JSON_BARE_RE`; +2 JSONL; heldout 9@1.0 |

## Live sample (post-fix 2026-09-06)

| Line tag | pred.kit | pred.scope | Notes |
|----------|----------|------------|-------|
| `[compression-train]` T4 scale | false | `scripts/compression_t4_*` | G2+G3 closed |
| `[compression-train]` Freeze TRAIN | false | `notes/COMPRESSION_TRAIN_RECIPE.md` | G2+G4 closed |
| `[comms-improve]` Compact encodings | false | `""` | G5 closed — tags-only; no invented COMMS_TRENDS path |
| `[factory:grounded_loop]` Harden | false | `scripts/peer_loop.py` | G6 closed — factory lane ≠ kit |
| `[compression-train]` write stress_bars.json | false | `notes/compression_artifacts/stress_bars.json` | G7 closed — TRAIN_READY canonical |
| `[compression-train]` Integrate if bars clear | false | `""` | tags-only; no invented path |
| Stall-watch `` `peer_watch` `` | true | `scripts/peer_watch.py` | G1 closed |

## Pass / ship rule

Heldout niche accuracy ≥ **0.90** after each fix wave. Ship stress doc even if some G* remain open — enqueue next-run rows here, do not invent hardware numbers.

## Anti-theater

- Heldout 1.0 alone ≠ production-ready; live Backlog miss classes above are the real stress.
- Closing BITNET_RESEARCH_TASKS “research stress → STRESS_GAPS” requires this file on disk with ≥1 falsifiable gap.
- Do **not** map bare `stress_bars.json` → `notes/stress_bars.json` (duplicate/non-canonical); gold is `notes/compression_artifacts/stress_bars.json`.

---

# P1 replicate — N03 + N08

**Needle:** `OVERSEER_NICHE_P1_N03_N08_2026_09_06`  
**Run:** 2026-09-06 · role `niche_distiller` · N03 heldout **1.000** (6/6) · N08 heldout **1.000** (6/6) · full corpora 30 each  
**Landed:** `practice_n03/` + `practice_n08/` + `scripts/niche_n03_practice.py` + `scripts/niche_n08_practice.py` (N01 recipe stamp; rule baselines)

Scaffold is green. **Remaining stress** (do not prune corpora — append JSONL / tighten rules):

| ID | Niche | Gap | Evidence | Falsifier | Status |
|----|-------|-----|----------|-----------|--------|
| P1-G1 | N03 | **Twin-needle prefer-order** — land-proof twin + primary in one line; rule takes first `OVERSEER_*` / labeled Needle | Train row twin → `OVERSEER_LAND_PROOF_…` before primary | Live Done/Active with `→` twin; serve must match gold twin (or document primary-first policy) | **open** — heldout ok; live twin lines not stress-sampled |
| P1-G2 | N03 | **Prose “landed overseer:” without ticks** — bare token after colon | Stall-watch / refuse-ASN rows | Serve → exact needle; null only when no `OVERSEER_` token | **open** — rule covers labeled form; more live variants needed |
| P1-G3 | N03 | **False claimable needle** — essay claims verify passed but no OVERSEER token → must stay `null` | Anti false-`[x]` exemplars | `--serve` → `null`; never invent needle from path alone | **open** — synthetic covered; live false-`[x]` wave pending |
| P1-G4 | N08 | **Substring trap** — `test_queue_drift` in unittest FAIL log must not → `queue_drift` | Fixed in rule via `failure_type=tests` before queue_drift | Regression if order flips | **fixed** in baseline; keep as falsifier |
| P1-G5 | N08 | **Soft warn vs chicken-egg** — “soft warn ignored” must not collapse to `healthy` | Chicken-egg train row | `plan-gate soft` only → healthy; chicken-egg markers win | **fixed** in baseline; live peer_watch soft-warn samples pending |
| P1-G6 | N08 | **Improve STOPPED + “wrong namespace”** — prefer `oversight_down` over `namespace_flip` | Improve-not-24/7 row | Serve → `oversight_down` | **fixed** in baseline; dual-signal live logs still thin |
| P1-G7 | N08 | **Live peer_watch status blobs** — bottleneck ids / Cycle rows beyond synthetic 30 | Live `peer_watch` / last_cycle | Enum exact-match ≥0.90 on fresh heldout append | **open** — P2 research stress |

## P1 pass / ship rule

Heldout niche accuracy ≥ **0.90** for each of N03 / N08. Closing this needle requires practice dirs + weights + this P1 section — not silent `[x]`. Next: P2 research agents attack live traces → append miss classes here.
