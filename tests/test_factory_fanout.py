#!/usr/bin/env python3
"""Tests for factory_fanout path resolution and config."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import factory_fanout  # noqa: E402


class FactoryFanoutTests(unittest.TestCase):
    def test_resolve_translates_missing_mac_path(self) -> None:
        def fake_is_dir(self: Path) -> bool:
            return str(self).startswith("/home/arnavrastogi/")

        with mock.patch.object(
            factory_fanout,
            "_path_roots",
            return_value=(Path("/Users/togi"), Path("/home/arnavrastogi")),
        ), mock.patch.object(Path, "is_dir", fake_is_dir):
            got = factory_fanout.resolve_repo_path("/Users/togi/CPT")
            self.assertIsNotNone(got)
            self.assertTrue(str(got).endswith("arnavrastogi/CPT"))

    def test_status_filter_defaults(self) -> None:
        with mock.patch.object(factory_fanout, "_fanout_cfg", return_value={}):
            self.assertIn("unaudited", factory_fanout.status_filter())

    def test_load_candidates_skips_hub(self) -> None:
        registry = {
            "repos": [
                {"name": "Hub", "path": str(ROOT), "status": "unaudited"},
                {"name": "CPT", "path": "/Users/togi/CPT", "status": "unaudited"},
            ]
        }
        with mock.patch("factory_fanout.REGISTRY") as reg:
            reg.is_file.return_value = True
            reg.read_text.return_value = json.dumps(registry)
            with mock.patch.object(
                factory_fanout,
                "resolve_repo_path",
                side_effect=lambda p: None if str(ROOT) in p else Path("/remote/CPT"),
            ):
                items = factory_fanout.load_candidates()
                self.assertEqual(len(items), 1)
                self.assertEqual(items[0]["name"], "CPT")

    def test_write_cycle_log_persists(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            cycle = Path(td) / "fanout_cycle.json"
            hub = Path(td) / "factory-fanout.log"
            with mock.patch.object(factory_fanout, "CYCLE_LOG", cycle), mock.patch.object(
                factory_fanout, "HUB_FANOUT_LOG", hub
            ), mock.patch.object(factory_fanout, "_cursor_agent_count", return_value=24), mock.patch.object(
                factory_fanout, "_worktree_pool_count", return_value=97
            ), mock.patch.object(
                factory_fanout.auto, "parallel_peer_floor", return_value=96
            ):
                path = factory_fanout.write_cycle_log(
                    {"ts": "2026-09-06T00:00:00+00:00", "candidates": 0, "ok": 0, "fail": 0, "results": []},
                    log_fn=lambda _m: None,
                )
                self.assertEqual(path, cycle)
                data = json.loads(cycle.read_text(encoding="utf-8"))
                self.assertTrue(data["verify_ok"])
                self.assertTrue(data["pool_ge_floor"])
                self.assertFalse(data["agents_ge_floor"])
                self.assertTrue(hub.is_file())


if __name__ == "__main__":
    unittest.main()
