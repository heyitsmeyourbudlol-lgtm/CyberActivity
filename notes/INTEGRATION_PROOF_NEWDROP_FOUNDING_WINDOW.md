# Integration proof — Newdrop founding window (#30)

- **When:** 2026-09-08T02:48Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #32 → #34)
- **Branch:** `peer/factory-founding-window-policy`
- **PR:** [#34](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/34) **MERGED** `bb49a570`
- **Product commit:** `111716b` — Close founding window for new signups at 50 paying customers (#30)
- **Needle:** `src/lib/billing/trial-offer.ts` `signupOfferForPayingCount` · `src/lib/auth/ensure-account.ts` · `supabase/migrations/0060_founding_window_handle_new_user.sql`
- **Diff scope (UI untouched):**
  - `src/lib/billing/trial-offer.ts` (+ tests)
  - `src/lib/billing/paying-count.ts` (+ tests)
  - `src/lib/auth/ensure-account.ts` (+ tests)
  - `supabase/migrations/0060_founding_window_handle_new_user.sql`
  - `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md` (#30 [x])
- **Verify (main):**
  - `npm test` — **373 passed** / 68 files · EXIT 0
  - `npm run check:controls` — **15 ok · 0 fail** · EXIT 0
- **Policy:** 0–49 paying → founding + 30d; 50–199 → 14d non-founding; 200+ → 7d. Count failures fail open to founding. Existing `founding_member` rows never flipped.
- **Next step:** closed — leave Active after #34 open
