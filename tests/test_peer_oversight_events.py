#!/usr/bin/env python3
"""Tests for peer_oversight event-based dispatch."""

from __future__ import annotations

import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import peer_oversight_events as events  # noqa: E402


class TestOversightEvents(unittest.TestCase):
    def setUp(self) -> None:
        self._live_patch = mock.patch.object(events, "scan_live_error_hits", return_value=[])
        self._live_patch.start()

    def tearDown(self) -> None:
        self._live_patch.stop()

    def test_noop_triggers_stagnation(self) -> None:
        ctx = {
            "queue_count": 10,
            "phase": "IDLE",
            "noop_backoff_sec": 0,
            "last_cycle": {"noop": True, "verify_ok": True, "git_head": "abc"},
            "kit": {"factory_pct": 50, "asi_pct": 80},
            "bottlenecks": [],
        }
        flaws = {"open": 0, "critical": 0, "high": 0}
        rep = events.evaluate_stagnation(ctx, flaws, state={})
        self.assertTrue(rep.should_dispatch)
        self.assertTrue(any("noop" in r.lower() for r in rep.reasons))

    def test_advancing_factory_held(self) -> None:
        ctx = {
            "queue_count": 5,
            "phase": "WORKING",
            "noop_backoff_sec": 0,
            "last_cycle": {"noop": False, "verify_ok": True, "git_head": "def"},
            "kit": {"factory_pct": 55, "asi_pct": 80, "queue_drift": 0, "daemons": {"peer_loop": True, "improve_loop": True}},
            "bottlenecks": [],
            "daemon_running": True,
        }
        flaws = {"open": 2, "critical": 0, "high": 0}
        state = {
            "snapshots": [
                {"factory_pct": 50, "queue_fp": "x", "git_head": "abc"},
                {"factory_pct": 52, "queue_fp": "y", "git_head": "def"},
            ],
            "last_agent_ts": 0,
        }
        rep = events.evaluate_stagnation(ctx, flaws, state=state)
        ok, _, hold = events.should_dispatch(ctx, flaws, state=state, dispatch_enabled=True, stagnation=rep)
        self.assertFalse(ok)
        self.assertTrue(any("advancing" in h.lower() for h in hold))

    def test_event_mode_default(self) -> None:
        with mock.patch.object(events.cfg_mod, "CFG", {}):
            self.assertEqual(events.agent_dispatch_mode(), "event")
            self.assertTrue(events.high_expectations_enabled())

    def test_dual_brain_mismatch_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wq = root / "notes" / "WORK_QUEUE.md"
            ctx = root / "scripts" / "self_improve_context.md"
            wq.parent.mkdir(parents=True)
            ctx.parent.mkdir(parents=True)
            wq.write_text("## Active\n\n- [ ] **only-wq** — task\n", encoding="utf-8")
            ctx.write_text(
                "## Remaining work (priority order)\n\n- [ ] **only-ctx** — task\n",
                encoding="utf-8",
            )
            with mock.patch.object(events.auto, "WORK_QUEUE_PATH", wq), mock.patch.object(
                events.auto, "CONTEXT_PATH", ctx
            ):
                self.assertTrue(events._dual_brain_mismatch())

    def test_dual_brain_mismatch_false_when_only_backlog_differs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wq = root / "notes" / "WORK_QUEUE.md"
            ctx = root / "scripts" / "self_improve_context.md"
            wq.parent.mkdir(parents=True)
            ctx.parent.mkdir(parents=True)
            wq.write_text(
                "## Active\n\n- [ ] **same** — task\n\n"
                "## Backlog (deferred — noop shrink)\n\n- [ ] **parked** — later\n",
                encoding="utf-8",
            )
            ctx.write_text(
                "## Remaining work (priority order)\n\n- [ ] **same** — task\n",
                encoding="utf-8",
            )
            with mock.patch.object(events.auto, "WORK_QUEUE_PATH", wq), mock.patch.object(
                events.auto, "CONTEXT_PATH", ctx
            ):
                self.assertFalse(events._dual_brain_mismatch())

    def test_dual_brain_mismatch_false_when_synced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wq = root / "notes" / "WORK_QUEUE.md"
            ctx = root / "scripts" / "self_improve_context.md"
            wq.parent.mkdir(parents=True)
            ctx.parent.mkdir(parents=True)
            body = "## Active\n\n- [ ] **same** — task\n"
            wq.write_text(body, encoding="utf-8")
            ctx.write_text(
                "## Remaining work (priority order)\n\n- [ ] **same** — task\n",
                encoding="utf-8",
            )
            with mock.patch.object(events.auto, "WORK_QUEUE_PATH", wq), mock.patch.object(
                events.auto, "CONTEXT_PATH", ctx
            ):
                self.assertFalse(events._dual_brain_mismatch())

    def test_critical_never_delayed_when_policy_on(self) -> None:
        ctx = {
            "queue_count": 3,
            "phase": "WORKING",
            "noop_backoff_sec": 0,
            "last_cycle": {"noop": False, "verify_ok": False},
            "kit": {"daemons": {"peer_loop": True, "improve_loop": True}},
            "bottlenecks": [],
            "daemon_running": True,
        }
        flaws = {"open": 0, "critical": 0, "high": 0}
        state = {"last_agent_ts": time.time() - 9.0}
        with mock.patch.object(events.cfg_mod, "CFG", {"autonomy_never_delay_on_error": True}):
            rep = events.evaluate_stagnation(ctx, flaws, state=state)
            ok, _, hold = events.should_dispatch(
                ctx, flaws, state=state, dispatch_enabled=True, stagnation=rep
            )
        self.assertTrue(rep.critical or rep.should_dispatch)
        self.assertTrue(ok)
        self.assertFalse(any("min gap" in h for h in hold))

    def test_live_log_error_is_critical(self) -> None:
        self._live_patch.stop()
        try:
            with mock.patch.object(
                events,
                "scan_live_error_hits",
                return_value=["live log: plan-gate BLOCKED — fix fail rows"],
            ):
                ctx = {
                    "queue_count": 3,
                    "phase": "WORKING",
                    "noop_backoff_sec": 0,
                    "last_cycle": {"noop": False, "verify_ok": True},
                    "kit": {"daemons": {"peer_loop": True, "improve_loop": True}},
                    "bottlenecks": [],
                    "daemon_running": True,
                }
                rep = events.evaluate_stagnation(ctx, {"open": 0, "critical": 0, "high": 0}, state={})
            self.assertTrue(rep.critical)
            self.assertTrue(rep.should_dispatch)
            self.assertTrue(any("plan-gate" in r for r in rep.reasons))
        finally:
            self._live_patch = mock.patch.object(events, "scan_live_error_hits", return_value=[])
            self._live_patch.start()


    def test_skip_live_hit_echo_and_auth_ready(self) -> None:
        echo = "live log: auth not ready —  (live log: auth not ready — pt: cleared au)"
        self.assertTrue(events._skip_live_hit_line(echo, "auth not ready"))
        primary = "2026-09-04 01:10:00 terminal: auth not ready — not logged in"
        with mock.patch.object(events, "_auth_currently_ready", return_value=True):
            self.assertTrue(events._skip_live_hit_line(primary, "auth not ready"))
        with mock.patch.object(events, "_auth_currently_ready", return_value=False):
            self.assertFalse(events._skip_live_hit_line(primary, "auth not ready"))

    def test_skip_local_cycle_timeout_from_live_hits(self) -> None:
        """OVERSEER_SKIP_LOCAL_CYCLE_TIMEOUT_2026_09_07 — improve quiet-wait theater."""
        line = "2026-09-07 15:58:16  mechanical: local cycle timed out after 90s"
        self.assertTrue(events._skip_live_hit_line(line, "timed out after"))
        self.assertTrue(events._skip_live_hit_line(line, " TimeoutExpired"))
        hard = "2026-09-07 15:58:16  verify: unittest timed out after 120s"
        self.assertFalse(events._skip_live_hit_line(hard, "timed out after"))

    def test_skip_nested_heal_all_timeout_from_live_hits(self) -> None:
        """OVERSEER_SKIP_NESTED_HEAL_ALL_TIMEOUT_2026_09_07"""
        line = (
            "error-adapt: cmd failed (Command '['/home/arnavrastogi/Automation/scripts/peer', "
            "'heal-all']' timed out after 120.0 seconds)"
        )
        self.assertTrue(events._skip_live_hit_line(line, "timed out after"))
        hard = "2026-09-07 15:58:16  verify: unittest timed out after 120s"
        self.assertFalse(events._skip_live_hit_line(hard, "timed out after"))


if __name__ == "__main__":
    unittest.main()
