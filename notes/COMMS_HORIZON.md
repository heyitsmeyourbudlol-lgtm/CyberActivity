# Comms horizon — agent communication efficiency

_Updated 2026-09-07 22:29:59 · cycle 404_ · comms improve forever

**North star:** Minimum tokens + maximum signal between 8 niches: structured GLink bus, per-agent vaults, targeted REQ/ACK — never English standups on the hot path.

## Live

| Signal | Value |
|--------|-------|
| Self-test | **RED** — enqueue blocked (FAIL: test_vault_prompt_omits_state_path (tests.test_peer_agent_comms.TestPeerAgentComms.test_vault_prompt_omits_state_path); AssertionError: None is not true) |
| GLink | enabled=True · bus=361 msgs |
| Research | gaps 2 · partial 3 |
| Queue | launch · 12 open |

## NOW — efficiency first

1. **[better]** [comms] Structured file bus (GLink) vs English
   - Extend GLink schema: binary refs, path hashes, REQ/ACK correlation ids. — ~10–50× fewer tokens than prose status updates when agents use STAT/DIFF codes.
   - priority `12`
2. **[better]** [comms] MCP / tool protocol for structured calls
   - GLink REQ types that map to MCP tool invocations where available. — Schema-bound args beat free-text handoffs for verify/adapt triggers.
   - priority `25`
3. **[efficiency]** [comms] GibberLink / GGWave (audio A2A)
   - Document when to use GLink (disk) vs MCP (RPC) vs GGWave (voice) — no audio in peer_loop. — GGWave wins on phone calls; JSONL bus wins on Cursor text peers.
   - priority `40`
4. **[efficiency]** [comms] Compact encodings (msgpack / CBOR / columnar)
   - Optional msgpack line mode for bus.jsonl when message rate > threshold. — Smaller disk + parse cost at scale; JSONL fine until ~1k msgs/day.
   - priority `45`

## Research map

See `notes/COMMS_TRENDS.md` · refresh: `python3 scripts/automation_comms_research.py --refresh --write`

## Commands

```bash
./scripts/peer comms-improve-status
./scripts/peer comms
./scripts/peer comms-bus
curl http://127.0.0.1:8765/api/comms
```

