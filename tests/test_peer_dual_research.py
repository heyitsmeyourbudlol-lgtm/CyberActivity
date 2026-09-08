#!/usr/bin/env python3
"""Tests for peer_dual_research — efficiency + output lanes."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import peer_dual_research as dr  # noqa: E402


class TestPeerDualResearch(unittest.TestCase):
    def test_make_id_stable(self) -> None:
        a = dr.ResearchFinding.make_id("efficiency", "noop loop")
        b = dr.ResearchFinding.make_id("efficiency", "noop loop")
        self.assertEqual(a, b)

    def test_merge_tracks_new(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = Path(tmp) / "findings.json"
            with mock.patch.object(dr, "FINDINGS_PATH", findings):
                f = dr.ResearchFinding(
                    id="abc",
                    lane="efficiency",
                    severity="high",
                    title="Test",
                    evidence="detail",
                    action="fix",
                    enqueue_title="Fix test",
                )
                open_f, new_f = dr.merge_findings("efficiency", [f])
                self.assertEqual(len(new_f), 1)
                open_f2, new_f2 = dr.merge_findings("efficiency", [f])
                self.assertEqual(len(new_f2), 0)

    def test_build_sync_digest(self) -> None:
        eff = dr.LaneReport(
            lane="efficiency",
            findings=[
                dr.ResearchFinding(
                    id="1",
                    lane="efficiency",
                    severity="high",
                    title="Speed win",
                    evidence="slow path",
                    action="./scripts/peer pre-dispatch",
                )
            ],
        )
        out = dr.LaneReport(
            lane="output",
            findings=[
                dr.ResearchFinding(
                    id="2",
                    lane="output",
                    severity="high",
                    title="External proof",
                    evidence="registry idle",
                    action="factory-sprint",
                )
            ],
        )
        md = dr.build_sync_digest(eff, out)
        self.assertIn("Research sync", md)
        self.assertIn("Efficiency lane", md)
        self.assertIn("Output lane", md)

    def test_findings_to_opportunities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = Path(tmp) / "findings.json"
            payload = {
                "items": {
                    "x1": {
                        "lane": "efficiency",
                        "severity": "high",
                        "title": "Compact queue",
                        "enqueue_title": "Compact queue to 12",
                        "evidence": "55 items",
                        "action": "compact",
                        "status": "open",
                    }
                }
            }
            findings.write_text(json.dumps(payload), encoding="utf-8")
            with mock.patch.object(dr, "FINDINGS_PATH", findings):
                opps = dr.findings_to_opportunities(known=set())
        self.assertEqual(len(opps), 1)
        self.assertEqual(opps[0]["category"], "efficiency")

    def test_probe_efficiency_noop(self) -> None:
        with mock.patch.object(dr, "_open_queue_items", return_value=["item"] * 20):
            with mock.patch.object(dr, "_loop_state", return_value={"noop": True}):
                with mock.patch.object(dr.cfg_mod, "CFG", {"role_pool_expand": False}):
                    findings = dr.probe_efficiency()
        titles = {f.title for f in findings}
        self.assertIn("Executable queue bloated", titles)
        self.assertIn("Noop loop — zero queue advance", titles)

    def test_soft_verify_false_skips_fix_verify_gate_theater(self) -> None:
        """OVERSEER_SKIP_SOFT_VERIFY_GATE_THEATER — deferred≠enqueue Fix verify gate."""
        soft = {
            "verify_ok": False,
            "failure_type": "deferred",
            "note": "verify deferred (swarm/lock)",
        }
        self.assertTrue(dr._soft_verify_false(soft))
        with mock.patch.object(dr, "_open_queue_items", return_value=[]):
            with mock.patch.object(dr, "_loop_state", return_value=soft):
                with mock.patch.object(dr.cfg_mod, "CFG", {"role_pool_expand": False}):
                    findings = dr.probe_efficiency()
        titles = {f.title for f in findings}
        self.assertNotIn("Verify gate blocking dispatch", titles)
        hard = {"verify_ok": False, "failure_type": "tests", "note": "unittest failed"}
        self.assertFalse(dr._soft_verify_false(hard))
        with mock.patch.object(dr, "_open_queue_items", return_value=[]):
            with mock.patch.object(dr, "_loop_state", return_value=hard):
                with mock.patch.object(dr.cfg_mod, "CFG", {"role_pool_expand": False}):
                    findings = dr.probe_efficiency()
        self.assertIn("Verify gate blocking dispatch", {f.title for f in findings})

    def test_run_cycle_digest_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            findings = Path(tmp) / "findings.json"
            digest = Path(tmp) / "sync.md"
            with mock.patch.object(dr, "STATE_PATH", state):
                with mock.patch.object(dr, "FINDINGS_PATH", findings):
                    with mock.patch.object(dr, "SYNC_DIGEST", digest):
                        with mock.patch.object(dr, "EFFICIENCY_DIGEST", Path(tmp) / "eff.md"):
                            with mock.patch.object(dr, "OUTPUT_DIGEST", Path(tmp) / "out.md"):
                                with mock.patch.object(dr, "research_enabled", return_value=True):
                                    with mock.patch.object(dr, "probe_efficiency", return_value=[]):
                                        with mock.patch.object(dr, "probe_output", return_value=[]):
                                            report = dr.run_research_cycle(digest_only=True, force=True)
        self.assertIn("digests", report)
        self.assertGreater(len(report.get("digests") or []), 0)

    def test_merge_lane_digest_keeps_agent_notes_and_extras(self) -> None:
        existing = (
            "# Output research\n\n"
            "## This cycle\n\n- old probe\n\n"
            "## Kit expansion freeze (Phase 1)\n\n| Metric | Gate |\n\n"
            "## Agent notes\n\n"
            "- **2026-09-02 22:45** — restore + Rekor deferral\n"
        )
        new = dr.build_lane_digest(
            lane="output",
            open_findings=[],
            new_findings=[],
            actions=["probed 0 finding(s); 0 new"],
            enqueued=[],
        )
        merged = dr.merge_lane_digest(existing, new)
        self.assertIn("2026-09-02 22:45", merged)
        self.assertIn("Kit expansion freeze", merged)
        self.assertNotIn(dr.AGENT_NOTES_STUB, merged.split("## Agent notes", 1)[-1])

    def test_preserve_sync_lane_unions_output_bullets(self) -> None:
        existing = (
            "# Research sync\n\n"
            "## Output lane (monster factory)\n\n"
            "- **[info]** Hub registry honesty — 0 adapted\n\n"
            "## Executable enqueue (improve + peer)\n\n- (none this cycle)\n"
        )
        new = (
            "# Research sync\n\n"
            "## Output lane (monster factory)\n\n"
            "- **[medium]** Factory progress below self-sufficient target — ./scripts/peer progress\n\n"
            "## Executable enqueue (improve + peer)\n\n- (none this cycle)\n"
        )
        out = dr.preserve_sync_lane(existing, new, "Output lane (monster factory)")
        self.assertIn("Factory progress", out)
        self.assertIn("Hub registry honesty", out)

    def test_probe_output_factory_progress_fail_no_unboundlocal(self) -> None:
        """except path must not UnboundLocalError on has_external/has_artifact."""
        boom = RuntimeError("compute_report boom")

        class _FP:
            @staticmethod
            def compute_factory_progress():
                raise boom

        with mock.patch.dict(sys.modules, {"factory_progress": _FP}), mock.patch.object(
            dr.auto, "factory_meter_mode", return_value="self_sufficient"
        ), mock.patch.object(dr, "_open_queue_items", return_value=[]), mock.patch.object(
            dr, "ROOT", Path("/tmp/no-registry-here")
        ):
            findings = dr.probe_output()
        titles = {f.title for f in findings}
        self.assertIn("Factory progress probe failed", titles)
        self.assertTrue(
            all("external proof" not in (f.enqueue_title or "").lower() for f in findings)
        )

    def test_cmd_install_linux_calls_linux_install_daemon(self) -> None:
        """OVERSEER_DUAL_RESEARCH_LINUX_INSTALL_2026_09_06 — no launchctl on Linux."""
        import peer_self_heal as heal

        with mock.patch.object(dr.sys, "platform", "linux"):
            with mock.patch.object(heal, "ensure_canonical_module"):
                with mock.patch.object(
                    heal, "linux_install_daemon", return_value="unit ok"
                ) as inst:
                    with mock.patch.object(dr.subprocess, "run") as run:
                        rc = dr.cmd_install()
        self.assertEqual(rc, 0)
        inst.assert_called_once_with("dual-research")
        run.assert_not_called()

    def test_cmd_uninstall_linux_calls_linux_uninstall_daemon(self) -> None:
        """OVERSEER_DUAL_RESEARCH_LINUX_INSTALL_2026_09_06"""
        import peer_self_heal as heal

        with mock.patch.object(dr.sys, "platform", "linux"):
            with mock.patch.object(heal, "ensure_canonical_module"):
                with mock.patch.object(
                    heal, "linux_uninstall_daemon", return_value="gone"
                ) as un:
                    with mock.patch.object(dr.subprocess, "run") as run:
                        rc = dr.cmd_uninstall()
        self.assertEqual(rc, 0)
        un.assert_called_once_with("dual-research")
        run.assert_not_called()

    def test_cmd_status_linux_uses_systemd(self) -> None:
        """OVERSEER_DUAL_RESEARCH_LINUX_INSTALL_2026_09_06"""
        import peer_self_heal as heal

        with mock.patch.object(dr.sys, "platform", "linux"):
            with mock.patch.object(heal, "_systemd_user_active", return_value=True):
                with mock.patch.object(dr, "_load_state", return_value={}):
                    with mock.patch.object(dr.subprocess, "run") as run:
                        rc = dr.cmd_status()
        self.assertEqual(rc, 0)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
