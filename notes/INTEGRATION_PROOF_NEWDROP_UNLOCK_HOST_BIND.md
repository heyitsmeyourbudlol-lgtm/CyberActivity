# Integration proof — Newdrop unlock cookie host-bind (#40/#41)

- **When:** 2026-09-08T03:05Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #39 → #40/#41)
- **Branch:** `peer/factory-unlock-cookie-host-bind` (+ hotfix `peer/factory-unlock-host-bind-hotfix`)
- **PR:** [#40](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/40) **MERGED** `c7fa8b7` · hotfix [#41](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/41) **MERGED** `2bf2334`
- **Needle:** HMAC `slug|host|exp` · `normalizeUnlockHost` · `unlockHostFromRequest` · HARD_FIXES #51
- **Diff scope (UI untouched):**
  - `src/lib/security/changelog-unlock-cookie.ts` (+ public-read + adversarial tests)
  - public API / RSS / unlock-actions call sites
  - `CHANGELOG.md` · `scripts/check-compliance-controls.sh` · `AGENT_MEMORY.md`
- **Verify (merge tip `2bf2334`):**
  - `npm test` — **386 passed** / 69 files · EXIT 0
  - `npm run check:controls` — **22–23 ok · 0 fail** · EXIT 0
- **Policy:** Password unlock cookies must not transfer across hosts.
- **Next step:** Active after #41 left open
