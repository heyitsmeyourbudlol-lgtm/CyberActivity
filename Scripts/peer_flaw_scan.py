#!/usr/bin/env python3
"""Daily flaw-detection cross-review — 8 niches scan each other's work.

Each day at ``flaw_scan_daily_time`` (local), every agent becomes
**Flaw Detection Scanner + {job title}** and reviews the other 7 niches.
Each subject receives 7 persona-specific reviews, then self-triages upgrades
vs downgrades.

State: ``~/.config/<namespace>/peer-flaw-scan-state.json``
Round: ``~/.config/<namespace>/peer-flaw-scan-round.json``

Usage:
  python3 scripts/peer_flaw_scan.py --status
  python3 scripts/peer_flaw_scan.py --preview
  python3 scripts/peer_flaw_scan.py --start        # force today's round
  python3 scripts/peer_flaw_scan.py --record-review REVIEWER TARGET "text"
  python3 scripts/peer_flaw_scan.py --compile
  ./scripts/peer flaw-scan
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import peer_roles as roles  # noqa: E402
import project_automation as auto  # noqa: E402

STATE_PATH = auto.CONFIG_DIR / "peer-flaw-scan-state.json"
ROUND_PATH = auto.CONFIG_DIR / "peer-flaw-scan-round.json"
REVIEWS_DIR = auto.CONFIG_DIR / "flaw-scan-reviews"

PHASE_SCAN = "scanning"
PHASE_TRIAGE = "triage"
PHASE_COMPLETE = "complete"


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _today() -> str:
    return date.today().isoformat()


def _plain(text: str, *, limit: int = 280) -> str:
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", str(text or ""))
    s = re.sub(r"`([^`]+)`", r"\1", s).strip()
    if len(s) > limit:
        return s[: limit - 1] + "…"
    return s


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class FlawScanConfig:
    enabled: bool
    daily_time: str  # HH:MM local
    min_hour: int
    min_minute: int


def load_config() -> FlawScanConfig:
    raw = auto.CFG.get("flaw_scan") or {}
    if not isinstance(raw, dict):
        raw = {}
    enabled = bool(raw.get("enabled", auto.CFG.get("flaw_scan_enabled", True)))
    daily = str(raw.get("daily_time") or auto.CFG.get("flaw_scan_daily_time") or "09:00").strip()
    m = re.match(r"^(\d{1,2}):(\d{2})$", daily)
    if not m:
        daily = "09:00"
        m = re.match(r"^(\d{1,2}):(\d{2})$", daily)
    assert m is not None
    hour, minute = int(m.group(1)), int(m.group(2))
    hour = max(0, min(23, hour))
    minute = max(0, min(59, minute))
    return FlawScanConfig(
        enabled=enabled,
        daily_time=f"{hour:02d}:{minute:02d}",
        min_hour=hour,
        min_minute=minute,
    )


def scanner_title(role: roles.AgentRole) -> str:
    return f"Flaw Detection Scanner + {role.job_title}"


def _target_work_for_role(role_id: str) -> dict[str, Any]:
    try:
        import peer_agent_board as board

        b = board.build_board(refresh_roster=False)
        for agent in b.get("agents") or []:
            if isinstance(agent, dict) and agent.get("role_id") == role_id:
                return {
                    "item": agent.get("item") or "",
                    "item_plain": agent.get("item_plain") or _plain(str(agent.get("item") or "")),
                    "responsibilities": agent.get("responsibilities") or "",
                    "worktree": agent.get("worktree"),
                }
    except Exception:  # noqa: BLE001
        pass
    for role in roles.load_roles():
        if role.id == role_id:
            return {
                "item": role.niche_task or role.responsibilities,
                "item_plain": _plain(role.niche_task or role.responsibilities),
                "responsibilities": role.responsibilities,
                "worktree": None,
            }
    return {"item": "", "item_plain": "(no assignment)", "responsibilities": "", "worktree": None}


def build_review_pairs(pool: list[roles.AgentRole] | None = None) -> list[dict[str, Any]]:
    """56 directed pairs: each reviewer scans each other niche (not self)."""
    pool = pool or roles.load_roles()[: roles.worker_pool_size()]
    pairs: list[dict[str, Any]] = []
    for reviewer in pool:
        for target in pool:
            if reviewer.id == target.id:
                continue
            work = _target_work_for_role(target.id)
            pairs.append(
                {
                    "reviewer_role_id": reviewer.id,
                    "reviewer_title": scanner_title(reviewer),
                    "reviewer_model": reviewer.model,
                    "reviewer_subagent": reviewer.subagent_type,
                    "target_role_id": target.id,
                    "target_job_title": target.job_title,
                    "target_work": work,
                    "status": "pending",
                    "review": None,
                    "recorded_at": None,
                }
            )
    return pairs


def load_state() -> dict[str, Any]:
    return _safe_read_json(STATE_PATH) or {}


def load_round() -> dict[str, Any] | None:
    return _safe_read_json(ROUND_PATH)


def save_state(state: dict[str, Any]) -> None:
    _write_json(STATE_PATH, state)


def save_round(round_data: dict[str, Any]) -> None:
    _write_json(ROUND_PATH, round_data)


def start_round(*, force: bool = False) -> dict[str, Any]:
    """Begin today's cross-review round."""
    today = _today()
    state = load_state()
    if not force and state.get("last_completed_date") == today:
        existing = load_round()
        if existing and existing.get("round_date") == today:
            return existing
    pool = roles.load_roles()[: roles.worker_pool_size()]
    pairs = build_review_pairs(pool)
    subjects = [
        {
            "role_id": r.id,
            "job_title": r.job_title,
            "reviews_received": [],
            "triage": None,
            "upgrades_accepted": [],
            "downgrades_rejected": [],
        }
        for r in pool
    ]
    round_data: dict[str, Any] = {
        "version": 1,
        "round_id": today,
        "round_date": today,
        "started_at": _now_iso(),
        "phase": PHASE_SCAN,
        "config": {"daily_time": load_config().daily_time},
        "pairs": pairs,
        "subjects": subjects,
        "completed_at": None,
    }
    save_round(round_data)
    state["current_round_date"] = today
    state["last_started_at"] = _now_iso()
    save_state(state)
    return round_data


def is_past_daily_time(cfg: FlawScanConfig | None = None) -> bool:
    cfg = cfg or load_config()
    now = datetime.now()
    if now.hour > cfg.min_hour:
        return True
    if now.hour == cfg.min_hour and now.minute >= cfg.min_minute:
        return True
    return False


def should_dispatch_flaw_scan() -> bool:
    """True when peer loop should send flaw-scan orchestration instead of normal plan."""
    cfg = load_config()
    if not cfg.enabled:
        return False
    today = _today()
    state = load_state()
    rnd = load_round()

    if rnd and rnd.get("round_date") == today and rnd.get("phase") in (PHASE_SCAN, PHASE_TRIAGE):
        return True

    if state.get("last_completed_date") == today:
        return False

    if not is_past_daily_time(cfg):
        return False

    if rnd is None or rnd.get("round_date") != today:
        start_round()
        return True

    return rnd.get("phase") in (PHASE_SCAN, PHASE_TRIAGE)


def record_review(reviewer_role_id: str, target_role_id: str, body: str) -> bool:
    rnd = load_round()
    if not rnd:
        return False
    body = str(body or "").strip()
    if not body:
        return False
    updated = False
    for pair in rnd.get("pairs") or []:
        if not isinstance(pair, dict):
            continue
        if pair.get("reviewer_role_id") == reviewer_role_id and pair.get("target_role_id") == target_role_id:
            pair["review"] = body
            pair["status"] = "done"
            pair["recorded_at"] = _now_iso()
            updated = True
            break
    if not updated:
        return False
    _attach_review_to_subject(rnd, target_role_id, reviewer_role_id, body)
    save_round(rnd)
    _maybe_advance_phase(rnd)
    return True


def _attach_review_to_subject(
    rnd: dict[str, Any],
    target_role_id: str,
    reviewer_role_id: str,
    body: str,
) -> None:
    reviewer_title = reviewer_role_id
    for pair in rnd.get("pairs") or []:
        if (
            isinstance(pair, dict)
            and pair.get("target_role_id") == target_role_id
            and pair.get("reviewer_role_id") == reviewer_role_id
        ):
            reviewer_title = pair.get("reviewer_title") or reviewer_role_id
            break

    for subj in rnd.get("subjects") or []:
        if subj.get("role_id") != target_role_id:
            continue
        received = list(subj.get("reviews_received") or [])
        received = [r for r in received if r.get("reviewer_role_id") != reviewer_role_id]
        received.append(
            {
                "reviewer_role_id": reviewer_role_id,
                "reviewer_title": reviewer_title,
                "body": body,
                "recorded_at": _now_iso(),
            }
        )
        subj["reviews_received"] = received
        return


def _scan_complete(rnd: dict[str, Any]) -> bool:
    pairs = rnd.get("pairs") or []
    if not pairs:
        return False
    return all(isinstance(p, dict) and p.get("status") == "done" for p in pairs)


def _triage_complete(rnd: dict[str, Any]) -> bool:
    subjects = rnd.get("subjects") or []
    if not subjects:
        return False
    return all(isinstance(s, dict) and s.get("triage") for s in subjects)


def _maybe_advance_phase(rnd: dict[str, Any]) -> None:
    phase = rnd.get("phase")
    if phase == PHASE_SCAN and _scan_complete(rnd):
        rnd["phase"] = PHASE_TRIAGE
        rnd["scan_completed_at"] = _now_iso()
        save_round(rnd)
    elif phase == PHASE_TRIAGE and _triage_complete(rnd):
        rnd["phase"] = PHASE_COMPLETE
        rnd["completed_at"] = _now_iso()
        save_round(rnd)
        state = load_state()
        state["last_completed_date"] = rnd.get("round_date") or _today()
        state["last_completed_at"] = _now_iso()
        save_state(state)
        try:
            import peer_debrief as debrief

            debrief.capture_flaw_round_debrief()
            debrief.ensure_sop_index()
        except Exception:  # noqa: BLE001
            pass


def record_triage(
    role_id: str,
    *,
    summary: str,
    upgrades: list[str] | None = None,
    downgrades: list[str] | None = None,
) -> bool:
    rnd = load_round()
    if not rnd:
        return False
    for subj in rnd.get("subjects") or []:
        if subj.get("role_id") != role_id:
            continue
        subj["triage"] = {
            "summary": summary.strip(),
            "recorded_at": _now_iso(),
        }
        subj["upgrades_accepted"] = list(upgrades or [])
        subj["downgrades_rejected"] = list(downgrades or [])
        save_round(rnd)
        _maybe_advance_phase(rnd)
        return True
    return False


def compile_from_review_files() -> int:
    """Ingest ``flaw-scan-reviews/{reviewer}__{target}.md`` files into round JSON."""
    rnd = load_round()
    if not rnd:
        return 0
    count = 0
    if REVIEWS_DIR.is_dir():
        for path in sorted(REVIEWS_DIR.glob("*__*.md")):
            parts = path.stem.split("__", 1)
            if len(parts) != 2:
                continue
            reviewer, target = parts[0], parts[1]
            try:
                body = path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if body and record_review(reviewer, target, body):
                count += 1
    return count


def _reviews_for_scanner(reviewer_id: str, pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [p for p in pairs if p.get("reviewer_role_id") == reviewer_id]


def _format_scanner_task(role: roles.AgentRole, targets: list[dict[str, Any]]) -> str:
    lines = [
        f"**Your identity:** {scanner_title(role)}",
        f"**Model:** {role.model} · **Subagent:** {role.subagent_type}",
        "",
        "You are a **flaw detection scanner** wearing your niche persona. "
        "Review **7 other agents' work** below — improvement & efficiency focus; holistic, not nitpicky.",
        "",
        "For **each** target output exactly:",
        "",
        "```",
        "### REVIEW:{target_role_id}",
        "- Flaws:",
        "- Efficiency upgrades:",
        "- Holistic advice:",
        "- Severity: low|med|high",
        "```",
        "",
        "After all 7 reviews, append each review via:",
        f"`python3 scripts/peer_flaw_scan.py --record-review {role.id} TARGET_ROLE_ID \"...\"`",
        "Or save to `~/.config/automation-hub/flaw-scan-reviews/{reviewer}__{target}.md` and run `--compile`.",
        "",
        "## Targets to scan",
        "",
    ]
    for i, t in enumerate(targets, 1):
        work = t.get("target_work") or {}
        lines.append(f"### {i}. {t.get('target_job_title')} (`{t.get('target_role_id')}`)")
        lines.append(f"- **Work / assignment:** {work.get('item_plain') or _plain(str(work.get('item')))}")
        if work.get("responsibilities"):
            lines.append(f"- **Niche duties:** {work['responsibilities']}")
        wt = work.get("worktree")
        if isinstance(wt, dict) and wt.get("path"):
            lines.append(f"- **Worktree:** `{wt.get('path')}` branch `{wt.get('branch', '')}`")
        lines.append("")
    return "\n".join(lines)


def _format_triage_task(role: roles.AgentRole, subject: dict[str, Any]) -> str:
    received = subject.get("reviews_received") or []
    lines = [
        f"**Your identity:** {role.job_title} (original niche — not scanner mode)",
        f"**Model:** {role.model}",
        "",
        "You received **7 flaw-detection reviews** from the other niches (one per persona). "
        "**Self-triage:** decide which advice is a genuine **upgrade** vs a **downgrade** for your work.",
        "",
        "Output:",
        "1. **Summary** — themes across reviews",
        "2. **Upgrades accepted** — bullet list (actionable)",
        "3. **Downgrades rejected** — bullet list with one-line why",
        "4. Run: "
        f"`python3 scripts/peer_flaw_scan.py --record-triage {role.id} --summary \"...\"`",
        "",
        "## Your 7 reviews",
        "",
    ]
    for i, rev in enumerate(received, 1):
        lines.append(f"### Review {i} — {rev.get('reviewer_title', '?')}")
        lines.append(str(rev.get("body") or "(missing)"))
        lines.append("")
    if len(received) < 7:
        lines.append(f"_({7 - len(received)} review(s) still pending — triage when all 7 arrive.)_")
    return "\n".join(lines)


def build_orchestrator_prompt() -> str | None:
    """Full orchestrator prompt for the active flaw-scan phase."""
    rnd = load_round()
    if not rnd:
        if should_dispatch_flaw_scan():
            rnd = start_round()
        else:
            return None

    phase = rnd.get("phase")
    if phase == PHASE_COMPLETE:
        return None

    pool = roles.load_roles()[: roles.worker_pool_size()]
    pairs = rnd.get("pairs") or build_review_pairs(pool)
    round_date = rnd.get("round_date") or _today()

    lines = [
        f"# Daily Flaw Detection Round — {round_date}",
        "",
        "Holistic improvement focus: each niche scans the others' automation work. "
        "Every agent gets **7 persona-specific reviews**, then self-triages upgrades vs downgrades.",
        "",
    ]

    if phase == PHASE_SCAN:
        done = sum(1 for p in pairs if p.get("status") == "done")
        lines.extend(
            [
                f"## Phase 1 — Cross-scan ({done}/56 reviews recorded)",
                "",
                "Launch **8 parallel Task peers** in **ONE** message. "
                "Each peer is **Flaw Detection Scanner + {job title}** and reviews **7 other agents**.",
                "",
            ]
        )
        for role in pool:
            targets = _reviews_for_scanner(role.id, pairs)
            lines.append(f"### Task: {scanner_title(role)}")
            lines.append(
                f'- Task(subagent_type="{role.subagent_type}", model="{role.model}", '
                f'description="{scanner_title(role)}", prompt="""'
            )
            lines.append(_format_scanner_task(role, targets))
            lines.append('""")')
            lines.append("")

        lines.extend(
            [
                "## After Phase 1",
                "- Ensure all 56 reviews are recorded (`--record-review` or `--compile`)",
                "- When complete, phase advances to triage automatically",
                "- Re-dispatch or continue to Phase 2 prompts",
                "",
            ]
        )
    elif phase == PHASE_TRIAGE:
        subjects = {s.get("role_id"): s for s in (rnd.get("subjects") or []) if isinstance(s, dict)}
        lines.extend(
            [
                "## Phase 2 — Self-triage (7 reviews → upgrade vs downgrade)",
                "",
                "Launch **8 parallel Task peers** in **ONE** message. "
                "Each original niche reads their 7 reviews and triages.",
                "",
            ]
        )
        for role in pool:
            subj = subjects.get(role.id) or {"reviews_received": [], "role_id": role.id}
            lines.append(f"### Task: {role.job_title} — self-triage")
            lines.append(
                f'- Task(subagent_type="{role.subagent_type}", model="{role.model}", '
                f'description="{role.job_title} triage", prompt="""'
            )
            lines.append(_format_triage_task(role, subj))
            lines.append('""")')
            lines.append("")

    lines.append("## Constraints")
    lines.append("- Improvement & efficiency focus — no style-only nitpicks")
    lines.append("- Each scanner uses their niche lens (verify, perf, safety, queue, …)")
    lines.append("- Subject agent owns final judgment on upgrades vs downgrades")
    return "\n".join(lines)


def status_dict() -> dict[str, Any]:
    cfg = load_config()
    state = load_state()
    rnd = load_round() or {}
    pairs = rnd.get("pairs") or []
    done_reviews = sum(1 for p in pairs if isinstance(p, dict) and p.get("status") == "done")
    subjects = rnd.get("subjects") or []
    done_triage = sum(1 for s in subjects if isinstance(s, dict) and s.get("triage"))
    return {
        "enabled": cfg.enabled,
        "daily_time": cfg.daily_time,
        "past_daily_time": is_past_daily_time(cfg),
        "today": _today(),
        "last_completed_date": state.get("last_completed_date"),
        "round": {
            "round_date": rnd.get("round_date"),
            "phase": rnd.get("phase"),
            "started_at": rnd.get("started_at"),
            "reviews_done": done_reviews,
            "reviews_total": len(pairs) or 56,
            "triage_done": done_triage,
            "triage_total": len(subjects) or 8,
        },
        "should_dispatch": should_dispatch_flaw_scan(),
    }


def format_status() -> str:
    st = status_dict()
    r = st.get("round") or {}
    lines = [
        f"Flaw scan · enabled={st['enabled']} · daily {st['daily_time']} local",
        f"Today {st['today']} · last completed {st.get('last_completed_date') or '—'}",
        f"Round phase={r.get('phase') or '—'} · reviews {r.get('reviews_done')}/{r.get('reviews_total')} "
        f"· triage {r.get('triage_done')}/{r.get('triage_total')}",
        f"Should dispatch now: {st.get('should_dispatch')}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Daily flaw-detection cross-review")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--preview", action="store_true", help="Print orchestrator prompt")
    parser.add_argument("--start", action="store_true", help="Force start today's round")
    parser.add_argument("--record-review", nargs=3, metavar=("REVIEWER", "TARGET", "BODY"))
    parser.add_argument("--record-triage", metavar="ROLE_ID")
    parser.add_argument("--summary", default="", help="With --record-triage")
    parser.add_argument("--upgrades", default="", help="Comma-separated accepted upgrades")
    parser.add_argument("--downgrades", default="", help="Comma-separated rejected advice")
    parser.add_argument("--compile", action="store_true", help="Ingest flaw-scan-reviews/*.md")
    parser.add_argument("--advance", action="store_true", help="Force phase check")
    args = parser.parse_args(argv)

    if args.start:
        start_round(force=True)

    if args.record_review:
        ok = record_review(args.record_review[0], args.record_review[1], args.record_review[2])
        return 0 if ok else 1

    if args.record_triage:
        ups = [s.strip() for s in args.upgrades.split(",") if s.strip()] if args.upgrades else []
        downs = [s.strip() for s in args.downgrades.split(",") if s.strip()] if args.downgrades else []
        ok = record_triage(args.record_triage, summary=args.summary or "(triage recorded)", upgrades=ups, downgrades=downs)
        return 0 if ok else 1

    if args.compile:
        n = compile_from_review_files()
        print(f"compiled {n} review file(s)")
        return 0

    if args.advance:
        rnd = load_round()
        if rnd:
            _maybe_advance_phase(rnd)
        return 0

    if args.preview:
        text = build_orchestrator_prompt()
        print(text or "(no active flaw-scan round)")
        return 0

    if args.json:
        print(json.dumps(status_dict(), indent=2))
        return 0

    if args.status:
        print(format_status())
        return 0

    print(format_status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
