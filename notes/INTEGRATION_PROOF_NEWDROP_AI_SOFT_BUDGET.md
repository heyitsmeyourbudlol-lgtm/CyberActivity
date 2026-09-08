# Integration proof — Newdrop shared AI soft budget (#88)

- **When:** 2026-09-08T04:09Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS`
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #87 → #88)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/88
  - branch `peer/factory-ai-soft-budget-shared`
  - product commit `347709f`
  - merge commit `f425185006da8f96ac201e3c5227febefb3f8a02` on `main`
- **Needle:** `aiSpendAccountKey` / `AI_SPEND_ACCOUNT_PER_HOUR=90` shared by support chat + `aiDraftUpdateAction`
- **Hard-Fix:** #77 residual (shared soft budget after env kill #78)
- **Native verify:**
  - `npm test` — **449 passed** EXIT 0
  - `npm run check:controls` — **73 ok · 0 fail** EXIT 0
- **UI:** untouched · **NO PAY**
- **Residual:** Metered daily $ circuit beyond env kill + soft hourly counter still open
