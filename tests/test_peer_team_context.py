#!/usr/bin/env python3
from __future__ import annotations
import sys, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import peer_team_context as tc
class TestPeerTeamContext(unittest.TestCase):
    def test_shared_reads_include_canon_docs(self):
        paths = tc.shared_read_paths()
        self.assertIn("notes/TEAM_CONTEXT.md", paths)
    def test_build_includes_agent_layers(self):
        b = tc.build_team_context()
        self.assertIn("learning", b.sections)
    def test_niche_block_includes_thinking(self):
        self.assertIn("Critical thinking", tc.format_niche_learning_block(role_id="verify_runner"))
    def test_build_and_write(self):
        self.assertTrue(tc.write_team_context(force=True).is_file())
    def test_format_prompt_block(self):
        tc.write_team_context(force=True)
        self.assertIn("Team context", tc.format_prompt_block(max_chars=2000))
    def test_write_team_context_ttl_skips_fresh(self):
        path = tc.write_team_context(force=True); path.touch(); m=path.stat().st_mtime
        with mock.patch.object(tc, "build_team_context") as build:
            out = tc.write_team_context()
        build.assert_not_called(); self.assertEqual(out, path); self.assertEqual(path.stat().st_mtime, m)
    def test_write_team_context_force_rebuilds(self):
        tc.write_team_context(force=True)
        with mock.patch.object(tc, "build_team_context", wraps=tc.build_team_context) as build:
            tc.write_team_context(force=True)
        build.assert_called_once()
if __name__ == "__main__":
    unittest.main()
