# Integration proof — Newdrop plus-alias signup reject

- **When:** 2026-09-08T03:07Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS`
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #41 → #44)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/44
  - branch `peer/factory-reject-plus-alias`
  - product commit `2ef105f`
  - merge commit `159138534606458909386ec73745a17f863376f4` on `main`
- **Needle:** `src/lib/security/disposable-email.ts` `hasPlusAliasLocalPart` · `isLikelyValidSignupEmail`
- **Native verify:**
  - `npm test` — **389 passed** EXIT 0
  - `npm run check:controls` — **24 ok · 0 fail** EXIT 0
- **UI:** untouched · **NO PAY**
- **Residual:** Auth-provider-only signups that bypass `/api/auth/otp` / subscribe gate
