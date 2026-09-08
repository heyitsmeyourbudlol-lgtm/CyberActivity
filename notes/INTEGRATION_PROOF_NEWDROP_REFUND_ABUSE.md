# Integration proof — Newdrop refund-abuse window lockstep (#33)

- **When:** 2026-09-08T02:53Z (Mac hub)
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #32)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS` · worktree `.worktrees/peer-refund-abuse-window`
- **Branch:** `peer/factory-refund-abuse-window`
- **Irreversible artifacts:**
  - Product PR [#36](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/36) merge `c52ea4c`
  - Docs follow-up [#38](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/38) merge `cde8381`
  - Product commit `e27e735` — Lock refund-abuse window defaults to SQL (#33)
- **Needle:** `REFUND_ABUSE_WINDOW_DAYS_DEFAULT=180` · `resolveRefundAbuseWindowDays` · SQL `0015` `p_window_days integer default 180`
- **Native verify (worktree):**
  - `npm test` — **377 passed** EXIT 0
  - `npm run check:controls` — **17 ok · 0 fail** EXIT 0
- **Scope:** billing/ops only — shared TS defaults + webhook resolvers + migration comment lockstep + unit tests; **UI untouched** · NO PAY
- **Next step:** leave Active after #38 open
