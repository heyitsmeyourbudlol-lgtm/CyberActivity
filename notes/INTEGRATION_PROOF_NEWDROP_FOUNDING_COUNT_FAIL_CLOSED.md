# Integration proof — Newdrop founding count fail-closed (#37)

- **When:** 2026-09-08T02:54Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #36 → #37)
- **Branch:** `peer/factory-founding-count-fail-closed`
- **PR:** [#37](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/37) **MERGED** `2724eab`
- **Product commit:** `1d4ba3e` — Fail-close founding when paying count is unknown
- **Needle:** `countPayingCustomers` → `null` · `signupOfferWhenPayingCountUnknown` · migration `0061_founding_count_fail_closed.sql`
- **Diff scope (UI untouched):**
  - `src/lib/billing/paying-count.ts` (+ tests)
  - `src/lib/billing/trial-offer.ts` (+ tests)
  - `src/lib/auth/ensure-account.ts` (+ tests)
  - `supabase/migrations/0061_founding_count_fail_closed.sql`
  - `CHANGELOG.md` · `scripts/check-compliance-controls.sh`
- **Verify (merge tip):**
  - `npm test` — **379 passed** / 69 files · EXIT 0
  - `npm run check:controls` — **18 ok · 0 fail** · EXIT 0
- **Policy:** Unknown paying count must not reopen founding (never treat as 0). Mid-phase trial instead.
- **Next step:** closed — Active after #37 left open
