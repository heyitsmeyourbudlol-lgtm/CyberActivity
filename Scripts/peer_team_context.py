#!/usr/bin/env python3
"""Team context — one shared brain for all agents each improve cycle.

Writes notes/TEAM_CONTEXT.md and pushes SUM payloads + vault summaries so every
niche gets critical AND output-changing low-importance facts (not just its todo).

Usage:
  python3 scripts/peer_team_context.py --write
  ./scripts/peer team-context
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import peer_roles as roles  # noqa: E402
import project_automation as auto  # noqa: E402

TEAM_CONTEXT_MD = ROOT / "notes" / "TEAM_CONTEXT.md"
TEAM_CONTEXT_JSON = auto.CONFIG_DIR / "team-context.json"

TEAM_CONTEXT_MAX_AGE_SEC = 3600
# Pre-dispatch write TTL — skip rebuild when md is fresh (probed 96–216ms/dispatch).
# OVERSEER_TEAM_CONTEXT_TTL_2026_09_04
# OVERSEER_TEAM_CONTEXT_TTL_2026_09_03
TEAM_CONTEXT_WRITE_TTL_SEC = 60.0

# Operational-only sections for niche prompts (intelligence layers live in persona block).
SNAPSHOT_SECTION_ORDER: tuple[str, ...] = (
    "build_mode",
    "factory",
    "last_cycle",
    "live",
    "queue",
    "assignments",
)

TEAM_SHARED_READS: tuple[str, ...] = (
    "notes/TEAM_CONTEXT.md",
    "notes/PROJECT_LEARNING.md",
    "notes/CRITICAL_THINKING.md",
    "notes/HALLUCINATION_GUARD.md",
    "notes/AGENT_VS_HUMAN.md",
    "notes/IDEA_SYNTHESIS.md",
    "notes/AGENT_GATES.md",
    "notes/PRECISION_HABITS.md",
    "notes/OUTPUT_COMPARE.md",
    "notes/AGENT_MINI_APPS.md",
    "notes/SELF_DIAGNOSE.md",
    "notes/AGENT_ERROR_PLAYBOOK.md",
    "notes/AGENT_SURVIVAL.md",
    "notes/MEMORY_SPAN.md",
    "notes/WORK_ASSIGN.md",
    "notes/RESEARCH_SYNC.md",
    "notes/AUTOMATION_DIGEST.md",
    "notes/COMMAND_BUILDER.md",
    "notes/WORK_QUEUE.md",
    "scripts/self_improve_context.md",
    "AGENTS.md",
)


@dataclass
class TeamContextBundle:
    as_of: float
    sections: dict[str, str] = field(default_factory=dict)
    assignments: list[dict[str, str]] = field(default_factory=list)

    def markdown(self, *, max_chars: int = 12000) -> str:
        lines = [
            "# Team context — shared by all agents",
            "",
            f"_Updated {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.as_of))}_ · "
            "read before Plan/Implement — includes low-importance facts that can change output",
            "",
        ]
        order = (
            "learning",
            "survival",
            "intelligence",
            "hallucination_guard",
            "human_gap",
            "idea_synthesis",
            "precision",
            "output_compare",
            "mini_apps",
            "self_diagnose",
            "memory",
            "build_mode",
            "factory",
            "last_cycle",
            "live",
            "queue",
            "self_heal",
            "research",
            "horizon",
            "playbook",
            "oversight",
            "flaw_scan",
            "comms",
            "config",
            "assignments",
            "misc",
        )
        for key in order:
            body = (self.sections.get(key) or "").strip()
            if not body:
                continue
            title = key.replace("_", " ").title()
            lines.extend([f"## {title}", "", body, ""])
        text = "\n".join(lines).strip() + "\n"
        if len(text) > max_chars:
            text = text[: max_chars - 80] + "\n\n…_(truncated — full JSON in team-context.json)_\n"
        return text

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "sections": self.sections,
            "assignments": self.assignments,
            "shared_reads": list(TEAM_SHARED_READS),
        }


def shared_read_paths(*, extra: list[str] | None = None) -> list[str]:
    paths = list(TEAM_SHARED_READS)
    if extra:
        paths.extend(extra)
    return list(dict.fromkeys(p for p in paths if p))


def _load_state() -> dict[str, Any]:
    path = auto.CONFIG_DIR / "peer-loop-state.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _file_excerpt(path: Path, *, max_lines: int = 12) -> str:
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[:max_lines])


def _horizon_now(signals: Any | None) -> str:
    if signals is None:
        return ""
    try:
        import automation_improve as improve

        opps = getattr(signals, "opportunities", None) or []
        lines: list[str] = []
        for o in opps:
            if improve._horizon_tier(o.priority) != "NOW":
                continue
            lines.append(f"- **[{o.category}]** {o.title} — {o.detail[:120]}")
            if len(lines) >= 6:
                break
        return "\n".join(lines)
    except Exception:  # noqa: BLE001
        return ""


def build_team_context(*, signals: Any | None = None) -> TeamContextBundle:
    now = time.time()
    sections: dict[str, str] = {}

    try:
        import peer_project_learning as pl

        pl.write_project_learning_md()
        sections["learning"] = pl.format_learning_block()
    except Exception as exc:  # noqa: BLE001
        sections["learning"] = f"- project learning unavailable ({exc})"

    try:
        import peer_agent_survival as survival

        sections["survival"] = survival.format_survival_block(compact=True)
    except Exception as exc:  # noqa: BLE001
        sections["survival"] = f"- agent survival unavailable ({exc})"

    try:
        import peer_critical_thinking as ct

        ct.write_critical_thinking_md()
        sections["intelligence"] = ct.format_critical_thinking_block()
    except Exception as exc:  # noqa: BLE001
        sections["intelligence"] = f"- critical thinking unavailable ({exc})"

    try:
        import peer_hallucination_guard as hg

        hg.write_hallucination_guard_md()
        sections["hallucination_guard"] = hg.format_hallucination_block()
    except Exception as exc:  # noqa: BLE001
        sections["hallucination_guard"] = f"- hallucination guard unavailable ({exc})"

    try:
        import peer_agent_human_gap as hgap

        hgap.write_agent_vs_human_md()
        sections["human_gap"] = hgap.format_human_gap_block(compact=True)
    except Exception as exc:  # noqa: BLE001
        sections["human_gap"] = f"- agent vs human gap unavailable ({exc})"

    try:
        import peer_idea_synthesis as idea

        idea.write_idea_synthesis_md()
        block = idea.format_idea_synthesis_block()
        recent = idea.format_recent_ideas_block(limit=3)
        if recent:
            block = block + "\n\n" + recent
        sections["idea_synthesis"] = block
    except Exception as exc:  # noqa: BLE001
        sections["idea_synthesis"] = f"- idea synthesis unavailable ({exc})"

    try:
        import peer_precision_habits as ph

        ph.write_precision_habits_md()
        sections["precision"] = ph.format_precision_block()
    except Exception as exc:  # noqa: BLE001
        sections["precision"] = f"- precision habits unavailable ({exc})"

    try:
        import peer_output_compare as oc

        oc.write_output_compare_md()
        sections["output_compare"] = oc.format_output_compare_block()
    except Exception as exc:  # noqa: BLE001
        sections["output_compare"] = f"- output compare unavailable ({exc})"

    try:
        import peer_agent_mini_apps as ma

        ma.write_mini_apps_md()
        sections["mini_apps"] = ma.format_mini_apps_block()
    except Exception as exc:  # noqa: BLE001
        sections["mini_apps"] = f"- mini apps unavailable ({exc})"

    try:
        import peer_self_diagnose as sd

        sd.write_self_diagnose_md()
        sections["self_diagnose"] = sd.format_self_diagnose_block(quick=True)
    except Exception as exc:  # noqa: BLE001
        sections["self_diagnose"] = f"- self-diagnosis unavailable ({exc})"

    try:
        import peer_memory_span as ms

        ms.write_memory_span_md()
        sections["memory"] = ms.format_memory_habits_block()
    except Exception as exc:  # noqa: BLE001
        sections["memory"] = f"- memory span unavailable ({exc})"

    sections["build_mode"] = (
        f"- factory_meter_mode: `{auto.factory_meter_mode()}`\n"
        f"- development_focus: `{auto.development_focus()}`\n"
        f"- north_star: {auto.factory_north_star()[:200]}"
    )

    try:
        import factory_progress as fp

        prog = fp.compute_factory_progress()
        dim_lines = [
            f"- **{d.name}** {d.score:.0%} — {d.evidence[:100]}"
            for d in prog.dimensions
        ]
        blocker_lines = [f"- {b}" for b in prog.blockers[:6]]
        sections["factory"] = (
            f"- Readiness: **{prog.pct}%** — {prog.label[:120]}\n"
            + "\n".join(dim_lines)
            + ("\n\n**Blockers:**\n" + "\n".join(blocker_lines) if blocker_lines else "")
        )
    except Exception as exc:  # noqa: BLE001
        sections["factory"] = f"- factory_progress unavailable ({exc})"

    try:
        import peer_transcript as tx

        last_block = tx.format_last_cycle_block(_load_state())
        if last_block:
            sections["last_cycle"] = last_block
    except Exception:  # noqa: BLE001
        pass

    if signals is not None:
        live = getattr(signals, "live", None) or {}
        drift = getattr(signals, "queue_drift", None) or []
        audit_w = getattr(signals, "audit_warnings", None) or []
        audit_e = getattr(signals, "audit_errors", None) or []
        live_lines = [
            f"- git: {live.get('git', '?')}",
            f"- tests: {live.get('tests', '?')}",
            f"- git_clean: {live.get('git_clean')}",
        ]
        if drift:
            live_lines.append("- queue_drift:")
            live_lines.extend(f"  - {d[:100]}" for d in drift[:5])
        if audit_e:
            live_lines.append("- audit_errors:")
            live_lines.extend(f"  - {e[:100]}" for e in audit_e[:4])
        if audit_w:
            live_lines.append("- audit_warnings:")
            live_lines.extend(f"  - {w[:100]}" for w in audit_w[:4])
        sections["live"] = "\n".join(live_lines)

    q = auto.open_work_items()
    q_lines = [f"- source: `{q.source}` · open: {len(q.open_items)}"]
    q_lines.extend(f"- {item[:100]}" for item in q.open_items[:10])
    sections["queue"] = "\n".join(q_lines)

    try:
        import peer_self_heal as sh

        bottlenecks = sh.scan_bottlenecks()
        if bottlenecks:
            sections["self_heal"] = "\n".join(
                f"- **[{b.severity}]** {b.title} — {str(b.evidence or '')[:80]}"
                for b in bottlenecks[:10]
            )
        else:
            sections["self_heal"] = "- No open bottlenecks"
    except Exception as exc:  # noqa: BLE001
        sections["self_heal"] = f"- scan skipped ({exc})"

    try:
        import peer_dual_research as dr

        sync = dr.load_sync_brief(max_chars=1500)
        if sync.strip():
            sections["research"] = sync.strip()
    except Exception:  # noqa: BLE001
        pass

    horizon = _horizon_now(signals)
    if horizon:
        sections["horizon"] = horizon

    try:
        import peer_playbook as pb

        fixes = pb.format_instant_fixes(pb.load_entries()[:8], max_entries=8)
        if fixes.strip():
            sections["playbook"] = fixes.strip()
    except Exception:  # noqa: BLE001
        pass

    oversight = ROOT / "notes" / "SYSTEM_OVERSIGHT.md"
    excerpt = _file_excerpt(oversight, max_lines=15)
    if excerpt:
        sections["oversight"] = excerpt

    try:
        import peer_flaw_scan as fs

        st = fs.status_dict()
        rnd = st.get("round") or {}
        sections["flaw_scan"] = (
            f"- enabled: {st.get('enabled')} · reviews "
            f"{rnd.get('reviews_done', '?')}/{rnd.get('reviews_total', '?')}"
        )
    except Exception:  # noqa: BLE001
        sections["flaw_scan"] = "- flaw-scan status unavailable"

    try:
        import peer_agent_comms as comms

        if comms.comms_enabled():
            recent = comms.read_bus(limit=5)
            lines = [
                f"- bus: {comms._try_rel(comms.BUS_PATH)} · recent {len(recent)} msg(s)"
            ]
            for msg in recent[-3:]:
                lines.append(
                    f"  - {msg.get('t')} {msg.get('f')}→{msg.get('to')}: "
                    f"{json.dumps(msg.get('p') or {})[:80]}"
                )
            sections["comms"] = "\n".join(lines)
    except Exception:  # noqa: BLE001
        pass

    sections["config"] = (
        f"- parallel_peer_floor: {auto.parallel_peer_floor()}\n"
        f"- continuous_wake_sec: {auto.CFG.get('continuous_wake_sec')}\n"
        f"- continue_on_dirty: {auto.CFG.get('continue_on_dirty')}\n"
        f"- improve_hand_out_roles: {auto.improve_hand_out_roles_enabled()}"
    )

    digest_excerpt = _file_excerpt(ROOT / "notes" / "AUTOMATION_DIGEST.md", max_lines=8)
    if digest_excerpt:
        sections["misc"] = f"**Digest peek:**\n{digest_excerpt}"

    try:
        import peer_work_assign as wa

        wa.write_work_assign_md()
        sections["assignments"] = wa.format_work_assign_block()
    except Exception as exc:  # noqa: BLE001
        sections["assignments"] = f"- work assignment unavailable ({exc})"

    return TeamContextBundle(as_of=now, sections=sections)


def write_team_context(*, signals: Any | None = None, force: bool = False) -> Path:
    """Write TEAM_CONTEXT.md + JSON; TTL-skip when fresh unless force/signals.

    OVERSEER_TEAM_CONTEXT_TTL_2026_09_04 — hub-protect needle; ignore Mac sync restore.
    """
    TEAM_CONTEXT_MD.parent.mkdir(parents=True, exist_ok=True)
    # Explicit signals always rebuild; force bypasses TTL.
    if signals is not None:
        force = True
    if not force and TEAM_CONTEXT_MD.is_file():
        try:
            age = time.time() - float(TEAM_CONTEXT_MD.stat().st_mtime)
            if age < TEAM_CONTEXT_WRITE_TTL_SEC:
                return TEAM_CONTEXT_MD
        except OSError:
            pass
    bundle = build_team_context(signals=signals)
    TEAM_CONTEXT_MD.write_text(bundle.markdown(), encoding="utf-8")
    TEAM_CONTEXT_JSON.parent.mkdir(parents=True, exist_ok=True)
    TEAM_CONTEXT_JSON.write_text(json.dumps(bundle.to_dict(), indent=2) + "\n", encoding="utf-8")
    return TEAM_CONTEXT_MD


def load_team_context_markdown(*, max_chars: int = 5000, refresh_if_stale: bool = True) -> str:
    if refresh_if_stale:
        if not TEAM_CONTEXT_MD.is_file():
            write_team_context()
        else:
            age = time.time() - TEAM_CONTEXT_MD.stat().st_mtime
            if age > TEAM_CONTEXT_MAX_AGE_SEC:
                write_team_context()
    if TEAM_CONTEXT_MD.is_file():
        try:
            text = TEAM_CONTEXT_MD.read_text(encoding="utf-8")
            return text[:max_chars] if len(text) > max_chars else text
        except OSError:
            pass
    return build_team_context().markdown(max_chars=max_chars)


def format_team_snapshot(*, max_chars: int = 2500) -> str:
    """Operational slice only — queue/live/factory; not intelligence layers (persona block)."""
    bundle = build_team_context()
    lines = [
        "## Team snapshot (operational)",
        "",
        f"_Updated {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bundle.as_of))}_",
        "",
    ]
    for key in SNAPSHOT_SECTION_ORDER:
        body = bundle.sections.get(key, "").strip()
        if not body:
            continue
        title = key.replace("_", " ").title()
        lines.extend([f"### {title}", "", body, ""])
    text = "\n".join(lines).strip()
    return text[:max_chars] if len(text) > max_chars else text


def format_niche_learning_block(
    *,
    role_id: str,
    model: str = "inherit",
    subagent_type: str = "",
) -> str:
    blocks: list[str] = []
    try:
        import peer_project_learning as pl

        blocks.append(pl.format_learning_block(role_id=role_id))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Project learning\n\n- unavailable ({exc})\n")
    try:
        import peer_critical_thinking as ct

        blocks.append(ct.format_critical_thinking_block(role_id=role_id))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Critical thinking\n\n- unavailable ({exc})\n")
    try:
        import peer_hallucination_guard as hg

        blocks.append(hg.format_hallucination_block(role_id=role_id))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Hallucination guard\n\n- unavailable ({exc})\n")
    try:
        import peer_agent_human_gap as hgap

        blocks.append(hgap.format_human_gap_block(compact=True))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Agent vs human\n\n- unavailable ({exc})\n")
    try:
        import peer_idea_synthesis as idea

        blocks.append(idea.format_idea_synthesis_block(role_id=role_id))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Idea synthesis\n\n- unavailable ({exc})\n")
    try:
        import peer_precision_habits as ph

        blocks.append(
            ph.format_precision_block(
                role_id=role_id,
                model=model,
                subagent_type=subagent_type,
            )
        )
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Precision habits\n\n- unavailable ({exc})\n")
    try:
        import peer_output_compare as oc

        blocks.append(oc.format_output_compare_block(role_id=role_id))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Expected vs actual\n\n- unavailable ({exc})\n")
    try:
        import peer_agent_mini_apps as ma

        blocks.append(ma.format_mini_apps_block(role_id=role_id))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Mini apps\n\n- unavailable ({exc})\n")
    try:
        import peer_self_diagnose as sd

        blocks.append(sd.format_self_diagnose_block(role_id=role_id, quick=True))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Self-diagnosis\n\n- unavailable ({exc})\n")
    try:
        import peer_work_assign as wa

        blocks.append(wa.format_work_assign_block(role_id=role_id))
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Work assignment\n\n- unavailable ({exc})\n")
    try:
        import peer_memory_span as ms

        blocks.append(ms.format_memory_habits_block())
    except Exception as exc:  # noqa: BLE001
        blocks.append(f"## Memory span\n\n- unavailable ({exc})\n")
    return "\n\n".join(blocks)


def sync_agent_vaults(
    assignments: list[Any],
    *,
    signals: Any | None = None,
) -> int:
    try:
        import peer_agent_comms as comms
    except ImportError:
        return 0
    if not comms.comms_enabled():
        return 0

    bundle = build_team_context(signals=signals)
    shared_md = bundle.markdown(max_chars=3500)
    pivotal = {
        "mode": auto.factory_meter_mode(),
        "focus": auto.development_focus(),
        "factory": bundle.sections.get("factory", "")[:200],
        "queue_open": len(auto.open_work_items().open_items),
    }
    # GLink bus: codes only — factory prose stays in vault, not on SUM lines.
    sh_compact = comms._compact_sum_shared(pivotal)

    comms.post_glink(
        msg_type=comms.MSG_SUM,
        from_role="orchestrator",
        to_role=comms.BROADCAST,
        payload={"code": "team", "sh": sh_compact, "n": len(assignments)},
    )

    synced = 0
    for asn in assignments:
        role = asn.role if hasattr(asn, "role") else asn
        plain = str(getattr(asn, "item", "") or "")[:500]
        learn_block = format_niche_learning_block(
            role_id=role.id,
            model=getattr(role, "model", "inherit"),
            subagent_type=getattr(role, "subagent_type", ""),
        )[:2400]
        try:
            import peer_persona_rules as pr

            persona = pr.format_persona_rules_block(
                role.id, fallback_job_title=getattr(role, "job_title", role.id)
            )[:2000]
        except Exception:  # noqa: BLE001
            persona = ""
        vault_summary = (
            f"ASSIGNMENT: {plain}\n\n"
            f"PERSONA:\n{persona}\n\n"
            f"LEARNING:\n{learn_block}\n\n"
            f"SHARED CONTEXT:\n{shared_md[:2400]}"
        )
        comms.update_tasks(role.id, todo=[plain[:500]] if plain else None, summary=vault_summary)
        sum_payload: dict[str, Any] = {"code": "asn", "sh": sh_compact}
        if plain:
            sum_payload["ah"] = comms.path_hash(plain[:120])
        comms.post_glink(
            msg_type=comms.MSG_SUM,
            from_role="orchestrator",
            to_role=role.id,
            payload=sum_payload,
        )
        synced += 1
    return synced


def format_prompt_block(*, max_chars: int = 4500) -> str:
    text = load_team_context_markdown(max_chars=max_chars)
    if not text.strip():
        return ""
    return (
        "## Team context (all agents — read before Plan/Implement)\n\n"
        "Includes pivotal facts **and** minor signals that can change your output.\n"
        "Read canon docs each cycle: PROJECT_LEARNING, AGENT_SURVIVAL, CRITICAL_THINKING, HALLUCINATION_GUARD, "
        "AGENT_VS_HUMAN, IDEA_SYNTHESIS, AGENT_GATES, PRECISION_HABITS, OUTPUT_COMPARE, AGENT_MINI_APPS, "
        "SELF_DIAGNOSE, MEMORY_SPAN, WORK_ASSIGN, AGENT_ERROR_PLAYBOOK.\n\n"
        f"{text.strip()}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Write shared team context for all agents")
    parser.add_argument("--write", action="store_true", help="Write TEAM_CONTEXT.md + JSON")
    args = parser.parse_args()
    path = write_team_context(force=True)
    if args.write or not args.write:
        print(f"team-context: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
