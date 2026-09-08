# QA smoke — scrub_last_cycle_poison keeps cycle_history notes

_Date: 2026-09-04 · role: qa_engineer · cycle Active AC_

## Strategy (hallucination guard)

```
Assumption: I will hallucinate unless grounded.
Evidence:   hub scripts/peer_transcript.py:302-332 scrub; :872-914 history append;
            tests/test_transcript.py:348-371 mocks scrub away
Hypothesis: scrub mutates only last_cycle; cycle_history notes stay intact at runtime;
            AC still open because dedicated unittest + land-proof needle are missing
Falsifier:  scrub call drops/empties cycle_history[].note or strips continue_on_dirty
Verify:     python probe A/B/C/E + unittest tests.test_transcript -q
Defy:       memory-recall + output-compare + diagnose
```

## Numbered smoke plan

| # | Action | Path | Expected | Verify |
|---|--------|------|----------|--------|
| 1 | Fixture-pop scrub with history notes | `peer_transcript.scrub_last_cycle_poison` | pops `last_cycle`; history notes unchanged | probe A |
| 2 | Deferred sanitize scrub | same | sanitizes lc; history notes unchanged | probe B |
| 3 | Module scrub parity | `peer_last_cycle_poison.scrub_last_cycle_poison` | same as 1 | probe C |
| 4 | record_cycle_outcome + real scrub | `record_cycle_outcome` | old+new history notes keep `continue_on_dirty` | probe E |
| 5 | Unittest AC coverage | `tests/test_transcript.py` | dedicated test calls real scrub + asserts history notes | FAIL — missing |

## Results (expected vs actual)

| Probe | Expected | Actual | Verdict |
|-------|----------|--------|---------|
| A fixture-pop | history notes intact | `['prior delivery; continue_on_dirty …', 'other']` | PASS |
| B sanitize | history intact + lc verify_ok=False | hist intact; lc sanitized | PASS |
| C module | history intact | PASS | PASS |
| E record+scrub | old+new frags | both notes keep fragment | PASS |
| Unittest AC | test without mocking scrub | PreserveContinueOnDirtyNoteTests mocks scrub→None; no AC phrase | **FAIL** |
| Hub `test-quick` | green | 243 OK | PASS (does not cover AC) |

## Verdict

- **Runtime:** PASS — scrub does not touch `cycle_history` notes.
- **Acceptance (queue AC):** FAIL closed — unittest + OVERSEER land-proof needle for this AC not present; Active item correctly remains open.
- **ASN:** assigned `factory_engineer` for unittest (do not mock scrub) — `asn-1788578496-factory_`.
- **Side finding:** loose land-proof token match falsely matched ASN text containing "Add unittest: scrub…" to T0 executable lane (`_land_proof_present` True) — do not use that phrasing in ASN; full WQ line is safe (`_land_proof_present` False).

## peer-5 worktree note

Lean `./scripts/peer` has no plan-gate; required unittest list references missing modules (`test_peer_worktree`, `test_peer_pen_test`, `test_peer_self_heal`). Hub smoke is authoritative for this AC.
