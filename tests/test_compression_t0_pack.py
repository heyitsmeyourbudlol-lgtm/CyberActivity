"""T0 packing proof — ALBERT-BitMoE + LoRA-Hive unique/pack gates.

OVERSEER_COMPRESSION_T0_PACK_2026_09_05
OVERSEER_COMPRESSION_T0_PACK_CACHE_2026_09_05
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import compression_t0_pack as t0  # noqa: E402


class CompressionT0PackTests(unittest.TestCase):
    """OVERSEER_COMPRESSION_T0_PACK_2026_09_05"""

    def test_needle_present(self) -> None:
        src = (SCRIPTS / "compression_t0_pack.py").read_text(encoding="utf-8")
        self.assertIn(t0.NEEDLE, src)
        self.assertIn(t0.CACHE_NEEDLE, src)
        novel = (ROOT / "notes/COMPRESSION_NOVEL.md").read_text(encoding="utf-8")
        self.assertIn(t0.NEEDLE, novel)

    def test_n_logic_targets(self) -> None:
        self.assertEqual(t0.N_L_TARGETS, (100_000, 1_000_000))

    def test_all_stacks_pass(self) -> None:
        rows = t0.run_all()
        self.assertEqual(len(rows), 4)
        stacks = {(r.stack, r.n_logic) for r in rows}
        self.assertEqual(
            stacks,
            {
                ("ALBERT-BitMoE", 100_000),
                ("ALBERT-BitMoE", 1_000_000),
                ("LoRA-Hive", 100_000),
                ("LoRA-Hive", 1_000_000),
            },
        )
        for r in rows:
            with self.subTest(stack=r.stack, n=r.n_logic):
                self.assertGreaterEqual(r.s_arith, t0.MIN_ARITH)
                self.assertTrue(r.pass_arith, msg=f"S={r.s_arith}")
                self.assertTrue(r.pass_pack, msg=f"bytes={r.packed_bytes} U={r.u_unique}")
                self.assertTrue(r.passed)
                self.assertEqual(r.quality, "N/A")
                # packed ≈ U/8 (± metadata)
                self.assertLessEqual(abs(r.packed_bytes - r.u_unique / 8.0), t0.META_BOUND_BYTES)
                self.assertEqual(r.payload_bytes, (r.u_unique + 7) // 8)
                self.assertEqual(r.packed_bytes, r.payload_bytes + r.meta_bytes)

    def test_prefer_near_100_when_easy(self) -> None:
        """Soft prefer ~100×; both stacks should clear well above 50."""
        for r in t0.run_all():
            with self.subTest(stack=r.stack, n=r.n_logic):
                self.assertGreaterEqual(r.s_arith, 80.0)

    def test_cli_json_exit_zero(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "compression_t0_pack.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["needle"], t0.NEEDLE)
        self.assertEqual(data["cache_needle"], t0.CACHE_NEEDLE)
        self.assertTrue(data["all_passed"])
        self.assertFalse(data["train_unlocked"])
        self.assertFalse(data["data_prune"])
        self.assertEqual(data["quality"], "N/A")
        self.assertEqual(len(data["results"]), 4)

    def test_summary_honesty_locks(self) -> None:
        """T0 packing proof must not imply train unlock or data prune."""
        payload = t0.summary_dict(t0.run_all())
        self.assertFalse(payload["train_unlocked"])
        self.assertFalse(payload["data_prune"])
        self.assertEqual(payload["quality"], "N/A")
        self.assertTrue(payload["all_passed"])
        self.assertEqual(payload["cache_needle"], t0.CACHE_NEEDLE)

    def test_pack_cache_roundtrip(self) -> None:
        """OVERSEER_COMPRESSION_T0_PACK_CACHE_2026_09_05 — dump/load fingerprint."""
        self.assertTrue(t0.pack_cache_roundtrip_ok())
        with tempfile.TemporaryDirectory(prefix="t0_pack_test_") as td:
            path = Path(td) / "pack.json"
            dump = t0.dump_pack_report(path)
            cached = t0.load_pack_report(dump)
            self.assertFalse(cached["train_unlocked"])
            self.assertFalse(cached["data_prune"])
            self.assertEqual(cached["cache_needle"], t0.CACHE_NEEDLE)
            # refuse train unlock
            bad = dict(cached)
            bad["train_unlocked"] = True
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                t0.load_pack_report(path)

    def test_ensure_default_pack_cli(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "compression_t0_pack.py"),
                "--ensure-default-pack",
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["pack_cache_ok"])
        self.assertTrue(data["all_passed"])
        self.assertFalse(data["train_unlocked"])
        self.assertFalse(data["data_prune"])
        self.assertEqual(data["pack_source"], "default_pack")
        self.assertTrue(t0.DEFAULT_PACK_PATH.is_file())
        loaded = t0.load_pack_report(t0.DEFAULT_PACK_PATH)
        self.assertEqual(loaded["needle"], t0.NEEDLE)
        self.assertEqual(loaded["cache_needle"], t0.CACHE_NEEDLE)

    def test_dual_sot_check_cli(self) -> None:
        """TRAIN-LOCK Dual SoT: pack report + T3 logit bank both green."""
        import compression_t3_bitdistill as t3

        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "compression_t0_pack.py"),
                "--dual-sot-check",
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["dual_sot"])
        self.assertTrue(data["dual_sot_ok"])
        self.assertTrue(data["pack_ok"])
        self.assertTrue(data["bank_ok"])
        self.assertFalse(data["train_unlocked"])
        self.assertFalse(data["data_prune"])
        self.assertEqual(data["pack_path"], str(t0.DEFAULT_PACK_PATH))
        self.assertEqual(data["bank_path"], str(t3.DEFAULT_BANK_PATH))
        # Falsifier: dual SoT green must never flip train_unlocked
        payload = t0.dual_sot_check()
        self.assertTrue(payload["dual_sot_ok"])
        self.assertIs(payload["train_unlocked"], False)

    def test_ensure_dual_sot_cli(self) -> None:
        """Refresh pack + logit bank then Dual SoT — still TRAIN-LOCKED."""
        import compression_t3_bitdistill as t3

        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "compression_t0_pack.py"),
                "--ensure-dual-sot",
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ensure_dual_sot"])
        self.assertTrue(data["dual_sot_ok"])
        self.assertTrue(data["pack_cache_ok"])
        self.assertTrue(data["bank_cache_ok"])
        self.assertTrue(data["pack_ok"])
        self.assertTrue(data["bank_ok"])
        self.assertFalse(data["train_unlocked"])
        self.assertFalse(data["data_prune"])
        self.assertEqual(data["pack_path"], str(t0.DEFAULT_PACK_PATH))
        self.assertEqual(data["bank_path"], str(t3.DEFAULT_BANK_PATH))
        # Falsifier: ensure path must not unlock train
        payload = t0.ensure_dual_sot()
        self.assertTrue(payload["dual_sot_ok"])
        self.assertIs(payload["train_unlocked"], False)


if __name__ == "__main__":
    unittest.main()
