#!/usr/bin/env python3
"""Tests for improve ↔ automation team integration."""

from __future__ import annotations

import sys
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import automation_improve as improve  # noqa: E402
import automation_team as team  # noqa: E402


class TestAutomationTeam(unittest.TestCase):
    def test_format_team_block_mentions_eight(self) -> None:
        text = team.format_team_block(quick=True)
        self.assertIn("Automation team", text)
        self.assertIn("8", text)
        self.assertIn("flaw", text.lower())

    def test_improve_plan_includes_team_block(self) -> None:
        signals = improve.ImproveSignals(
            live={"git": "clean", "tests": "ok", "queue_source": "empty", "open_items": []},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={},
            opportunities=[
                improve.Opportunity("speed", "Worktree pool", "ensure-pool", priority=20),
            ],
        )
        text = improve.build_plan_prompt(signals)
        self.assertIn("Automation team", text)
        self.assertIn("OPERATING_SYSTEM", text)

    def test_rank_team_opportunities_executable(self) -> None:
        opps = team.rank_team_opportunities(set())
        self.assertTrue(len(opps) >= 1)
        titles = " ".join(o.title.lower() for o in opps)
        self.assertTrue(
            "flaw" in titles or "debrief" in titles or "worktree" in titles or "roster" in titles
        )

    def test_hand_out_worker_pool_assigns_all_roles(self) -> None:
        logs: list[str] = []
        signals = improve.ImproveSignals(
            live={"open_items": ["**Fix tests** — run unittest"]},
            audit_ok=True,
            audit_warnings=[],
            audit_errors=[],
            queue_drift=[],
            loop_state={},
            opportunities=[],
        )
        with unittest.mock.patch.object(team, "hand_out_worker_pool", wraps=team.hand_out_worker_pool):
            handed = team.hand_out_worker_pool(log_fn=logs.append, signals=signals)
        self.assertGreaterEqual(len(handed), 1)
        self.assertTrue(any("hand_out:" in line for line in logs))


if __name__ == "__main__":
    unittest.main()
