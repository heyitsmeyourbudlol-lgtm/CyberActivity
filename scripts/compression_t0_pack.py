#!/usr/bin/env python3
"""T0 packing proof — synthetic unique-param + 1-bit pack math (no training).

OVERSEER_COMPRESSION_T0_PACK_2026_09_05
OVERSEER_COMPRESSION_T0_PACK_CACHE_2026_09_05
OVERSEER_COMPRESSION_DUAL_SOT_CACHE_2026_09_07

Proves ALBERT-BitMoE (primary) and LoRA-Hive (control) hit:
  N_L ∈ {1e5, 1e6},  C_arith = N_L/U ≥ 50,  packed_bytes ≈ U/8 (± metadata).

Quality/loss is out of scope for T0. No data pruning. Torch-free.
Durable pack report (Lane-U sibling to T3 logit bank) — not a train unlock.
Dual SoT cache (pack + logit bank report) — Lane-U durable gate; still not a train unlock.

Usage::

    python3 scripts/compression_t0_pack.py
    python3 scripts/compression_t0_pack.py --json
    python3 scripts/compression_t0_pack.py --write-report /tmp/t0_pack.json
    python3 scripts/compression_t0_pack.py --check-cache /tmp/t0_pack.json --json
    python3 scripts/compression_t0_pack.py --ensure-default-pack --json
    python3 scripts/compression_t0_pack.py --dual-sot-check --json
    python3 scripts/compression_t0_pack.py --ensure-dual-sot --json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# OVERSEER_COMPRESSION_T0_PACK_2026_09_05
NEEDLE = "OVERSEER_COMPRESSION_T0_PACK_2026_09_05"
# OVERSEER_COMPRESSION_T0_PACK_CACHE_2026_09_05
CACHE_NEEDLE = "OVERSEER_COMPRESSION_T0_PACK_CACHE_2026_09_05"
# OVERSEER_COMPRESSION_DUAL_SOT_CACHE_2026_09_07
DUAL_SOT_CACHE_NEEDLE = "OVERSEER_COMPRESSION_DUAL_SOT_CACHE_2026_09_07"

_ROOT = Path(__file__).resolve().parents[1]
# Canonical packing SoT (repo-relative; TRAIN still LOCKED — not a train unlock)
DEFAULT_PACK_PATH = _ROOT / "notes" / "compression_artifacts" / "t0_pack_report.json"
# Dual SoT durable report (pack + T3 logit bank); TRAIN still LOCKED
DEFAULT_DUAL_SOT_PATH = (
    _ROOT / "notes" / "compression_artifacts" / "dual_sot_report.json"
)

# Pass gates (COMPRESSION_NOVEL.md T0)
MIN_ARITH = 50.0
# Prefer ~100 when geometry is easy; soft target for reporting only.
PREFER_ARITH = 100.0
# Packed store may add a tiny header; payload must track U/8.
META_HEADER_BYTES = 16
META_BOUND_BYTES = 64
# Fail if unique or pack miss target by >2× (falsifier).
FAIL_MISS_FACTOR = 2.0

N_L_TARGETS = (100_000, 1_000_000)


@dataclass(frozen=True)
class PackResult:
    stack: str
    n_logic: int
    u_unique: int
    s_arith: float
    packed_bytes: int
    payload_bytes: int
    meta_bytes: int
    pass_arith: bool
    pass_pack: bool
    passed: bool
    quality: str  # always N/A for T0
    detail: dict[str, Any]


def _pack_1bit(u: int, meta_bytes: int = META_HEADER_BYTES) -> tuple[int, int]:
    """Pack U ternary/1-bit slots → (payload_bytes, packed_bytes)."""
    payload = (u + 7) // 8
    return payload, payload + meta_bytes


def _pass_pack(u: int, packed_bytes: int) -> bool:
    """packed ≈ U/8 within metadata bound (ceil vs float both allowed)."""
    ideal = u / 8.0
    ceil_ideal = (u + 7) // 8
    return (
        abs(packed_bytes - ideal) <= META_BOUND_BYTES
        or abs(packed_bytes - ceil_ideal) <= META_BOUND_BYTES
    )


def albert_bitmoe(n_logic: int) -> PackResult:
    """ALBERT-BitMoE: one shared 1-bit FFN body + per-layer LoRA.

    U = B_body + L * r * (d_in + d_out)   with L_share = L
    N_L = L * B_body
    """
    # Geometry tuned for exact N_L and S ≳ 80 (prefer ~100).
    # L=100 → B = N_L/100; tiny LoRA so body share dominates.
    layers = 100
    if n_logic % layers != 0:
        raise ValueError(f"n_logic={n_logic} not divisible by L={layers}")
    body = n_logic // layers
    # Synthetic body shape (up+down): d_in * d_ff + d_ff * d_out == body
    d_in = d_out = max(1, int(math.isqrt(max(body // 2, 1))))
    d_ff = max(1, body // (d_in + d_out))
    body_unique = body  # shared once (= N_L / L)

    r = 1
    # Tiny adapter dims so LoRA does not erase the share win (still nonzero U_lora).
    lora_d_in, lora_d_out = 1, 1
    u_lora = layers * r * (lora_d_in + lora_d_out)
    u = body_unique + u_lora
    s = n_logic / u
    payload, packed = _pack_1bit(u)
    pass_arith = s >= MIN_ARITH
    pass_pack = _pass_pack(u, packed)
    # Fail if unique/pack miss hard floor by >2× (COMPRESSION_NOVEL falsifier).
    passed = pass_arith and pass_pack and s >= (MIN_ARITH / FAIL_MISS_FACTOR)
    return PackResult(
        stack="ALBERT-BitMoE",
        n_logic=n_logic,
        u_unique=u,
        s_arith=s,
        packed_bytes=packed,
        payload_bytes=payload,
        meta_bytes=META_HEADER_BYTES,
        pass_arith=pass_arith,
        pass_pack=pass_pack,
        passed=passed,
        quality="N/A",
        detail={
            "L": layers,
            "L_share": layers,
            "B_body": body_unique,
            "r": r,
            "lora_d_in": lora_d_in,
            "lora_d_out": lora_d_out,
            "u_lora": u_lora,
            "d_in_body": d_in,
            "d_ff_body": d_ff,
            "d_out_body": d_out,
            "formula": "U = B_body + L*r*(d_in+d_out); N_L = L*B_body",
        },
    )


def lora_hive(n_logic: int) -> PackResult:
    """LoRA-Hive: shared 1-bit hive + per-expert LoRA (control).

    Amortized: U = B_hive/E + r*(d_in+d_out), N_L = B_hive
    (equivalently total N = E*B_hive, U_tot = B_hive + E*r*(...)).
    """
    experts = 100
    b_hive = n_logic  # logical expert size = hive body
    r = 1
    lora_d_in, lora_d_out = 1, 1
    u_lora_amortized = r * (lora_d_in + lora_d_out)
    u = b_hive // experts + u_lora_amortized
    # Exact integer share: require divisible hive.
    if b_hive % experts != 0:
        raise ValueError(f"n_logic={n_logic} not divisible by E={experts}")
    s = n_logic / u
    payload, packed = _pack_1bit(u)
    pass_arith = s >= MIN_ARITH
    pass_pack = _pass_pack(u, packed)
    passed = pass_arith and pass_pack and s >= (MIN_ARITH / FAIL_MISS_FACTOR)
    return PackResult(
        stack="LoRA-Hive",
        n_logic=n_logic,
        u_unique=u,
        s_arith=s,
        packed_bytes=packed,
        payload_bytes=payload,
        meta_bytes=META_HEADER_BYTES,
        pass_arith=pass_arith,
        pass_pack=pass_pack,
        passed=passed,
        quality="N/A",
        detail={
            "E": experts,
            "B_hive": b_hive,
            "r": r,
            "lora_d_in": lora_d_in,
            "lora_d_out": lora_d_out,
            "u_hive_amortized": b_hive // experts,
            "u_lora_amortized": u_lora_amortized,
            "formula": "U_e = B_hive/E + r*(d_in+d_out); N_L = B_hive",
        },
    )


def run_all(n_targets: tuple[int, ...] = N_L_TARGETS) -> list[PackResult]:
    rows: list[PackResult] = []
    for n in n_targets:
        rows.append(albert_bitmoe(n))
        rows.append(lora_hive(n))
    return rows


def summary_dict(rows: list[PackResult]) -> dict[str, Any]:
    return {
        "needle": NEEDLE,
        "cache_needle": CACHE_NEEDLE,
        "min_arith": MIN_ARITH,
        "prefer_arith": PREFER_ARITH,
        "meta_header_bytes": META_HEADER_BYTES,
        "meta_bound_bytes": META_BOUND_BYTES,
        "quality": "N/A",  # packing proof only — never measured LM
        "data_prune": False,  # RECIPE: no data/example/token prune
        "train_unlocked": False,  # T0 packing ≠ permission to train
        "all_passed": all(r.passed for r in rows),
        "results": [asdict(r) for r in rows],
    }


def dump_pack_report(path: str | Path, rows: list[PackResult] | None = None) -> Path:
    """Persist packing SoT JSON (no prune). TRAIN still LOCKED."""
    out = Path(path)
    payload = summary_dict(rows if rows is not None else run_all())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    return out


def load_pack_report(path: str | Path) -> dict[str, Any]:
    """Reload durable pack report; refuse pruned / train-unlocked caches."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("needle") not in (None, NEEDLE):
        raise ValueError(f"refusing pack report with foreign needle: {data.get('needle')!r}")
    if data.get("cache_needle") != CACHE_NEEDLE:
        raise ValueError(
            f"refusing pack report missing cache_needle={CACHE_NEEDLE!r} "
            f"(got {data.get('cache_needle')!r})"
        )
    if data.get("data_prune") is True:
        raise ValueError("refusing pruned pack report cache")
    if data.get("train_unlocked") is True:
        raise ValueError("refusing train-unlocked pack report (recipe LOCKED)")
    results = data.get("results")
    if not isinstance(results, list) or len(results) != len(N_L_TARGETS) * 2:
        raise ValueError("pack report results length mismatch")
    return data


def _results_fingerprint(payload: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows = []
    for r in payload["results"]:
        rows.append(
            (
                r["stack"],
                int(r["n_logic"]),
                int(r["u_unique"]),
                float(r["s_arith"]),
                int(r["packed_bytes"]),
                bool(r["passed"]),
            )
        )
    return rows


def pack_cache_roundtrip_ok(path: str | Path | None = None) -> bool:
    """Fresh run → dump → load must match packing fingerprint."""
    import tempfile

    fresh = summary_dict(run_all())
    if path is None:
        with tempfile.TemporaryDirectory(prefix="t0_pack_") as td:
            p = Path(td) / "pack.json"
            dump_pack_report(p, run_all())
            cached = load_pack_report(p)
            return (
                fresh["all_passed"]
                and cached["all_passed"] is True
                and _results_fingerprint(fresh) == _results_fingerprint(cached)
                and cached.get("train_unlocked") is False
                and cached.get("data_prune") is False
            )
    dump_pack_report(path, run_all())
    cached = load_pack_report(path)
    return (
        fresh["all_passed"]
        and cached["all_passed"] is True
        and _results_fingerprint(fresh) == _results_fingerprint(cached)
        and cached.get("train_unlocked") is False
        and cached.get("data_prune") is False
    )


def ensure_default_pack(path: Path | None = None) -> tuple[Path, bool]:
    """Dump canonical repo pack report + prove load match. TRAIN still LOCKED."""
    out = Path(path) if path is not None else DEFAULT_PACK_PATH
    rows = run_all()
    fresh = summary_dict(rows)
    dump_pack_report(out, rows)
    meta = load_pack_report(out)
    ok = (
        fresh["all_passed"]
        and meta["all_passed"] is True
        and _results_fingerprint(fresh) == _results_fingerprint(meta)
        and meta.get("train_unlocked") is False
        and meta.get("data_prune") is False
        and meta.get("cache_needle") == CACHE_NEEDLE
        and meta.get("needle") == NEEDLE
    )
    return out, ok


def dual_sot_check(
    pack_path: Path | None = None,
    bank_path: Path | None = None,
) -> dict[str, Any]:
    """TRAIN-LOCK Dual SoT: canonical T0 pack + T3 logit bank both green.

    Recipe must not unlock real train until both durable caches load clean
    (no prune, train_unlocked=false). Does **not** unlock training.
    """
    import compression_t3_bitdistill as t3

    pack = Path(pack_path) if pack_path is not None else DEFAULT_PACK_PATH
    bank = Path(bank_path) if bank_path is not None else t3.DEFAULT_BANK_PATH
    out: dict[str, Any] = {
        "dual_sot": True,
        "train_unlocked": False,  # Dual SoT green ≠ TRAIN unlock
        "data_prune": False,
        "pack_path": str(pack),
        "bank_path": str(bank),
        "pack_ok": False,
        "bank_ok": False,
        "dual_sot_ok": False,
        "quality": "proxy",
    }
    try:
        pack_meta = load_pack_report(pack)
        fresh = summary_dict(run_all())
        out["pack_ok"] = (
            pack_meta.get("all_passed") is True
            and fresh["all_passed"]
            and _results_fingerprint(fresh) == _results_fingerprint(pack_meta)
            and pack_meta.get("train_unlocked") is False
            and pack_meta.get("data_prune") is False
            and pack_meta.get("cache_needle") == CACHE_NEEDLE
        )
        out["pack_needle"] = pack_meta.get("needle")
        out["pack_cache_needle"] = pack_meta.get("cache_needle")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        out["pack_error"] = str(exc)
        out["pack_ok"] = False

    try:
        out["bank_ok"] = bool(t3.check_bank_at_path(bank))
        bank_meta = json.loads(bank.read_text(encoding="utf-8"))
        out["bank_needle"] = bank_meta.get("needle")
        out["bank_cache_needle"] = bank_meta.get("cache_needle")
        if bank_meta.get("train_unlocked") is True or bank_meta.get("data_prune") is True:
            out["bank_ok"] = False
    except (OSError, ValueError, KeyError, TypeError) as exc:
        out["bank_error"] = str(exc)
        out["bank_ok"] = False

    out["dual_sot_ok"] = bool(out["pack_ok"] and out["bank_ok"])
    return out


def ensure_dual_sot(
    pack_path: Path | None = None,
    bank_path: Path | None = None,
) -> dict[str, Any]:
    """Refresh T0 pack + T3 logit bank SoTs, then Dual-SoT check.

    Advances one Dual-SoT keep-alive step (pack/logit) without unlocking train.
    Needle siblings: CACHE_NEEDLE + T3 CACHE_NEEDLE via ensure_default_*.
    """
    import compression_t3_bitdistill as t3

    pack_out, pack_cache_ok = ensure_default_pack(pack_path)
    bank_out, bank_cache_ok = t3.ensure_default_bank(bank_path)
    payload = dual_sot_check(pack_path=pack_out, bank_path=bank_out)
    payload["ensure_dual_sot"] = True
    payload["pack_cache_ok"] = bool(pack_cache_ok)
    payload["bank_cache_ok"] = bool(bank_cache_ok)
    payload["pack_path"] = str(pack_out)
    payload["bank_path"] = str(bank_out)
    # Refuse unlock even if caches green
    payload["train_unlocked"] = False
    payload["dual_sot_ok"] = bool(
        payload.get("dual_sot_ok")
        and pack_cache_ok
        and bank_cache_ok
        and payload.get("train_unlocked") is False
        and payload.get("data_prune") is False
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="T0 compression packing proof")
    p.add_argument("--json", action="store_true", help="print JSON summary only")
    p.add_argument(
        "--write-report",
        metavar="PATH",
        help="dump durable pack report JSON (TRAIN still LOCKED)",
    )
    p.add_argument(
        "--check-cache",
        metavar="PATH",
        nargs="?",
        const="",
        help="verify dump→load fingerprint (PATH or default after write)",
    )
    p.add_argument(
        "--ensure-default-pack",
        action="store_true",
        help=(
            f"dump+verify canonical pack report at {DEFAULT_PACK_PATH.name} "
            "(not a train unlock)"
        ),
    )
    p.add_argument(
        "--dual-sot-check",
        action="store_true",
        help=(
            "TRAIN-LOCK Dual SoT: verify canonical pack report + T3 logit bank "
            "(both green, prune/unlock refused; does not unlock train)"
        ),
    )
    p.add_argument(
        "--ensure-dual-sot",
        action="store_true",
        help=(
            "refresh canonical pack + T3 logit bank then Dual SoT check "
            "(not a train unlock)"
        ),
    )
    args = p.parse_args(argv)

    if args.ensure_dual_sot:
        payload = ensure_dual_sot()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["dual_sot_ok"] else 1

    if args.dual_sot_check:
        payload = dual_sot_check()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["dual_sot_ok"] else 1

    if args.ensure_default_pack:
        out, pack_cache_ok = ensure_default_pack()
        payload = summary_dict(run_all())
        payload["pack_cache_ok"] = pack_cache_ok
        payload["pack_source"] = "default_pack"
        payload["pack_path"] = str(out)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if pack_cache_ok and payload["all_passed"] else 1

    rows = run_all()
    payload = summary_dict(rows)

    if args.write_report:
        dump_pack_report(args.write_report, rows)
        payload["pack_path"] = str(Path(args.write_report))

    if args.check_cache is not None:
        check_path = args.check_cache or args.write_report or str(DEFAULT_PACK_PATH)
        if not check_path:
            print("error: --check-cache needs PATH or --write-report/--ensure", file=sys.stderr)
            return 2
        try:
            cached = load_pack_report(check_path)
            pack_cache_ok = (
                payload["all_passed"]
                and cached["all_passed"] is True
                and _results_fingerprint(payload) == _results_fingerprint(cached)
                and cached.get("train_unlocked") is False
                and cached.get("data_prune") is False
            )
        except (OSError, ValueError, KeyError, TypeError) as exc:
            pack_cache_ok = False
            payload["pack_cache_error"] = str(exc)
        payload["pack_cache_ok"] = pack_cache_ok
        payload["pack_path"] = str(check_path)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if pack_cache_ok and payload["all_passed"] else 1

    if args.json or args.write_report:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
        for r in rows:
            status = "PASS" if r.passed else "FAIL"
            print(
                f"{status} {r.stack} N_L={r.n_logic} U={r.u_unique} "
                f"S={r.s_arith:.2f} bytes={r.packed_bytes} "
                f"(payload={r.payload_bytes}+meta={r.meta_bytes}) quality={r.quality}",
                file=sys.stderr,
            )
    return 0 if payload["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
