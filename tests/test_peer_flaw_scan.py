#!/usr/bin/env python3
"""Tests for daily flaw-detection cross-review."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import peer_flaw_scan as flaw  # noqa: E402
import peer_roles as roles  # noqa: E402


class TestPeerFlawScan(unittest.TestCase):
    def test_build_review_pairs_count(self) -> None:
        pool = roles.load_roles()
        pairs = flaw.build_review_pairs(pool[:8])
        self.assertEqual(len(pairs), 56)
        self.assertEqual(len({(p["reviewer_role_id"], p["target_role_id"]) for p in pairs}), 56)
        for p in pairs:
            self.assertNotEqual(p["reviewer_role_id"], p["target_role_id"])
            self.assertTrue(p["reviewer_title"].startswith("Flaw Detection Scanner +"))

    def test_record_review_and_advance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rnd_path = Path(tmp) / "round.json"
            st_path = Path(tmp) / "state.json"
            with mock.patch.object(flaw, "ROUND_PATH", rnd_path):
                with mock.patch.object(flaw, "STATE_PATH", st_path):
                    flaw.start_round(force=True)
                    ok = flaw.record_review("factory_engineer", "verify_runner", "Add cache to verify gate")
                    self.assertTrue(ok)
                    rnd = json.loads(rnd_path.read_text())
                    done = sum(1 for p in rnd["pairs"] if p["status"] == "done")
                    self.assertEqual(done, 1)
                    vr = next(s for s in rnd["subjects"] if s["role_id"] == "verify_runner")
                    self.assertEqual(len(vr["reviews_received"]), 1)

    def test_scanner_title(self) -> None:
        role = roles.load_roles()[0]
        self.assertIn(role.job_title, flaw.scanner_title(role))

    def test_should_dispatch_after_daily_time(self) -> None:
        cfg = flaw.FlawScanConfig(enabled=True, daily_time="00:00", min_hour=0, min_minute=0)
        with mock.patch.object(flaw, "load_config", return_value=cfg):
            with mock.patch.object(flaw, "load_state", return_value={}):
                with mock.patch.object(flaw, "load_round", return_value=None):
                    with mock.patch.object(flaw, "start_round", return_value={"phase": flaw.PHASE_SCAN}):
                        self.assertTrue(flaw.should_dispatch_flaw_scan())


if __name__ == "__main__":
    unittest.main()
