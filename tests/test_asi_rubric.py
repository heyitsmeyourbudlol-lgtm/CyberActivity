#!/usr/bin/env python3
"""Tests for phased ASI rubric."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import asi_rubric  # noqa: E402
import automation_improve as improve  # noqa: E402


class TestAsiRubric(unittest.TestCase):
    def test_phases_defined(self) -> None:
        self.assertGreaterEqual(len(asi_rubric.ASI_PHASES), 4)
        completable = [p for p in asi_rubric.ASI_PHASES if p.completable]
        self.assertEqual(len(completable), 4)

    def test_empty_signals_low_pct(self) -> None:
        signals = improve.ImproveSignals(
            live={},
            audit_ok=False,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={},
        )
        result = asi_rubric.compute_asi_rubric(signals)
        self.assertLess(result.pct, 50)
        self.assertGreaterEqual(result.pct, 0)
        self.assertTrue(result.phases)
        self.assertTrue(result.current_phase_id)
        self.assertIsNotNone(result.next_plan)

    def test_last_cycle_improves_phase1_partial(self) -> None:
        signals = improve.ImproveSignals(
            live={},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={
                "last_cycle": {
                    "ts": 1.0,
                    "verify_ok": True,
                    "noop": False,
                }
            },
        )
        with mock.patch.object(asi_rubric, "_launchctl_running", return_value=True):
            with mock.patch.object(
                asi_rubric,
                "_log_has_recent",
                return_value=(True, "log ok"),
            ):
                result = asi_rubric.compute_asi_rubric(signals)
        phase1 = next(p for p in result.phases if p["id"] == "grounded_loop")
        self.assertGreater(phase1["score"], 0.5)

    def test_peer_log_recent_uses_last_cycle_not_log_tail(self) -> None:
        signals = improve.ImproveSignals(
            live={},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={
                "last_cycle": {
                    "ts": __import__("time").time() - 30,
                    "verify_ok": True,
                    "noop": False,
                }
            },
        )
        ctx = asi_rubric._probe_ctx(signals)
        score, evidence = asi_rubric._p1_peer_log_recent(ctx)
        self.assertEqual(score, 1.0)
        self.assertIn("last_cycle", evidence)

    def test_p2_verify_ok_soft_deferred_not_red(self) -> None:
        """OVERSEER_ASI_DEFERRED_SOFT_VERIFY_2026_09_07 — swarm deferred ≠ Phase-2 fail."""
        signals = improve.ImproveSignals(
            live={},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={
                "last_cycle": {
                    "ts": __import__("time").time(),
                    "verify_ok": False,
                    "noop": False,
                    "failure_type": "deferred",
                    "note": "verify deferred (swarm/lock)",
                }
            },
        )
        ctx = asi_rubric._probe_ctx(signals)
        score, evidence = asi_rubric._p2_verify_ok(ctx)
        self.assertEqual(score, 1.0)
        self.assertIn("soft deferred", evidence)
        self.assertIn("OVERSEER_ASI_DEFERRED_SOFT_VERIFY_2026_09_07", Path(asi_rubric.__file__).read_text())

    def test_compute_asi_progress_delegates(self) -> None:
        signals = improve.ImproveSignals(
            live={},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={},
        )
        asi = improve.compute_asi_progress(signals)
        self.assertTrue(asi.phases)
        self.assertIn("phase", asi.label.lower() + (asi.next_plan or "").lower())
        self.assertEqual(asi.pct, max(0, min(100, int(round(asi.raw * 100)))))

    def test_horizon_includes_phases(self) -> None:
        signals = improve.ImproveSignals(
            live={"tests": "ok"},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={},
            opportunities=[],
        )
        text = improve.build_horizon_markdown(signals, cycle=1)
        self.assertIn("Phased rubric", text)
        self.assertIn("Phase 1", text)
        payload = improve.horizon_payload(signals, cycle=1)
        self.assertIn("phases", payload["asi"])
        self.assertIn("current_phase_id", payload["asi"])

    def test_format_phase_advance_plan_mentions_met_and_next(self) -> None:
        text = asi_rubric.format_phase_advance_plan(
            "grounded_loop", "verify_memory"
        )
        self.assertIn("MET", text)
        self.assertIn("Verify", text)
        self.assertIn("work kit", text.lower())
        self.assertIn("automation_improve", text)

    def test_work_kit_plan_forbids_self_improve(self) -> None:
        plan = asi_rubric.work_kit_plan_for_phase("parallel_orchestration")
        lowered = plan.lower()
        self.assertIn("do not edit automation_improve", lowered)
        self.assertTrue("worktree" in lowered or "peer" in lowered)

    def test_peer_probe_ignores_sibling_project_label(self) -> None:
        """Phase 1 must not credit ram-peer-loop when Automation peer is down."""
        signals = improve.ImproveSignals(
            live={},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={},
        )
        ctx = asi_rubric._probe_ctx(signals)
        self.assertNotIn("com.togi.ram-peer-loop", ctx["peer_labels"])
        project_label = str(ctx["peer_labels"][0] or "")
        self.assertTrue(project_label)
        self.assertIn("automation", project_label.lower())

        def fake_running(label: str) -> bool:
            return label == "com.togi.ram-peer-loop"

        with mock.patch.object(asi_rubric, "_launchctl_running", side_effect=fake_running):
            score, evidence = asi_rubric._p1_peer_daemon(ctx)
        self.assertEqual(score, 0.0)
        self.assertIn("not running", evidence)


    def test_launchctl_running_falls_back_to_systemd(self) -> None:
        with mock.patch.object(asi_rubric.subprocess, "run", side_effect=FileNotFoundError("launchctl")):
            with mock.patch.object(asi_rubric, "_systemd_user_active", return_value=True) as sysd:
                self.assertTrue(asi_rubric._launchctl_running("com.togi.automation-hub-peer-loop"))
                sysd.assert_called_with("peer-loop.service")


class TestEnqueuePhasePlan(unittest.TestCase):
    def _signals(self) -> improve.ImproveSignals:
        return improve.ImproveSignals(
            live={},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={},
        )

    def test_active_phase_enqueues_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            work = tmp_path / "WORK_QUEUE.md"
            ctx = tmp_path / "self_improve_context.md"
            work.write_text("# Q\n\n## Active\n\n")
            ctx.write_text("# C\n\n## Remaining work\n\n")
            logs: list[str] = []
            with mock.patch.object(
                improve, "_queue_paths_for_enqueue", return_value=(ctx, work)
            ):
                with mock.patch.object(
                    improve,
                    "compute_asi_progress",
                    return_value=improve.AsiProgress(
                        pct=10,
                        label="active phase",
                        scale=100,
                        raw=0.1,
                        dimensions=[],
                        phases=[],
                        current_phase_id="grounded_loop",
                        next_plan="Stabilize peer daemons",
                    ),
                ):
                    out = improve.enqueue_phase_plan(
                        self._signals(), log_fn=logs.append, previous_phase_id=None
                    )
            self.assertIsNotNone(out)
            self.assertIn("Harden active capability", out or "")
            self.assertIn("factory:grounded_loop", out or "")
            body = work.read_text()
            self.assertIn("grounded_loop", body)
            self.assertIn("Stabilize peer daemons", body)

    def test_phase_advance_enqueues_complete_to_plan_next(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            work = tmp_path / "WORK_QUEUE.md"
            ctx = tmp_path / "self_improve_context.md"
            work.write_text("# Q\n\n## Active\n\n")
            ctx.write_text("# C\n\n## Remaining work\n\n")
            logs: list[str] = []
            with mock.patch.object(
                improve, "_queue_paths_for_enqueue", return_value=(ctx, work)
            ):
                with mock.patch.object(
                    improve,
                    "compute_asi_progress",
                    return_value=improve.AsiProgress(
                        pct=30,
                        label="advanced",
                        scale=100,
                        raw=0.3,
                        dimensions=[],
                        phases=[],
                        current_phase_id="verify_memory",
                        next_plan="Fix verify",
                    ),
                ):
                    out = improve.enqueue_phase_plan(
                        self._signals(),
                        log_fn=logs.append,
                        previous_phase_id="grounded_loop",
                    )
            self.assertIsNotNone(out)
            self.assertIn("complete → next", out or "")
            self.assertIn("factory:verify_memory", out or "")
            body = work.read_text()
            self.assertIn("MET", body)
            self.assertIn("verify_memory", body)
            with mock.patch.object(
                improve, "_queue_paths_for_enqueue", return_value=(ctx, work)
            ):
                with mock.patch.object(
                    improve,
                    "compute_asi_progress",
                    return_value=improve.AsiProgress(
                        pct=30,
                        label="advanced",
                        scale=100,
                        raw=0.3,
                        dimensions=[],
                        phases=[],
                        current_phase_id="verify_memory",
                        next_plan="Fix verify",
                    ),
                ):
                    again = improve.enqueue_phase_plan(
                        self._signals(),
                        log_fn=logs.append,
                        previous_phase_id="grounded_loop",
                    )
            self.assertIsNone(again)

    def test_load_previous_asi_phase_id_from_horizon_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "improve-horizon.json"
            path.write_text(
                json.dumps({"asi": {"current_phase_id": "verify_memory"}}) + "\n"
            )
            with mock.patch.object(improve, "HORIZON_JSON_PATH", path):
                self.assertEqual(
                    improve._load_previous_asi_phase_id(), "verify_memory"
                )


class TestLogTailSeek(unittest.TestCase):
    """LOG_TAIL_SEEK_2026_09_05 — seek last N bytes; do not full-read huge logs."""

    def test_read_log_tail_seeks_not_full_decode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "big.log"
            # ~2MB prefix + distinctive tail (mirrors multi-MB improve-loop.log).
            path.write_bytes(b"X" * (2 * 1024 * 1024) + b"wake peer\nhand_out:1\n")
            with mock.patch.object(Path, "read_text", autospec=True) as rt:
                tail = asi_rubric._read_log_tail(path, tail_bytes=64)
                rt.assert_not_called()
            self.assertIn("wake peer", tail)
            self.assertIn("hand_out:1", tail)
            self.assertLessEqual(len(tail.encode("utf-8")), 64)

    def test_log_has_recent_any_matches_tail_needle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "improve-loop.log"
            path.write_bytes(b"noise\n" * 5000 + b"drive work kit ok\n")
            ok, ev = asi_rubric._log_has_recent_any(
                path,
                ("wake peer", "hand_out:", "drive work kit"),
                max_age_sec=3600.0,
                tail_bytes=256,
            )
            self.assertTrue(ok)
            self.assertIn("drive work kit", ev)


if __name__ == "__main__":
    unittest.main()
