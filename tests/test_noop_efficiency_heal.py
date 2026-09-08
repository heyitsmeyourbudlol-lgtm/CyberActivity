#!/usr/bin/env python3
"""OVERSEER_NOOP_EFFICIENCY_2026_09_07 — noop backoff + MET theater close."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import peer_loop  # noqa: E402
import project_automation as auto  # noqa: E402


class TestNoopSpinGuards(unittest.TestCase):
    def test_should_spin_false_on_flat_fp_even_if_noop_cleared(self) -> None:
        lc = {
            "noop": False,
            "verify_ok": True,
            "queue_fp_before": "aaaaaaaa",
            "queue_fp": "aaaaaaaa",
            "rc": 0,
        }
        self.assertFalse(peer_loop._should_spin_after_agent_cycle(lc))

    def test_should_spin_true_when_fp_advances(self) -> None:
        lc = {
            "noop": False,
            "verify_ok": True,
            "queue_fp_before": "aaaaaaaa",
            "queue_fp_after": "bbbbbbbb",
            "rc": 0,
        }
        self.assertTrue(peer_loop._should_spin_after_agent_cycle(lc))

    def test_noop_remaining_does_not_clear_via_never_delay(self) -> None:
        state = {
            "last_cycle": {
                "noop": True,
                "verify_ok": True,
                "ts": 10_000_000_000.0,
                "queue_fp_before": "a",
                "queue_fp": "a",
            }
        }
        with patch.object(peer_loop.auto, "CFG", {"autonomy_never_delay_on_error": True}):
            with patch("peer_transcript.noop_backoff_remaining", return_value=30.0):
                with patch("peer_error_adapt.clear_autonomy_delays") as clear:
                    left = peer_loop._noop_remaining_or_clear(
                        state=state, log_fn=lambda _m: None, backoff_sec=30.0
                    )
        self.assertEqual(left, 30.0)
        clear.assert_not_called()


class TestMetTheaterClose(unittest.TestCase):
    def test_resolve_satisfied_met_theater_closes_cod_and_noop(self) -> None:
        md = """## Active

- [ ] **Unblock dirty tree for peer_loop dispatch** — continue_on_dirty keeps coding
- [ ] **Fix verify gate — unblock worker dispatch** — self-heal seeded last_cycle
- [ ] **Prove improve→peer closed loop** — peer + improve daemons running
- [ ] **[auto] Break noop loop** — Queue fingerprint unchanged after ok cycle
- [ ] **Break noop loop — advance or shrink queue** — Last ok cycle left queue fingerprint unchanged
- [ ] **Keep real work** — file-scoped creative item
"""
        # First pass without close_noop (verify_soft_ok False) still closes dirty when COD
        mid, n1 = auto.resolve_satisfied_met_theater(
            md,
            continue_on_dirty=True,
            peer_up=True,
            improve_up=True,
            verify_soft_ok=False,
            open_active_count=6,
        )
        self.assertGreaterEqual(n1, 1)
        self.assertIn("- [x] **Unblock dirty tree", mid)
        # Second pass closes verify/loop/noop twins
        out, n2 = auto.resolve_satisfied_met_theater(
            mid,
            continue_on_dirty=True,
            peer_up=True,
            improve_up=True,
            verify_soft_ok=True,
            open_active_count=5,
        )
        self.assertGreaterEqual(n2, 3)
        self.assertIn("- [x] **Fix verify gate", out)
        self.assertIn("- [x] **Prove improve→peer", out)
        self.assertIn("- [x] **[auto] Break noop loop**", out)
        self.assertIn("- [x] **Break noop loop — advance or shrink queue**", out)
        self.assertIn("- [ ] **Keep real work**", out)

    def test_needles_present(self) -> None:
        pl = (Path(__file__).resolve().parents[1] / "scripts" / "peer_loop.py").read_text()
        pa = (
            Path(__file__).resolve().parents[1] / "scripts" / "project_automation.py"
        ).read_text()
        self.assertIn("OVERSEER_FLAT_FP_NO_SPIN_2026_09_07", pl)
        self.assertIn("OVERSEER_NOOP_BACKOFF_NOT_ERROR_2026_09_07", pl)
        self.assertIn("OVERSEER_PRE_DISPATCH_NOOP_CLEAR_FP_2026_09_07", pl)
        self.assertIn("OVERSEER_MET_THEATER_CLOSE_2026_09_07", pa)


if __name__ == "__main__":
    unittest.main()
