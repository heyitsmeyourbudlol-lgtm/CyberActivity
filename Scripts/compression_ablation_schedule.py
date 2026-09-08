#!/usr/bin/env python3
"""Share×rank ablation schedule — OA screen → successive halving / Hyperband.

OVERSEER_COMPRESSION_ABLATION_SCHEDULE_2026_09_06

Research-speed S03 / S16 / S32 (notes/RESEARCH_SPEED_TRAINING.md).
Torch-free. Emits dry-run brackets for future T1–T2-style (k, r) screens.
Does **not** change the LOCKED recipe, unlock train, or block rung0.

Usage::

    python3 scripts/compression_ablation_schedule.py
    python3 scripts/compression_ablation_schedule.py --json
    python3 scripts/compression_ablation_schedule.py --mode oa --write
    python3 scripts/compression_ablation_schedule.py --mode hyperband --eta 3 --json
    python3 scripts/compression_ablation_schedule.py --mode oa-then-hb --write
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

# OVERSEER_COMPRESSION_ABLATION_SCHEDULE_2026_09_06
NEEDLE = "OVERSEER_COMPRESSION_ABLATION_SCHEDULE_2026_09_06"

# Default grids aligned with T1/T2 toys (schedule only — not a recipe rewrite).
K_LEVELS_DEFAULT = (2, 4, 8, 16, 50, 100, 125, 200)
R_LEVELS_DEFAULT = (1, 2, 4, 8, 16, 32)
# Early resource / epoch proxy levels for 3-factor OA (S32 OATM).
E_LEVELS_DEFAULT = (1, 3, 9)

ETA_DEFAULT = 3
MAX_RESOURCE_DEFAULT = 81  # 3^4 — Hyperband R
ARTIFACT_REL = Path("notes/compression_artifacts/ablation_schedule.json")
BLOCKS_RUNG0 = False
TRAIN_UNLOCKED = False
RECIPE_LOCKED = True


@dataclass(frozen=True)
class ConfigPoint:
    """One (k, r[, E]) candidate in a schedule."""

    k: int
    r: int
    e: int | None = None
    config_id: str = ""

    def label(self) -> str:
        if self.e is None:
            return f"k={self.k},r={self.r}"
        return f"k={self.k},r={self.r},E={self.e}"


@dataclass(frozen=True)
class BracketRound:
    round_idx: int
    resource: int
    n_configs: int
    configs: tuple[str, ...]


@dataclass(frozen=True)
class Bracket:
    bracket_id: int
    n0: int
    r0: int
    s: int
    eta: int
    rounds: tuple[BracketRound, ...]
    total_resource_units: int


def _pick_levels(values: Sequence[int], n: int) -> tuple[int, ...]:
    """Evenly subsample ``values`` down to ``n`` levels (inclusive endpoints)."""
    if n <= 0:
        raise ValueError("n must be positive")
    vals = tuple(int(v) for v in values)
    if n >= len(vals):
        return vals
    if n == 1:
        return (vals[len(vals) // 2],)
    out: list[int] = []
    for i in range(n):
        idx = round(i * (len(vals) - 1) / (n - 1))
        out.append(vals[idx])
    # Dedupe while preserving order (grids can collapse when short).
    seen: set[int] = set()
    uniq: list[int] = []
    for v in out:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    while len(uniq) < n:
        for v in vals:
            if v not in seen:
                seen.add(v)
                uniq.append(v)
            if len(uniq) >= n:
                break
    return tuple(uniq[:n])


def taguchi_l9() -> tuple[tuple[int, int, int], ...]:
    """Classic Taguchi L9 (3^4 reduced) — first three columns for (k, r, E).

    Levels are 0..2. Nine runs vs 27 full factorial (S32 OATM screen).
    """
    return (
        (0, 0, 0),
        (0, 1, 1),
        (0, 2, 2),
        (1, 0, 1),
        (1, 1, 2),
        (1, 2, 0),
        (2, 0, 2),
        (2, 1, 0),
        (2, 2, 1),
    )


def orthogonal_array_screen(
    k_levels: Sequence[int] = K_LEVELS_DEFAULT,
    r_levels: Sequence[int] = R_LEVELS_DEFAULT,
    e_levels: Sequence[int] = E_LEVELS_DEFAULT,
    *,
    n_levels: int = 3,
) -> list[ConfigPoint]:
    """OATM / Taguchi L9 screen over share×rank×resource (S03/S32).

    Subsamples each factor to ``n_levels`` (default 3), maps L9 indices, and
    returns balanced (k, r, E) points — far fewer than a full k×r×E grid.
    """
    if n_levels != 3:
        raise ValueError("only L9 (n_levels=3) is implemented")
    ks = _pick_levels(k_levels, n_levels)
    rs = _pick_levels(r_levels, n_levels)
    es = _pick_levels(e_levels, n_levels)
    points: list[ConfigPoint] = []
    for i, (ik, ir, ie) in enumerate(taguchi_l9()):
        pt = ConfigPoint(
            k=ks[ik],
            r=rs[ir],
            e=es[ie],
            config_id=f"oa{i}",
        )
        points.append(pt)
    return points


def full_grid(
    k_levels: Sequence[int] = K_LEVELS_DEFAULT,
    r_levels: Sequence[int] = R_LEVELS_DEFAULT,
) -> list[ConfigPoint]:
    """Full factorial share×rank grid (baseline cost reference)."""
    out: list[ConfigPoint] = []
    i = 0
    for k in k_levels:
        for r in r_levels:
            out.append(ConfigPoint(k=int(k), r=int(r), e=None, config_id=f"g{i}"))
            i += 1
    return out


def successive_halving_bracket(
    configs: Sequence[ConfigPoint],
    *,
    max_resource: int,
    eta: int = ETA_DEFAULT,
    bracket_id: int = 0,
    s: int = 0,
) -> Bracket:
    """One successive-halving bracket (Jamieson & Talwalkar; Hyperband inner loop).

    Starts with ``len(configs)`` arms at resource r0 = max_resource / eta^s,
    keeps top 1/eta each round until one (or few) remain.
    Dry-run: no metrics — cull order is schedule order (deterministic placeholder).
    """
    if eta < 2:
        raise ValueError("eta must be >= 2")
    if max_resource < 1:
        raise ValueError("max_resource must be >= 1")
    n = len(configs)
    if n < 1:
        raise ValueError("configs must be non-empty")

    r0 = max(1, int(max_resource / (eta**s)))
    alive: list[ConfigPoint] = list(configs)
    rounds: list[BracketRound] = []
    total = 0
    round_idx = 0
    # Number of SH rounds ≈ floor(log_eta n) + 1, capped by s+1 in Hyperband.
    max_rounds = max(1, s + 1)
    while alive and round_idx < max_rounds:
        resource = int(r0 * (eta**round_idx))
        resource = min(resource, max_resource)
        n_i = len(alive)
        total += n_i * resource
        rounds.append(
            BracketRound(
                round_idx=round_idx,
                resource=resource,
                n_configs=n_i,
                configs=tuple(c.config_id for c in alive),
            )
        )
        keep = max(1, int(math.floor(n_i / eta)))
        if keep >= n_i and round_idx > 0:
            break
        # Dry-run cull: keep first ``keep`` (stable schedule; real runs rank by loss).
        alive = alive[:keep]
        round_idx += 1
        if keep == 1 and round_idx >= max_rounds:
            break

    return Bracket(
        bracket_id=bracket_id,
        n0=n,
        r0=r0,
        s=s,
        eta=eta,
        rounds=tuple(rounds),
        total_resource_units=total,
    )


def hyperband_brackets(
    configs: Sequence[ConfigPoint],
    *,
    max_resource: int = MAX_RESOURCE_DEFAULT,
    eta: int = ETA_DEFAULT,
) -> list[Bracket]:
    """Hyperband outer loop: s = s_max .. 0 brackets with η cull (S16).

    Each bracket gets a fresh shuffle-free slice of ``configs`` (round-robin
    take of n_i arms) so dry-run stays deterministic.
    """
    if eta < 2:
        raise ValueError("eta must be >= 2")
    s_max = int(math.floor(math.log(max_resource) / math.log(eta)))
    brackets: list[Bracket] = []
    pool = list(configs)
    if not pool:
        raise ValueError("configs must be non-empty")

    for bracket_id, s in enumerate(range(s_max, -1, -1)):
        n = int(math.ceil((s_max + 1) / (s + 1) * (eta**s)))
        # Cycle-take from pool so every arm can appear across brackets.
        taken: list[ConfigPoint] = []
        for i in range(n):
            base = pool[i % len(pool)]
            taken.append(
                ConfigPoint(
                    k=base.k,
                    r=base.r,
                    e=base.e,
                    config_id=f"hb{bracket_id}_{i}_{base.config_id}",
                )
            )
        brackets.append(
            successive_halving_bracket(
                taken,
                max_resource=max_resource,
                eta=eta,
                bracket_id=bracket_id,
                s=s,
            )
        )
    return brackets


def schedule_cost_units(brackets: Iterable[Bracket]) -> int:
    return sum(b.total_resource_units for b in brackets)


def build_schedule(
    *,
    mode: str = "oa-then-hb",
    k_levels: Sequence[int] = K_LEVELS_DEFAULT,
    r_levels: Sequence[int] = R_LEVELS_DEFAULT,
    e_levels: Sequence[int] = E_LEVELS_DEFAULT,
    eta: int = ETA_DEFAULT,
    max_resource: int = MAX_RESOURCE_DEFAULT,
) -> dict[str, Any]:
    """Build dry-run ablation schedule JSON payload."""
    mode_key = mode.strip().lower().replace("_", "-")
    grid = full_grid(k_levels, r_levels)
    full_n = len(grid)
    full_cost_proxy = full_n * max_resource  # naive: every cell at R

    oa_points = orthogonal_array_screen(k_levels, r_levels, e_levels)
    brackets: list[Bracket] = []
    screen: list[ConfigPoint] = []

    if mode_key == "oa":
        screen = oa_points
        # Single cheap SH on OA set (optional structure for consumers).
        brackets = [
            successive_halving_bracket(
                oa_points,
                max_resource=max_resource,
                eta=eta,
                bracket_id=0,
                s=int(math.floor(math.log(max(len(oa_points), 1)) / math.log(eta))),
            )
        ]
    elif mode_key in ("sh", "successive-halving"):
        screen = list(grid)
        s = int(math.floor(math.log(max(len(grid), 1)) / math.log(eta)))
        brackets = [
            successive_halving_bracket(
                grid,
                max_resource=max_resource,
                eta=eta,
                bracket_id=0,
                s=s,
            )
        ]
    elif mode_key in ("hyperband", "hb"):
        screen = list(grid)
        brackets = hyperband_brackets(grid, max_resource=max_resource, eta=eta)
    elif mode_key in ("oa-then-hb", "oa-hb", "oatm"):
        screen = oa_points
        # Promote OA (k,r) unique pairs into Hyperband arms (drop E for HB resource).
        seen: set[tuple[int, int]] = set()
        arms: list[ConfigPoint] = []
        for p in oa_points:
            key = (p.k, p.r)
            if key in seen:
                continue
            seen.add(key)
            arms.append(ConfigPoint(k=p.k, r=p.r, e=None, config_id=p.config_id))
        brackets = hyperband_brackets(arms, max_resource=max_resource, eta=eta)
    else:
        raise ValueError(
            f"unknown mode={mode!r}; use oa|sh|hyperband|oa-then-hb"
        )

    sched_cost = schedule_cost_units(brackets)
    speedup = (full_cost_proxy / sched_cost) if sched_cost else None

    return {
        "needle": NEEDLE,
        "mode": mode_key,
        "dry_run": True,
        "blocks_rung0": BLOCKS_RUNG0,
        "train_unlocked": TRAIN_UNLOCKED,
        "recipe_locked": RECIPE_LOCKED,
        "refs": {
            "S03": "orthogonal array / successive halving for (k,r)",
            "S16": "Hyperband-style brackets eta cull after OA",
            "S32": "OATM / Taguchi L9 multi-factor k,r,E screen",
        },
        "eta": eta,
        "max_resource": max_resource,
        "k_levels": list(k_levels),
        "r_levels": list(r_levels),
        "e_levels": list(e_levels),
        "full_grid_n": full_n,
        "full_grid_cost_proxy": full_cost_proxy,
        "screen": [asdict(p) for p in screen],
        "screen_n": len(screen),
        "brackets": [_bracket_dict(b) for b in brackets],
        "schedule_resource_units": sched_cost,
        "approx_speedup_vs_full_grid": speedup,
        "note": (
            "Dry-run schedule only — cull order is deterministic placeholder; "
            "does not rewrite LOCKED recipe or gate rung0."
        ),
    }


def _bracket_dict(b: Bracket) -> dict[str, Any]:
    return {
        "bracket_id": b.bracket_id,
        "n0": b.n0,
        "r0": b.r0,
        "s": b.s,
        "eta": b.eta,
        "total_resource_units": b.total_resource_units,
        "rounds": [asdict(r) for r in b.rounds],
    }


def write_artifact(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _parse_int_list(raw: str | None, default: Sequence[int]) -> tuple[int, ...]:
    if raw is None or not raw.strip():
        return tuple(default)
    parts = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    return tuple(int(p) for p in parts)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run OA / successive-halving / Hyperband schedule for "
            "share×rank (k,r) ablations (S03/S16/S32)."
        )
    )
    parser.add_argument(
        "--mode",
        default="oa-then-hb",
        choices=("oa", "sh", "hyperband", "oa-then-hb"),
        help="Schedule builder (default: oa-then-hb)",
    )
    parser.add_argument("--eta", type=int, default=ETA_DEFAULT, help="Cull factor η")
    parser.add_argument(
        "--max-resource",
        type=int,
        default=MAX_RESOURCE_DEFAULT,
        help="Hyperband R (max resource units)",
    )
    parser.add_argument(
        "--k-levels",
        default=None,
        help="Comma-separated share factors (default: T1-aligned grid)",
    )
    parser.add_argument(
        "--r-levels",
        default=None,
        help="Comma-separated SVD/LoRA ranks (default: T2-aligned grid)",
    )
    parser.add_argument(
        "--e-levels",
        default=None,
        help="Comma-separated early resource levels for OA (default: 1,3,9)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full schedule JSON to stdout",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"Write schedule under {ARTIFACT_REL}",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Override artifact path (implies --write)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    k_levels = _parse_int_list(args.k_levels, K_LEVELS_DEFAULT)
    r_levels = _parse_int_list(args.r_levels, R_LEVELS_DEFAULT)
    e_levels = _parse_int_list(args.e_levels, E_LEVELS_DEFAULT)

    payload = build_schedule(
        mode=args.mode,
        k_levels=k_levels,
        r_levels=r_levels,
        e_levels=e_levels,
        eta=args.eta,
        max_resource=args.max_resource,
    )

    root = Path(__file__).resolve().parents[1]
    out_path: Path | None = None
    if args.write or args.out is not None:
        out_path = args.out if args.out is not None else root / ARTIFACT_REL
        if not out_path.is_absolute():
            out_path = root / out_path
        write_artifact(payload, out_path)
        try:
            artifact_s = str(out_path.relative_to(root))
        except ValueError:
            artifact_s = str(out_path)
        payload = {**payload, "artifact": artifact_s}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"needle={NEEDLE}")
        print(f"mode={payload['mode']} dry_run=true blocks_rung0=false")
        speedup = payload["approx_speedup_vs_full_grid"]
        speedup_s = f"{speedup:.2f}x" if speedup else "n/a"
        print(
            f"screen_n={payload['screen_n']} full_grid_n={payload['full_grid_n']} "
            f"brackets={len(payload['brackets'])} "
            f"units={payload['schedule_resource_units']} "
            f"approx_speedup={speedup_s}"
        )
        if out_path is not None:
            print(f"wrote={out_path}")
        for b in payload["brackets"]:
            rounds = b["rounds"]
            rsrc = ",".join(str(r["resource"]) for r in rounds)
            ns = ",".join(str(r["n_configs"]) for r in rounds)
            print(
                f"  bracket s={b['s']} n0={b['n0']} r0={b['r0']} "
                f"n_path=[{ns}] R_path=[{rsrc}] units={b['total_resource_units']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
