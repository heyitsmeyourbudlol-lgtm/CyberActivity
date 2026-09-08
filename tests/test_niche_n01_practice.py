"""Tests for N01 P0 practice distill/eval/serve.

OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import niche_n01_practice as n01  # noqa: E402
import project_automation as auto  # noqa: E402


class NicheN01PracticeTests(unittest.TestCase):
    """OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04"""

    def test_land_proof_needle_present(self) -> None:
        recipe = (ROOT / "notes/niche_distill/RECIPE.md").read_text(encoding="utf-8")
        self.assertIn("OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04", recipe)
        self.assertRegex(recipe, r"(ckpt|checkpoint|\.pt\b|weights/)")
        src = (SCRIPTS / "niche_n01_practice.py").read_text(encoding="utf-8")
        self.assertIn("OVERSEER_NICHE_P0_PRACTICE_N01_2026_09_04", src)

    def test_niche_p0_practice_landed(self) -> None:
        self.assertTrue(auto._niche_p0_practice_landed())
        self.assertTrue(n01.CKPT_JSON.is_file())
        self.assertTrue(n01.WEIGHTS_PT.is_file())
        meta = json.loads(n01.CKPT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(meta.get("needle"), n01.NEEDLE)
        self.assertGreaterEqual(float(meta.get("heldout_accuracy") or 0), 0.90)

    def test_weights_pt_loads(self) -> None:
        blob = n01.load_weights_pt()
        self.assertEqual(blob.get("needle"), n01.NEEDLE)

    def test_heldout_accuracy_pass_bar(self) -> None:
        report = n01.run_train_eval(write=False)
        # Re-score existing heldout without rewrite when present.
        if n01.HELDOUT_JSONL.is_file():
            acc = n01.eval_heldout(n01.load_jsonl(n01.HELDOUT_JSONL))
        else:
            acc = report.heldout_accuracy
        self.assertGreaterEqual(acc, 0.90)

    def test_serve_predict_kit_needle(self) -> None:
        line = (
            "- [ ] **[kit] peer_loop: IDLE seed** — file `scripts/peer_loop.py`; "
            "Needle: `OVERSEER_PEER_IDLE_SEED_LOG_LAST_RESORT_2026_09_04`."
        )
        pred = n01.predict(line)
        self.assertTrue(pred["kit"])
        self.assertEqual(pred["scope"], "scripts/peer_loop.py")
        self.assertEqual(
            pred["needle"], "OVERSEER_PEER_IDLE_SEED_LOG_LAST_RESORT_2026_09_04"
        )

    def test_serve_compression_train_and_comms_tags(self) -> None:
        """Live Active tags — kit=false; scope from glob / bare RECIPE.md."""
        t4 = (
            "- [ ] [compression-train] T4 scale rung — N_logic 1e7→1e8; "
            "scripts/compression_t4_* or extend t3"
        )
        pred = n01.predict(t4)
        self.assertIs(pred["kit"], False)
        self.assertEqual(pred["scope"], "scripts/compression_t4_*")
        freeze = (
            "- [ ] [compression-train] Freeze TRAIN recipe card after T4 — "
            "COMPRESSION_TRAIN_RECIPE.md lock fields"
        )
        pred2 = n01.predict(freeze)
        self.assertIs(pred2["kit"], False)
        self.assertEqual(pred2["scope"], "notes/COMPRESSION_TRAIN_RECIPE.md")
        comms = (
            "- [x] **[comms-improve] Populate vault for Fact Checker** — "
            "role `fact_checker`"
        )
        pred3 = n01.predict(comms)
        self.assertIs(pred3["kit"], False)


if __name__ == "__main__":
    unittest.main()
