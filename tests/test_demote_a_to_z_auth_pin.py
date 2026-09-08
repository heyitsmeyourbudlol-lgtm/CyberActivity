"""OVERSEER_DEMOTE_A_TO_Z_AUTH_PIN_2026_09_07 — red sequencing-lock Active demotes."""

from __future__ import annotations

import unittest

from project_automation import (
    demote_human_auth_blocked_active,
    is_human_auth_blocked_item,
)


class DemoteAToZAuthPinTests(unittest.TestCase):
    def test_sequencing_lock_red_is_human_auth_blocked(self) -> None:
        item = (
            "[a-to-z] Factory A→Z sequencing lock — red until real PR/merge_note; "
            "do not jump ladder — OVERSEER_NO_JUMP_UNTIL_A_TO_Z_2026_09_07"
        )
        self.assertTrue(is_human_auth_blocked_item(item))

    def test_unrelated_a_to_z_not_blocked(self) -> None:
        item = "[a-to-z:phase3] Second registry target A→E — Doc2Api on CLEAN"
        self.assertFalse(is_human_auth_blocked_item(item))

    def test_demote_moves_active_to_creative(self) -> None:
        work = (
            "## Active\n"
            "- [ ] **[a-to-z] Factory A→Z sequencing lock** — red until real PR/merge_note; "
            "do not jump ladder — OVERSEER_NO_JUMP_UNTIL_A_TO_Z_2026_09_07\n"
            "\n"
            "## Creative backlog\n"
            "- [ ] **[a-to-z:phase4] Stamp green lock** — blocked: push_auth_missing "
            "on CLEAN (no SSH/gh) — demoted human-auth block · "
            "OVERSEER_DEMOTE_HUMAN_AUTH_BLOCK_2026_09_07\n"
        )
        ctx = work
        new_w, new_c, n = demote_human_auth_blocked_active(work, ctx)
        self.assertGreaterEqual(n, 1)
        self.assertNotIn("- [ ] **[a-to-z] Factory A→Z sequencing lock**", new_w.split("## Creative")[0])
        self.assertIn("sequencing lock", new_w.lower())
        self.assertIn("OVERSEER_DEMOTE_HUMAN_AUTH_BLOCK_2026_09_07", new_w)
        # Creative section holds the demoted open line
        cre = new_w.split("## Creative backlog", 1)[1]
        self.assertIn("- [ ] **[a-to-z] Factory A→Z sequencing lock**", cre)
        self.assertIn("sequencing lock", new_c.lower())


if __name__ == "__main__":
    unittest.main()
