#!/usr/bin/env python3
"""N01 queue_bullet_parse — P0 practice distill / eval / serve (cloneable).

OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04

Practice baseline for BITNET_NICHE_BANK P0: prove the **recipe** (schema →
train/heldout → niche accuracy → checkpoint path → serve hook) before
stamping across niches. This ships a deterministic rule baseline + ckpt under
``notes/niche_distill/practice_n01/`` — not catalog mass-train.

Neural ~10M swap: keep the same layout; replace ``predict`` weights only
(see ``notes/niche_distill/RECIPE.md``).

Usage::

    python3 scripts/niche_n01_practice.py              # train+eval+write ckpt
    python3 scripts/niche_n01_practice.py --eval-only
    python3 scripts/niche_n01_practice.py --serve '- [ ] **[kit] … Needle: `OVERSEER_X`.'
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04
NEEDLE = "OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04"
ROOT = Path(__file__).resolve().parents[1]
DISTILL = ROOT / "notes" / "niche_distill"
TRAIN_JSONL = DISTILL / "N01_queue_bullet_parse.jsonl"
HELDOUT_JSONL = DISTILL / "N01_queue_bullet_parse_heldout.jsonl"
PRACTICE_DIR = DISTILL / "practice_n01"
CKPT_JSON = PRACTICE_DIR / "checkpoint.json"
WEIGHTS_DIR = PRACTICE_DIR / "weights"
WEIGHTS_PT = WEIGHTS_DIR / "n01_queue_bullet_parse_practice.pt"

_NEEDLE_RE = re.compile(r"(OVERSEER_[A-Z0-9_]+)")
# Prefer backticked paths; else first bare scripts|notes|tests|profiles|.worktrees path.
_SCOPE_TICK_RE = re.compile(r"`((?:scripts|notes|tests|profiles|\.worktrees)/[^`]+)`")
_SCOPE_BARE_RE = re.compile(
    r"(?<![A-Za-z0-9_/])((?:scripts|notes|tests|profiles|\.worktrees)/"
    r"[A-Za-z0-9_./\-*]*?)(?=[)\s,;`]|$)"
)
# Bare COMPRESSION_*.md (or similar notes/*.md stems) → notes/<name>
_NOTES_MD_BARE_RE = re.compile(
    r"(?<![A-Za-z0-9_/])((?:COMPRESSION_[A-Z0-9_]+)\.md)\b"
)
# Bare compression artifact JSON → notes/compression_artifacts/<name>
# (canonical: COMPRESSION_TRAIN_READY.md — not notes/<name> alone).
_ARTIFACT_JSON_BARE_RE = re.compile(
    r"(?<![A-Za-z0-9_/])(stress_bars\.json)\b"
)
# Bare module ticks: `peer_watch` → scripts/peer_watch.py when present on disk.
_MOD_TICK_RE = re.compile(r"`([a-z][a-z0-9_]*)`")
_KIT_TAG_TRUE = re.compile(r"\[kit\]", re.I)
_KIT_TAG_FALSE = re.compile(
    r"\[(?:bitnet-research|efficiency-research|output-research|fact-check|"
    r"pen-test|creative|progress-monitor|company-org|oversight|hallucination|"
    r"research|compression-train|research-speed|comms-improve|flaw-research|"
    r"factory:[a-z0-9_]+)\]",
    re.I,
)
_FILE_EXTS = (".py", ".md", ".json", ".jsonl", ".sh")
_BARE_PEER_LOOP_RE = re.compile(
    r"(?:^|[\s`\[*])peer_loop(?:\.py)?(?=[\s:\]\`]|$)", re.I
)
# Factory-shaped without [kit] (P0 gold labels treat these as kit=true).
# Do NOT imply kit from [flaw-research] — research tags stay false via _KIT_TAG_FALSE.
_KIT_IMPLIED = re.compile(
    r"(?:^|\s)(?:\*\*)?(?:slim |sync WORK_QUEUE|Ensure \d+-worker)",
    re.I,
)
_CREATIVE_IMPLIED = re.compile(
    r"Discover clever|CREATIVE_BACKLOG|anchors CPT/",
    re.I,
)

# Tiny packed header so .pt is a real checkpoint file (not empty theater).
_PT_MAGIC = b"N01P"  # niche 01 practice
_PT_VERSION = 1


@dataclass(frozen=True)
class EvalReport:
    niche_id: str
    n_train: int
    n_heldout: int
    heldout_accuracy: float
    pass_bar: float
    passed: bool
    checkpoint: str
    weights: str
    needle: str


def _clean_scope_cand(c: str) -> str:
    if ".py:" in c:
        c = c.split(".py:", 1)[0] + ".py"
    if c.startswith(".worktrees/"):
        c = ".worktrees/"
    return c


def _scope_cands(seg: str) -> list[str]:
    return [
        _clean_scope_cand(m.group(1).rstrip(".,;)"))
        for m in _SCOPE_BARE_RE.finditer(seg)
    ]


def _pick_scope(cands: list[str]) -> str:
    """Prefer non-tests/ primary; include .sh; skip AC path soup when possible."""
    if not cands:
        return ""
    order = [c for c in cands if not c.startswith("tests/")] or cands
    for c in order:
        if c.endswith(_FILE_EXTS) or c.endswith("/") or "*" in c:
            return c
    return order[0]


def _mod_tick_scope(text_n: str) -> str:
    for mm in _MOD_TICK_RE.finditer(text_n):
        name = mm.group(1)
        if (ROOT / "scripts" / f"{name}.py").is_file():
            return f"scripts/{name}.py"
    return ""


def _extract_scope(text: str) -> str:
    """Primary path = title / after em-dash, before AC: — not first tests/ hit."""
    tm = _SCOPE_TICK_RE.search(text)
    if tm:
        return tm.group(1).rstrip(".,;)")
    # CPT/scripts/… → scripts/…; ./scripts/foo → scripts/foo
    text_n = text.replace("CPT/scripts/", "scripts/")
    text_n = re.sub(
        r"(?<![A-Za-z0-9_/])\./((?:scripts|notes|tests|profiles)/)",
        r"\1",
        text_n,
    )
    primary_seg = re.split(r"\bAC\s*:", text_n, maxsplit=1, flags=re.I)[0]
    em = re.search(r"[—–]\s*(.+)$", primary_seg)
    title_seg = em.group(1) if em else primary_seg

    for seg in (title_seg, primary_seg, text_n):
        picked = _pick_scope(_scope_cands(seg))
        if picked:
            return picked

    am = re.search(
        r"(?:anchors?:?\s*)((?:scripts|notes)/[A-Za-z0-9_./\-]+\.py)",
        text_n,
        re.I,
    )
    if am:
        return am.group(1)
    md = _NOTES_MD_BARE_RE.search(text_n)
    if md:
        return f"notes/{md.group(1)}"
    art = _ARTIFACT_JSON_BARE_RE.search(text_n)
    if art:
        return f"notes/compression_artifacts/{art.group(1)}"
    # Landed prose often cites `peer_watch` without scripts/… path.
    mod = _mod_tick_scope(text_n)
    if mod:
        return mod
    # RECIPE smoke: bare peer_loop: → scripts/peer_loop.py
    if _BARE_PEER_LOOP_RE.search(text_n):
        return "scripts/peer_loop.py"
    return ""


def predict(line: str) -> dict[str, Any]:
    """Rule baseline for N01 — clone target for neural ~10M swap."""
    text = (line or "").strip()
    needle_m = _NEEDLE_RE.search(text)
    needle = needle_m.group(1) if needle_m else None
    scope = _extract_scope(text)
    if _KIT_TAG_TRUE.search(text) or _KIT_IMPLIED.search(text):
        kit: bool | None = True
    elif _KIT_TAG_FALSE.search(text) or _CREATIVE_IMPLIED.search(text):
        kit = False
    elif "demoted" in text.lower() or "ASN th" in text:
        kit = None
    else:
        kit = None
    return {"kit": kit, "scope": scope, "needle": needle}


def _exact_match(pred: dict[str, Any], gold: Any) -> bool:
    if not isinstance(gold, dict):
        return False
    # Normalize nullish scope.
    g_scope = gold.get("scope") or ""
    p_scope = pred.get("scope") or ""
    return (
        pred.get("kit") == gold.get("kit")
        and p_scope == g_scope
        and pred.get("needle") == gold.get("needle")
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        rows.append(json.loads(raw))
    return rows


def split_train_heldout(
    rows: list[dict[str, Any]], *, hold_frac: float = 0.2
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Deterministic ~20% heldout (every 5th row) — recipe stamp, not RNG."""
    heldout: list[dict[str, Any]] = []
    train: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        if (i % 5) == 4:  # ~20%
            heldout.append(row)
        else:
            train.append(row)
    if not heldout and rows:
        heldout = [rows[-1]]
        train = rows[:-1]
    _ = hold_frac  # documented in RECIPE; fixed stride for cloneability
    return train, heldout


def write_heldout(rows: list[dict[str, Any]]) -> None:
    HELDOUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with HELDOUT_JSONL.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_checkpoint(*, n_train: int, n_heldout: int, accuracy: float) -> None:
    """Persist practice ckpt + weights/.pt under niche_distill (done bar)."""
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    rules = {
        "kind": "n01_rule_baseline",
        "version": _PT_VERSION,
        "needle": NEEDLE,
        "predict": "scripts/niche_n01_practice.py:predict",
        "grain": "~10M neural swap keeps this layout",
    }
    payload = json.dumps(rules, separators=(",", ":")).encode("utf-8")
    # Packed .pt: magic + version + len + utf-8 JSON rules (torch-free serve).
    blob = _PT_MAGIC + struct.pack(">HI", _PT_VERSION, len(payload)) + payload
    WEIGHTS_PT.write_bytes(blob)
    manifest = {
        "needle": NEEDLE,
        "niche_id": "N01",
        "niche": "queue_bullet_parse",
        "checkpoint": str(CKPT_JSON.relative_to(ROOT)),
        "weights": str(WEIGHTS_PT.relative_to(ROOT)),
        "train_jsonl": str(TRAIN_JSONL.relative_to(ROOT)),
        "heldout_jsonl": str(HELDOUT_JSONL.relative_to(ROOT)),
        "n_train": n_train,
        "n_heldout": n_heldout,
        "heldout_accuracy": round(accuracy, 4),
        "pass_bar": 0.90,
        "passed": accuracy >= 0.90,
        "serve": "python3 scripts/niche_n01_practice.py --serve '<line>'",
        "recipe": "notes/niche_distill/RECIPE.md",
    }
    CKPT_JSON.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def load_weights_pt(path: Path = WEIGHTS_PT) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw[:4] != _PT_MAGIC:
        raise ValueError(f"bad practice .pt magic: {path}")
    ver, n = struct.unpack(">HI", raw[4:10])
    if ver != _PT_VERSION:
        raise ValueError(f"unsupported practice .pt version {ver}")
    return json.loads(raw[10 : 10 + n].decode("utf-8"))


def eval_heldout(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    ok = 0
    for row in rows:
        pred = predict(str(row.get("input") or ""))
        if _exact_match(pred, row.get("output")):
            ok += 1
    return ok / len(rows)


def run_train_eval(*, write: bool = True) -> EvalReport:
    rows = load_jsonl(TRAIN_JSONL)
    train, heldout = split_train_heldout(rows)
    if write:
        write_heldout(heldout)
    acc = eval_heldout(heldout)
    if write:
        write_checkpoint(n_train=len(train), n_heldout=len(heldout), accuracy=acc)
    return EvalReport(
        niche_id="N01",
        n_train=len(train),
        n_heldout=len(heldout),
        heldout_accuracy=acc,
        pass_bar=0.90,
        passed=acc >= 0.90,
        checkpoint=str(CKPT_JSON.relative_to(ROOT)),
        weights=str(WEIGHTS_PT.relative_to(ROOT)),
        needle=NEEDLE,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eval-only", action="store_true", help="score heldout; no rewrite")
    p.add_argument("--serve", metavar="LINE", help="parse one WORK_QUEUE line → JSON")
    p.add_argument("--json", action="store_true", help="print EvalReport as JSON")
    args = p.parse_args(argv)

    if args.serve is not None:
        print(json.dumps(predict(args.serve), ensure_ascii=False))
        return 0

    if args.eval_only:
        if HELDOUT_JSONL.is_file():
            heldout = load_jsonl(HELDOUT_JSONL)
        else:
            _, heldout = split_train_heldout(load_jsonl(TRAIN_JSONL))
        acc = eval_heldout(heldout)
        report = EvalReport(
            niche_id="N01",
            n_train=0,
            n_heldout=len(heldout),
            heldout_accuracy=acc,
            pass_bar=0.90,
            passed=acc >= 0.90,
            checkpoint=str(CKPT_JSON.relative_to(ROOT)),
            weights=str(WEIGHTS_PT.relative_to(ROOT)),
            needle=NEEDLE,
        )
    else:
        report = run_train_eval(write=True)
        # Prove .pt loads.
        meta = load_weights_pt()
        assert meta.get("needle") == NEEDLE, meta

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(
            f"N01 practice {NEEDLE}\n"
            f"  heldout={report.n_heldout} acc={report.heldout_accuracy:.3f} "
            f"pass_bar={report.pass_bar} passed={report.passed}\n"
            f"  checkpoint={report.checkpoint}\n"
            f"  weights={report.weights}"
        )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
