# Peer work assignment — ETA + deadline

_Updated 2026-09-08 00:12:18_ · assign across niches · respect cursor-agent timeout

**Peer work assignment** — delegate across niches to ship faster:

Agents may **assign each other** scoped work when parallel product speed beats solo hero work.
Every assignment must include **ETA + deadline check** against the **cursor-agent session limit**.

| Field | Meaning |
|-------|---------|
| **task** | Executable scope (file paths + outcome) |
| **eta_sec** | Estimated seconds for assignee to finish |
| **due** | Hard deadline (ISO) — min(your target, cursor-agent timeout) |
| **when** | `now` = take this cycle · `later` = next slot before due · `miss` = escalate BLOCK |
| **slack_sec** | due − (now + eta) — negative means won't meet deadline |

**Assign workflow:**

```
1. Estimate: ./scripts/peer eta --task "..." --role verify_runner [--deadline ISO]
2. If when=now|later → assign: ./scripts/peer assign --from YOU --to ROLE --task "..."
3. Assignee reads vault todo + GLink ASN; posts ACK then DONE
4. If when=miss → split scope, reassign, or post GLink BLOCK — do not pretend on-time
```

## Session limit

- cursor-agent timeout: **120** minutes

## Open assignments

- No open peer assignments.

## Niche guidance

### Factory Engineer
- Assign verify_runner for test-only runs; adapt_specialist for profile drift.

### Orchestrator
- Assign disjoint file scopes — never two peers same path.
- Run `./scripts/peer eta` per peer before dispatch; skip when=miss.

### Queue Steward
- Assign sync pairs to self; escalate drift to orchestrator with ETA.

### Verify Runner
- Accept run-only assignments; assign factory_engineer for code fixes.
