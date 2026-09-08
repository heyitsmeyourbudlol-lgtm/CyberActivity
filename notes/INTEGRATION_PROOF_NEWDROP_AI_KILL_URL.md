# Integration proof — Newdrop AI spend kill + support URL allowlist (#64)

- **When:** 2026-09-08T03:47Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS`
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #62 → #64; Active after #51 already closed via intervening lands)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/64
  - branch `peer/factory-support-url-allowlist`
  - product commit `2a672ca`
  - merge commit `7facc2fc657fad1351b27c8e098ae33fde2e6319` on `main`
- **Needle:** `KILL_AI` / `AI_BUDGET_KILL` → `isKillSwitchOn("ai")` · `resolveAiClient` null · `env_kills.ai` · `isAllowedSupportUrl` / `stripDisallowedSupportUrls` in `sanitizeSupportReply`
- **Hard-fix:** #78 (env budget stops AI calls) · #79 (invented URLs stripped)
- **Native verify:**
  - `npm test` — **430 passed** EXIT 0
  - `npm run check:controls` — **54 ok · 0 fail** EXIT 0
- **UI:** untouched · **NO PAY**
- **Residual:** Metered daily $ circuit (beyond env kill) still open; draft-assist path shares same `resolveAiClient` kill
