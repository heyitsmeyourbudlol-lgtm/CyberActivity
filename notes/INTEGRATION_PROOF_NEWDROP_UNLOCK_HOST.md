# Integration proof — Newdrop unlock host-bind (#51) + hotfix

- **When:** 2026-09-08T03:06Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #33/#34 → through #41)
- **PRs:**
  - [#40](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/40) MERGED `c7fa8b7` — Bind unlock cookie HMAC to request host (#51)
  - [#41](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/41) MERGED `2bf2334` — Restore CHANGELOG + fix unlock verify test args
- **Also closed this wave:** [#37](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/37) founding count fail-closed · [#39](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/39) refund-abuse ban waits for Stripe cancel
- **Verify (main `@2bf2334`):**
  - `npm test` — **386 passed** / 69 files · EXIT 0
  - `npm run check:controls` — **23 ok · 0 fail** · EXIT 0
- **UI untouched** · NO PAY
- **Next:** Active after #41
