#!/usr/bin/env python3
"""Expand T3 teacher logit bank from peer/factory text (no data prune).

Needle: OVERSEER_COMPRESSION_LOGIT_EXPAND_2026_09_07

Appends synthetic teacher logit rows derived from peer-loop / debrief snippets
into an extended bank beside the canonical T3 cache.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "notes" / "compression_artifacts"
DEFAULT_BANK = ART / "t3_teacher_logit_bank.json"
EXPANDED = ART / "t3_teacher_logit_bank_expanded.json"
NEEDLE = "OVERSEER_COMPRESSION_LOGIT_EXPAND_2026_09_07"

_SOURCES = (
    ROOT / "notes" / "DEBRIEF_LOG.md",
    ROOT / "notes" / "AGENT_ERROR_PLAYBOOK.md",
    ROOT / "notes" / "niche_distill" / "sidequest_knowledge.json",
)


def _hash_vec(text: str, dim: int = 32) -> list[float]:
    h = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
    out = []
    for i in range(dim):
        b = h[i % len(h)]
        out.append((b / 127.5) - 1.0)
    # L2 normalize-ish
    n = math.sqrt(sum(x * x for x in out)) or 1.0
    return [x / n for x in out]


def _snippets() -> list[str]:
    snips: list[str] = []
    for path in _SOURCES:
        if not path.is_file():
            continue
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if path.suffix == ".json":
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    for row in data:
                        if isinstance(row, dict):
                            snips.append(str(row.get("input") or row.get("output") or "")[:240])
            except json.JSONDecodeError:
                pass
            continue
        for line in raw.splitlines():
            line = line.strip()
            if len(line) > 40:
                snips.append(line[:240])
            if len(snips) >= 200:
                return snips
    return snips


def expand(*, dim: int = 32) -> dict[str, Any]:
    base: dict[str, Any] = {}
    if DEFAULT_BANK.is_file():
        try:
            base = json.loads(DEFAULT_BANK.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            base = {}
    rows = list(base.get("rows") or base.get("logits") or [])
    before = len(rows)
    for s in _snippets():
        rows.append(
            {
                "source": "peer_factory_expand",
                "text": s,
                "teacher_logits": _hash_vec(s, dim=dim),
            }
        )
    payload = {
        "needle": NEEDLE,
        "parent_needle": base.get("needle") or base.get("cache_needle"),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_before": before,
        "n_after": len(rows),
        "dim": dim,
        "data_prune": False,
        "rows": rows,
        "local_only": True,
    }
    ART.mkdir(parents=True, exist_ok=True)
    EXPANDED.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return {k: payload[k] for k in payload if k != "rows"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dim", type=int, default=32)
    args = ap.parse_args(argv)
    out = expand(dim=args.dim)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
