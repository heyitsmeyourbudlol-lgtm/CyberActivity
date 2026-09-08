"""Tests for GLink agent comms."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import peer_agent_comms as comms  # noqa: E402


class TestPeerAgentComms(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        comms.COMMS_DIR = base / "agent-comms"
        comms.BUS_PATH = comms.COMMS_DIR / "bus.jsonl"
        comms.AGENTS_DIR = comms.COMMS_DIR / "agents"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_post_and_read_bus(self) -> None:
        comms.ensure_agent("factory_engineer")
        line = comms.post_glink(
            msg_type=comms.MSG_STAT,
            from_role="factory_engineer",
            payload={"st": "WIP", "op": "test"},
        )
        self.assertEqual(line["t"], "STAT")
        msgs = comms.read_bus(limit=5)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["f"], "factory_engineer")

    def test_targeted_message_filtered(self) -> None:
        comms.post_glink(
            msg_type=comms.MSG_REQ,
            from_role="factory_engineer",
            to_role="verify_runner",
            payload={"need": "vfy"},
        )
        all_msgs = comms.read_bus(limit=10)
        self.assertEqual(len(all_msgs), 1)
        for_role = comms.read_bus(limit=10, for_role="adapt_specialist")
        self.assertEqual(len(for_role), 0)
        for_verify = comms.read_bus(limit=10, for_role="verify_runner")
        self.assertEqual(len(for_verify), 1)

    def test_update_tasks_moves_done(self) -> None:
        comms.update_tasks("queue_steward", todo=["a", "b"], done=[])
        comms.update_tasks("queue_steward", append_done="a")
        state = comms.ensure_agent("queue_steward")
        self.assertEqual(state["tasks"]["done"], ["a"])
        self.assertEqual(state["tasks"]["todo"], ["b"])

    def test_format_prompt_block_includes_protocol(self) -> None:
        text = comms.format_prompt_block()
        self.assertIn("GLink", text)
        self.assertIn("STAT", text)
        self.assertIn("ASN", text)

    def test_assign_message_type(self) -> None:
        line = comms.post_glink(
            msg_type=comms.MSG_ASN,
            from_role="orchestrator",
            to_role="verify_runner",
            payload={"id": "asn-1", "task": "run verify", "when": "now"},
        )
        self.assertEqual(line["t"], "ASN")

    def test_rotate_bus_archives_tail(self) -> None:
        comms.ensure_agent("factory_engineer")
        lines = [
            json.dumps({"v": 1, "t": "STAT", "f": "factory_engineer", "to": "*", "ts": "2026", "p": {"n": i}})
            for i in range(12)
        ]
        comms.BUS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        archived = comms.rotate_bus_if_needed(max_lines=10, keep=5)
        self.assertEqual(archived, 7)
        kept = [ln for ln in comms.BUS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(len(kept), 5)
        archive_dir = comms.COMMS_DIR / "bus-archive"
        self.assertTrue(archive_dir.is_dir())
        self.assertTrue(list(archive_dir.glob("bus-*.jsonl")))

    def test_glink_schema_exposes_validators(self) -> None:
        schema = comms.glink_schema()
        self.assertEqual(schema["v"], 1)
        self.assertIn("cid", schema["compact"])
        self.assertEqual(schema["validators"]["payload"], "validate_glink_payload")
        self.assertIn("schema", comms.status_dict())

    def test_req_auto_cid_and_ack_requires_correlation(self) -> None:
        req = comms.validate_glink_payload("REQ", {"need": "vfy"})
        self.assertTrue(req.get("cid"))
        ack = comms.validate_glink_payload("ACK", {"cid": req["cid"], "ok": 1})
        self.assertEqual(ack["cid"], req["cid"])
        with self.assertRaises(ValueError):
            comms.validate_glink_payload("ACK", {"ok": 1})

    def test_reject_english_heavy_payload(self) -> None:
        with self.assertRaises(ValueError):
            comms.validate_glink_payload(
                "SUM",
                {
                    "txt": (
                        "We should maybe think about refactoring the entire "
                        "orchestration layer next week carefully."
                    )
                },
            )

    def test_path_hash_and_diff_ph(self) -> None:
        ph = comms.path_hash("scripts/peer_agent_comms.py")
        self.assertEqual(len(ph), 8)
        line = comms.post_glink(
            msg_type=comms.MSG_DIFF,
            from_role="communications_engineer",
            payload={"ph": [ph], "bref": "wt:peer-7"},
        )
        self.assertEqual(line["p"]["ph"], [ph])

    def test_prefer_ph_compacts_diff_done_paths(self) -> None:
        schema = comms.glink_schema()
        self.assertEqual(schema["validators"]["prefer_ph"], "_compact_paths_to_ph")
        self.assertIn("kp", schema["compact"])
        paths = ["scripts/peer_agent_comms.py", "tests/test_peer_agent_comms.py"]
        expected = [comms.path_hash(p) for p in paths]
        compact = comms.validate_glink_payload("DIFF", {"paths": paths, "cid": "ph1"})
        self.assertEqual(compact["ph"], expected)
        self.assertNotIn("paths", compact)
        keep = comms.validate_glink_payload(
            "DONE", {"ref": "t1", "paths": paths, "kp": 1}
        )
        self.assertEqual(keep["paths"], paths)
        self.assertEqual(keep.get("kp"), 1)
        both = comms.validate_glink_payload(
            "DIFF", {"paths": paths, "ph": [expected[0]], "cid": "ph2"}
        )
        self.assertEqual(both["ph"], [expected[0]])
        self.assertNotIn("paths", both)

    def test_req_need_aliases_and_mcp(self) -> None:
        schema = comms.glink_schema()
        self.assertEqual(schema["validators"]["req_need"], "_normalize_req_need")
        self.assertIn("mcp_need", schema["validators"])
        self.assertEqual(schema["caps"]["bus_prompt_limit"], comms.BUS_PROMPT_LIMIT)
        aliased = comms.validate_glink_payload("REQ", {"need": "verify"})
        self.assertEqual(aliased["need"], "vfy")
        mcp = comms.validate_glink_payload(
            "REQ", {"need": "mcp:search_docs", "args": {"q": "glink"}}
        )
        self.assertEqual(mcp["need"], "mcp:search_docs")
        self.assertEqual(mcp["mcp"], 1)
        self.assertEqual(mcp["args"]["tool"], "search_docs")
        mcp2 = comms.validate_glink_payload(
            "REQ", {"need": "mcp", "args": {"tool": "list_tools"}}
        )
        self.assertEqual(mcp2["need"], "mcp:list_tools")
        with self.assertRaises(ValueError):
            comms.validate_glink_payload("REQ", {"need": "please help verify"})
        with self.assertRaises(ValueError):
            comms.validate_glink_payload("REQ", {"need": "mcp"})

    def test_bus_prompt_line_cap_shrinks_injection(self) -> None:
        # Seed a fat payload line then confirm prompt clip.
        fat = {"st": "WIP", "op": "x", "note": "n" * 80}
        comms.post_glink(
            msg_type=comms.MSG_STAT,
            from_role="communications_engineer",
            payload=fat,
        )
        block = comms.format_bus_block(for_role="communications_engineer", limit=8, line_cap=80)
        for line in block.splitlines():
            if line.startswith("- `"):
                self.assertLessEqual(len(line), 80 + 4)  # "- `" + "`" overhead

    def test_sum_nested_shared_asn_byte_shrink(self) -> None:
        schema = comms.glink_schema()
        self.assertEqual(schema["validators"]["sum_nested"], "_normalize_sum_nested")
        self.assertIn("sh", schema["compact"])
        self.assertIn("ah", schema["compact"])
        fat = {
            "asn": (
                "Communications Engineer — GLink bus validators and efficiency "
                "hot path with numbered plan steps before edits"
            ),
            "shared": {
                "mode": "self_sufficient",
                "focus": "command_builder",
                "factory": (
                    "- Readiness: **99%** — self-sufficient peer improve heal "
                    "without babysitting dispatch clear git changed paths"
                ),
                "queue_open": 3,
            },
        }
        before = len(json.dumps(fat, separators=(",", ":")))
        compact = comms.validate_glink_payload("SUM", fat)
        after = len(json.dumps(compact, separators=(",", ":")))
        self.assertNotIn("asn", compact)
        self.assertNotIn("shared", compact)
        self.assertNotIn("factory", compact.get("sh") or {})
        self.assertEqual(compact.get("code"), "asn")
        self.assertEqual(compact.get("ah"), comms.path_hash(fat["asn"]))
        self.assertEqual(compact.get("sh"), {"m": "ss", "f": "cb", "q": 3})
        self.assertLess(after, before)
        self.assertGreaterEqual(before - after, 200)

        team = comms.validate_glink_payload(
            "SUM",
            {
                "team": {
                    "mode": "external_proof",
                    "focus": "factory",
                    "factory": "more English factory prose that must not hit the bus",
                    "queue_open": 0,
                }
            },
        )
        self.assertEqual(team.get("sh"), {"m": "ep", "f": "fac", "q": 0})
        self.assertNotIn("team", team)
        schema = comms.glink_schema()
        self.assertEqual(schema["validators"]["stat_op_aliases"], "_normalize_stat_op")
        self.assertEqual(schema["validators"]["sum_tx_alias"], "_normalize_sum_aliases")
        self.assertIn("pri", schema["validators"])
        self.assertIn("ttl", schema["validators"])
        self.assertEqual(schema["materialize"]["role_board"], "materialize_role_board")
        self.assertEqual(schema["materialize"]["open_reqs_mcp"], "materialize_open_reqs_mcp")

        aliased = comms.validate_glink_payload(
            "STAT", {"st": "WIP", "op": "hand_out", "pri": 2, "ttl": 60, "git": "abcdef1"}
        )
        self.assertEqual(aliased["op"], "hand")
        self.assertEqual(aliased["pri"], 2)
        self.assertEqual(aliased["ttl"], 60)
        self.assertEqual(aliased["git"], "abcdef1")
        with self.assertRaises(ValueError):
            comms.validate_glink_payload("STAT", {"st": "WIP", "op": "too_long_op"})
        with self.assertRaises(ValueError):
            comms.validate_glink_payload("STAT", {"st": "WIP", "op": "x", "pri": 99})

        sum_p = comms.validate_glink_payload("SUM", {"tx": "mat"})
        self.assertEqual(sum_p["code"], "mat")
        self.assertNotIn("tx", sum_p)

        with self.assertRaises(ValueError):
            comms.validate_glink_payload("ASN", {"task": "only"})

        req = comms.post_glink(
            msg_type=comms.MSG_REQ,
            from_role="communications_engineer",
            to_role="verify_runner",
            payload={"need": "mcp:search_docs", "pri": 1},
        )
        cid = req["p"]["cid"]
        open_rows = comms.materialize_open_reqs_mcp()
        self.assertTrue(any(r.get("cid") == cid for r in open_rows))
        comms.post_glink(
            msg_type=comms.MSG_ACK,
            from_role="verify_runner",
            payload={"cid": cid, "ok": 1},
        )
        self.assertFalse(any(r.get("cid") == cid for r in comms.materialize_open_reqs_mcp()))

        comms.post_glink(
            msg_type=comms.MSG_STAT,
            from_role="communications_engineer",
            payload={"st": "WIP", "op": "schema", "pri": 3},
        )
        board = comms.materialize_role_board()
        self.assertEqual(board["communications_engineer"]["op"], "schema")
        self.assertEqual(board["communications_engineer"]["pri"], 3)

        with self.assertRaises(ValueError):
            comms.post_glink(
                msg_type=comms.MSG_REQ,
                from_role="communications_engineer",
                to_role="communications_engineer",
                payload={"need": "vfy"},
            )

    def test_build_diff_done_payload_byte_shrink_and_bref(self) -> None:
        schema = comms.glink_schema()
        self.assertEqual(schema["validators"]["ph_bref"], "_normalize_ph_bref")
        self.assertEqual(schema["validators"]["build_diff"], "build_diff_payload")
        self.assertEqual(schema["validators"]["build_done"], "build_done_payload")
        paths = [
            "scripts/peer_agent_comms.py",
            "scripts/automation_comms_improve.py",
            "tests/test_peer_agent_comms.py",
            "notes/WORK_QUEUE.md",
            "scripts/self_improve_context.md",
        ]
        fat = {"paths": paths}
        before = len(json.dumps(fat, separators=(",", ":")))
        compact = comms.build_diff_payload(paths, bref="wt:peer-7", cid="cid-wave19")
        after = len(json.dumps(compact, separators=(",", ":")))
        self.assertNotIn("paths", compact)
        self.assertEqual(len(compact["ph"]), 5)
        self.assertEqual(compact["bref"], "wt:peer-7")
        self.assertEqual(compact["cid"], "cid-wave19")
        self.assertLess(after, before)
        self.assertGreaterEqual(before - after, 40)

        done = comms.build_done_payload(
            "glink-cid-ph",
            paths=paths[:2],
            bref="blob:abc",
            cid="cid-wave19",
        )
        self.assertEqual(done["ref"], "glink-cid-ph")
        self.assertNotIn("paths", done)
        self.assertEqual(len(done["ph"]), 2)

        with self.assertRaises(ValueError):
            comms.build_diff_payload(bref="please see the attached binary artifact carefully")
        with self.assertRaises(ValueError):
            comms.validate_glink_payload("DIFF", {"ph": ["not-a-hex-path"]})
        with self.assertRaises(ValueError):
            comms.build_done_payload("")

    def test_a2a_task_card_from_req_ack_asn(self) -> None:
        schema = comms.glink_schema()
        self.assertEqual(schema["validators"]["a2a_card"], "validate_a2a_task_card")
        self.assertEqual(schema["validators"]["a2a_from_glink"], "a2a_task_card_from_glink")
        self.assertEqual(schema["materialize"]["a2a_open"], "materialize_a2a_open_cards")
        self.assertEqual(schema["a2a"]["from_types"], ["REQ", "ACK", "ASN"])
        self.assertEqual(schema["v"], 1)

        built = comms.build_a2a_task_card(
            id="c1",
            from_role="factory_engineer",
            to_role="verify_runner",
            task="vfy",
            cid="c1",
            eta=120,
            st="req",
        )
        self.assertEqual(built["cid"], "c1")
        self.assertEqual(built["eta"], 120)

        with self.assertRaises(ValueError):
            comms.validate_a2a_task_card({"id": "x", "from": "a", "to": "b", "task": ""})

        req_line = {
            "t": "REQ",
            "f": "factory_engineer",
            "to": "verify_runner",
            "p": {"need": "vfy", "cid": "req-cid-01", "ttl": 60},
        }
        req_card = comms.a2a_task_card_from_glink(req_line)
        self.assertEqual(req_card["id"], "req-cid-01")
        self.assertEqual(req_card["from"], "factory_engineer")
        self.assertEqual(req_card["to"], "verify_runner")
        self.assertEqual(req_card["task"], "vfy")
        self.assertEqual(req_card["cid"], "req-cid-01")
        self.assertEqual(req_card["st"], "req")
        self.assertEqual(req_card["eta"], 60)

        ack_card = comms.a2a_task_card_from_glink(
            {
                "t": "ACK",
                "f": "verify_runner",
                "to": "factory_engineer",
                "p": {"cid": "req-cid-01", "ok": 1},
            }
        )
        self.assertEqual(ack_card["st"], "ack")
        self.assertEqual(ack_card["task"], "ack")
        self.assertEqual(ack_card["cid"], "req-cid-01")
        self.assertEqual(ack_card["ok"], 1)

        asn_card = comms.a2a_task_card_from_glink(
            {
                "t": "ASN",
                "f": "orchestrator",
                "to": "factory_engineer",
                "p": {"id": "asn-9", "task": "land a2a helper", "eta_sec": 300},
            }
        )
        self.assertEqual(asn_card["id"], "asn-9")
        self.assertEqual(asn_card["cid"], "asn-9")
        self.assertEqual(asn_card["task"], "land a2a helper")
        self.assertEqual(asn_card["eta"], 300)
        self.assertEqual(asn_card["st"], "asn")

        with self.assertRaises(ValueError):
            comms.a2a_task_card_from_glink({"t": "STAT", "f": "x", "to": "*", "p": {"st": "WIP"}})

        # Live bus: open REQ → A2A card; ACK removes it.
        posted = comms.post_glink(
            msg_type=comms.MSG_REQ,
            from_role="factory_engineer",
            to_role="verify_runner",
            payload={"need": "heal"},
        )
        cid = posted["p"]["cid"]
        open_cards = comms.materialize_a2a_open_cards()
        self.assertTrue(any(c.get("cid") == cid and c.get("task") == "heal" for c in open_cards))
        comms.post_glink(
            msg_type=comms.MSG_ACK,
            from_role="verify_runner",
            payload={"cid": cid, "ok": 1},
        )
        self.assertFalse(any(c.get("cid") == cid for c in comms.materialize_a2a_open_cards()))


    def test_vault_prompt_omits_state_path(self) -> None:
        """Hot-path vaults drop per-role state.json paths (protocol doc has root)."""
        schema = comms.glink_schema()
        self.assertTrue(schema["caps"].get("vault_omit_state_path"))
        for role in ("factory_engineer", "communications_engineer", "verify_runner"):
            comms.ensure_agent(role)
            st = comms.ensure_agent(role)
            st["summary"] = "WIP"
            comms._write_json(comms.agent_state_path(role), st)
        # Reconstruct legacy bloat to measure savings.
        legacy_extra = 0
        for role in ("factory_engineer", "communications_engineer", "verify_runner"):
            legacy_extra += len(f"- state: `{comms._try_rel(comms.agent_state_path(role))}`\n")
        block = comms.format_team_vaults(limit_roles=8)
        self.assertNotIn("- state:", block)
        self.assertNotIn("state.json", block)
        self.assertIn("### Vault `factory_engineer`", block)
        self.assertIn("- todo:", block)
        # Empty-bus tip is basename-only (protocol doc has full bus path).
        empty = comms.format_bus_block(for_role="communications_engineer")
        self.assertIn("`bus.jsonl`", empty)
        self.assertNotIn(str(comms.COMMS_DIR), empty)
        self.assertGreaterEqual(legacy_extra, 120)


if __name__ == "__main__":
    unittest.main()
