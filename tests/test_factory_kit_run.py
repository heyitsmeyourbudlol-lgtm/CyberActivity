"""Guards for factory_kit_run dry-run / registry resolve."""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load():
    path = SCRIPTS / "factory_kit_run.py"
    spec = importlib.util.spec_from_file_location("factory_kit_run", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["factory_kit_run"] = mod
    spec.loader.exec_module(mod)
    return mod


class FactoryKitRunTests(unittest.TestCase):
    def test_dry_run_cpt_ok(self) -> None:
        mod = _load()
        report = mod.run_kit("CPT", dry_run=True, stop_after="C")
        self.assertTrue(report.get("ok"), report)
        self.assertEqual(report.get("dry_run"), True)
        steps = {s.get("step") for s in report.get("steps") or []}
        self.assertIn("A_adapt", steps)
        self.assertIn("B_verify", steps)
        self.assertIn("C_worktree", steps)

    def test_dry_run_cpt_through_e(self) -> None:
        """Phase2 A→E dry-run — OVERSEER_KIT_RUN_AE_2026_09_07."""
        mod = _load()
        report = mod.run_kit("CPT", dry_run=True, stop_after="E")
        self.assertTrue(report.get("ok"), report)
        steps = {s.get("step") for s in report.get("steps") or []}
        self.assertEqual(
            steps,
            {"A_adapt", "B_verify", "C_worktree", "D_artifact", "E_writeback"},
        )
        self.assertEqual(report.get("needle_ae"), "OVERSEER_KIT_RUN_AE_2026_09_07")

    def test_artifact_blocked_without_origin(self) -> None:
        mod = _load()
        # Honest blocked receipt is ok=True (Phase 2 stamp path)
        d = mod.step_artifact(
            Path("/tmp"),
            worktree_path=None,
            branch="peer/kit-test",
            dry_run=False,
        )
        self.assertTrue(d.get("ok"), d)
        self.assertEqual(d.get("mode"), "blocked_receipt")
        reasons = (d.get("blocked_receipt") or {}).get("reasons") or []
        self.assertTrue(reasons, d)

    def test_adapt_cmd_uses_target_not_root(self) -> None:
        """Live A must pass --target; --root is unrecognized (Phase2 false-green)."""
        mod = _load()
        a = mod.step_adapt(Path("/home/arnavrastogi/CPT"), dry_run=True)
        cmd = a.get("cmd") or []
        self.assertIn("--target", cmd)
        self.assertNotIn("--root", cmd)
        self.assertIn("/home/arnavrastogi/CPT", cmd)

    def test_find_repo_cpt(self) -> None:
        mod = _load()
        row = mod.find_repo(mod.load_registry(), "CPT")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertIn("CPT", str(row.get("name")))

    def test_home_mirrors_no_users_literal(self) -> None:
        """Static scanners flag hardcoded /Users/… — mirrors must be Path.home()-relative."""
        src = (SCRIPTS / "factory_kit_run.py").read_text(encoding="utf-8")
        self.assertNotIn('"/Users/', src)
        self.assertNotIn("'/Users/", src)
        mod = _load()
        with mock.patch.dict(os.environ, {"AUTOMATION_MAC_HOME": "/home/kit_mirror"}):
            for name, ns in (
                ("CPT", "cpt"),
                ("ram-park", "ram-park"),
                ("Newdrop CaaS", "newdrop"),
                ("Doc2Api", "doc2api"),
            ):
                for path in mod._home_mirror_candidates(name, ns):
                    self.assertTrue(path.startswith("/home/kit_mirror/"), path)
                    self.assertTrue(path.endswith(("CPT", "ram", "CaaS", "Doc2Api")), path)

    def test_classify_push_auth_missing(self) -> None:
        mod = _load()
        reason = mod.classify_push_failure(
            exit_code=128,
            stderr="fatal: could not read Username for 'https://github.com': No such device or address",
        )
        self.assertEqual(reason, "push_auth_missing")
        generic = mod.classify_push_failure(exit_code=1, stderr="remote rejected")
        self.assertEqual(generic, "push_failed:1")

    def test_green_lock_rejects_blocked_receipt(self) -> None:
        mod = _load()
        ok, why = mod.green_lock_eligible({"artifact_mode": "blocked_receipt"})
        self.assertFalse(ok)
        self.assertEqual(why, "blocked_receipt")
        # OVERSEER_FALSE_GREEN_LOCK_2026_09_07 — PR URL alone must not unlock.
        ok2, why2 = mod.green_lock_eligible(
            {
                "mode": "pr",
                "pr_url": "https://github.com/heyitsmeyourbudlol-lgtm/CPT/pull/1",
                "ok": True,
            }
        )
        self.assertFalse(ok2)
        self.assertEqual(why2, "pr_remote_ref_missing")
        ok3, why3 = mod.green_lock_eligible({"mode": "pr", "pr_url": "not-a-url", "ok": True})
        self.assertFalse(ok3)
        self.assertEqual(why3, "pr_url_missing")

    def test_green_lock_pr_requires_origin_ls_remote(self) -> None:
        """Eligible PR only when worktree exists and origin ls-remote hits branch."""
        import tempfile

        mod = _load()
        with tempfile.TemporaryDirectory() as tmp:
            probe = Path(tmp)
            (probe / ".git").mkdir()
            receipt = {
                "mode": "pr",
                "pr_url": "https://github.com/heyitsmeyourbudlol-lgtm/CPT/pull/1",
                "ok": True,
                "branch": "peer/kit-a-to-z",
                "worktree_path": str(probe),
            }
            with mock.patch.object(
                mod,
                "_run",
                return_value={"exit": 0, "stdout_tail": "abc123\trefs/heads/peer/kit-a-to-z\n"},
            ):
                ok, why = mod.green_lock_eligible(receipt)
            self.assertTrue(ok, why)
            self.assertEqual(why, "pr")
            with mock.patch.object(
                mod, "_run", return_value={"exit": 0, "stdout_tail": ""}
            ):
                ok_miss, why_miss = mod.green_lock_eligible(receipt)
            self.assertFalse(ok_miss)
            self.assertEqual(why_miss, "pr_remote_ref_missing")

    def test_heal_false_green_forces_red(self) -> None:
        """OVERSEER_FALSE_GREEN_LOCK_2026_09_07 — Status green + blocked receipt → force red."""
        import json
        import tempfile

        mod = _load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            notes = root / "notes"
            notes.mkdir()
            proof = notes / "FACTORY_A_TO_Z_PROOF.md"
            proof.write_text(
                "# Factory A→Z proof\n\n"
                "## Lock status\n\n"
                "| Field | Value |\n"
                "|-------|-------|\n"
                "| Status | **green** |\n"
                "| Green lock stamped | fake PR |\n",
                encoding="utf-8",
            )
            receipt = notes / "factory_a_to_z_last.json"
            receipt.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "artifact_mode": "blocked_receipt",
                        "steps": [
                            {
                                "step": "D_artifact",
                                "mode": "blocked_receipt",
                                "blocked_receipt": {
                                    "reasons": ["push_auth_missing", "gh_cli_missing"]
                                },
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            ext = notes / "EXTERNAL_PROOF.md"
            ext.write_text(
                "| # | Repo | Status | Verify | PR / merge | Date |\n"
                "|---|------|--------|--------|------------|------|\n"
                "| 1 | CPT | kit A→E **green** | ok | #1 | 2026-09-07 |\n",
                encoding="utf-8",
            )
            tasks = notes / "FACTORY_A_TO_Z_TASKS.md"
            tasks.write_text(
                "## Phase 4 — Green lock\n\n"
                "- [x] **[a-to-z:phase4] Stamp green lock** — fake\n"
                "- [x] **[a-to-z] Factory A→Z sequencing lock** — fake\n",
                encoding="utf-8",
            )
            with mock.patch.object(mod, "ROOT", root), mock.patch.object(
                mod, "PROOF_MD", proof
            ), mock.patch.object(mod, "PROOF_JSON", receipt), mock.patch.object(
                mod, "EXTERNAL_PROOF", ext
            ), mock.patch.object(mod, "TASKS_MD", tasks):
                heal = mod.heal_false_green_lock(write=True)
            self.assertTrue(heal.get("healed"), heal)
            self.assertEqual(heal.get("action"), "force_red")
            text = proof.read_text(encoding="utf-8")
            self.assertIn("**red**", text)
            self.assertIn(mod.NEEDLE_FALSE_GREEN, text)
            loaded = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(loaded.get("artifact_mode"), "blocked_receipt")
            self.assertIn("push_auth_missing", ext.read_text(encoding="utf-8"))
            self.assertIn("- [ ] **[a-to-z:phase4]", tasks.read_text(encoding="utf-8"))

    def test_dry_run_skips_live_receipt_write(self) -> None:
        """Dry-run must not clobber notes/factory_a_to_z_last.json."""
        import tempfile

        mod = _load()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text('{"sentinel": true}\n', encoding="utf-8")
            with mock.patch.object(mod, "PROOF_JSON", path):
                report = {"ok": True, "dry_run": True}
                mod._commit_receipt(report, dry_run=True)
            self.assertEqual(path.read_text(encoding="utf-8"), '{"sentinel": true}\n')
            self.assertEqual(report.get("receipt_skipped"), "dry_run")

    def test_commit_receipt_live_writes_once(self) -> None:
        """Live path must call write_receipt — not recurse on _commit_receipt."""
        import json
        import tempfile

        mod = _load()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            with mock.patch.object(mod, "PROOF_JSON", path):
                report = {"ok": True, "artifact_mode": "blocked_receipt", "needle": "t"}
                mod._commit_receipt(report, dry_run=False)
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded.get("artifact_mode"), "blocked_receipt")
            self.assertNotIn("receipt_skipped", report)


if __name__ == "__main__":
    unittest.main()
